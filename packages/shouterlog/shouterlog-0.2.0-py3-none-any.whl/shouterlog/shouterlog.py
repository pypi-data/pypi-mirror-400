"""
This is an alternative logging module with extra capabilities.
It provides a method to output various types of lines and headers, with customizable message and line lengths, 
traces additional information and provides some debug capabilities based on that.
Its purpose is to be integrated into other classes that also use logger, primerally based on [`attrsx`](https://kiril-mordan.github.io/reusables/attrsx/).
"""

import logging
import inspect
from typing import List, Dict, Any
from datetime import datetime
import threading
import asyncio
import json
import os
import contextvars
import itertools
from functools import reduce
from operator import attrgetter
import dill #>=0.3.7
import attrs
import attrsx
import threading
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional

import attrs
import matplotlib.pyplot as plt

__design_choices__ = {}

_lock = threading.Lock()
_counter = itertools.count(1)

_IN_GATHER: ContextVar[bool] = ContextVar("_IN_GATHER", default=False)

_ORIG_tasks_gather = None
_ORIG_base_create_task = None


def _make_name(prefix: str) -> str:
    return f"{prefix}-{next(_counter)}"


def patch_asyncio_proc_naming(prefix: str = "Proc") -> None:
    """
    Rename ONLY tasks created by asyncio.gather(...) to Proc-{n}, if they were unnamed.

    Covers:
      - await asyncio.gather(*(coro() for ...))   -> renamed (because gather creates Tasks)
      - await asyncio.gather(*tasks)             -> can optionally rename Task-* passed in (see below)
    Does NOT rename:
      - plain `await coro()`
      - asyncio.create_task(coro()) outside gather
    """
    global _ORIG_tasks_gather, _ORIG_base_create_task

    with _lock:
        if _ORIG_tasks_gather is not None:
            return  # already patched

        import asyncio.tasks as tasks
        from asyncio.base_events import BaseEventLoop

        # 1) Patch the REAL gather implementation
        _ORIG_tasks_gather = tasks.gather

        def gather_patched(*aws, **kwargs):
            token = _IN_GATHER.set(True)
            try:
                # Optional: rename already-created Tasks passed into gather
                # (won't affect your "coro list" scenario, but helps other cases)
                for aw in aws:
                    if isinstance(aw, asyncio.Task):
                        try:
                            nm = aw.get_name()
                            if nm.startswith("Task-"):
                                aw.set_name(_make_name(prefix))
                        except Exception:
                            pass

                return _ORIG_tasks_gather(*aws, **kwargs)
            finally:
                _IN_GATHER.reset(token)

        tasks.gather = gather_patched  # type: ignore[assignment]
        asyncio.gather = tasks.gather  # keep alias in sync

        # 2) Patch BaseEventLoop.create_task (where gather creates Tasks from coroutines)
        _ORIG_base_create_task = BaseEventLoop.create_task

        def base_create_task_patched(self, coro, *, name=None, context=None):
            # Only name tasks created while gather is building its task set
            if name is None and _IN_GATHER.get():
                name = _make_name(prefix)

            # 3.11+ supports context=; 3.10 may raise TypeError for it
            try:
                return _ORIG_base_create_task(self, coro, name=name, context=context)
            except TypeError:
                return _ORIG_base_create_task(self, coro, name=name)

        BaseEventLoop.create_task = base_create_task_patched  # type: ignore[assignment]


def unpatch_asyncio_proc_naming() -> None:
    global _ORIG_tasks_gather, _ORIG_base_create_task

    with _lock:
        if _ORIG_tasks_gather is None:
            return

        import asyncio.tasks as tasks
        from asyncio.base_events import BaseEventLoop

        tasks.gather = _ORIG_tasks_gather  # type: ignore[assignment]
        asyncio.gather = tasks.gather  # type: ignore[assignment]

        BaseEventLoop.create_task = _ORIG_base_create_task  # type: ignore[assignment]

        _ORIG_tasks_gather = None
        _ORIG_base_create_task = None

@attrsx.define(slots=True)
class LogPlotter:

    # labels
    label_mode: str = "method"  # "method" | "full" | "none"

    # show/hide
    show_leaf_only_events: bool = True   # show events that don't cause inter-class movement
    show_self_calls: bool = True
    show_intra_class_proc_path: bool = True 
    show_record_label: bool = True
    show_idx: bool = True
    show_right_labels: bool = True
    show_only_leaf_fn_in_proc_path: bool = True
    show_count_suffix: bool = True
    
    # proc rendering / grouping
    proc_group_window_seconds: float = 0.35   # time-window for burst grouping

    # plotting defaults
    figsize: Optional[Tuple[float, float]] = None  # None => autosize
    title: str = "Sequence diagram"

    # autosize tuning knobs (used when figsize is None)
    autosize_inches_per_row: float = 0.4
    autosize_inches_per_lane: float = 2.6
    autosize_min_w: float = 10.0
    autosize_max_w: float = 28.0
    autosize_min_h: float = 6.0
    autosize_max_h: float = 30.0

    # ---------------- internal message model ----------------

    @attrs.define(frozen=True, slots=True)
    class _Msg:
        kind: str  # "call" | "event" | "proc_group"
        src: str
        dst: str
        label: str
        is_proc: bool
        invocation_key: tuple
        count: int = 1
        rec_label: str = ""
        idxs: Tuple[int, ...] = (),

    def __attrs_post_init__(self) -> None:
        self._validate(label_mode=self.label_mode)

    # ---------------- helpers ----------------

    @staticmethod
    def _validate(*, label_mode: str) -> None:
        if label_mode not in ("method", "full", "none"):
            raise ValueError("label_mode must be 'method', 'full', or 'none'")

    @staticmethod
    def _parse_ts(s: str, fmt: str) -> datetime:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            if "%f" not in fmt:
                return datetime.strptime(s, fmt + ".%f")
            raise

    @staticmethod
    def _split_fn(fn: str) -> Tuple[str, str]:
        if not fn:
            return "<unknown>", "<unknown>"
        if "." not in fn:
            return fn, fn
        cls, meth = fn.split(".", 1)
        return cls, meth

    def _chain_origin_to_leaf(self, tb_list: List[str]) -> List[Tuple[str, str]]:
        # tb format: [leaf, ..., origin]  -> we want [origin, ..., leaf]
        return [self._split_fn(x) for x in reversed(tb_list or [])]

    @staticmethod
    def _lca_prefix_len(a: List[Tuple[str, str]], b: List[Tuple[str, str]]) -> int:
        n = min(len(a), len(b))
        i = 0
        while i < n and a[i] == b[i]:
            i += 1
        return i

    @staticmethod
    def _mk_label(cls: str, meth: str, label_mode: str) -> str:
        if label_mode == "none":
            return ""
        if label_mode == "full":
            return f"{cls}.{meth}"
        return meth

    def _auto_figsize(self, n_rows: int, n_lanes: int) -> Tuple[float, float]:
        width = n_lanes * self.autosize_inches_per_lane
        height = n_rows * self.autosize_inches_per_row
        width = max(self.autosize_min_w, min(self.autosize_max_w, width))
        height = max(self.autosize_min_h, min(self.autosize_max_h, height))
        return float(width), float(height)

    @staticmethod
    def _resolve(value, default):
        return default if value is None else value

    @staticmethod
    def _format_idxs(idxs: Tuple[int, ...]) -> str:
        if not idxs:
            return ""
        xs = sorted(set(int(x) for x in idxs))
        if len(xs) == 1:
            return str(xs[0])

        # build contiguous ranges
        ranges = []
        start = prev = xs[0]
        for x in xs[1:]:
            if x == prev + 1:
                prev = x
                continue
            ranges.append((start, prev))
            start = prev = x
        ranges.append((start, prev))

        # if everything is a single contiguous block, show "a-b"
        if len(ranges) == 1:
            a, b = ranges[0]
            return f"{a}-{b}"

        # otherwise: show list for small sets, else show ranges
        if len(xs) <= 6:
            return ",".join(str(x) for x in xs)

        parts = [f"{a}-{b}" if a != b else str(a) for a, b in ranges]
        return ", ".join(parts)


    # ---------------- public API ----------------

    def plot_sequence_diagram_from_tracebacks(
        self,
        log_records: List[Dict[str, Any]],
        *,
        label_mode: Optional[str] = None,
        show_count_suffix: Optional[bool] = None,
        show_leaf_only_events: Optional[bool] = None,
        show_self_calls: Optional[bool] = None,
        show_record_label: Optional[bool] = None,
        show_right_labels: Optional[bool] = None,
        show_idx: Optional[bool] = None,
        proc_group_window_seconds: Optional[float] = None,
        show_intra_class_proc_path: Optional[bool] = None,
        show_only_leaf_fn_in_proc_path: Optional[bool] = None,
        figsize: Optional[Tuple[float, float]] = None,
        title: Optional[str] = None,
    ):
        if not log_records:
            raise ValueError("log_records is empty")

        # ---------------- resolve config ----------------

        label_mode = self._resolve(label_mode, self.label_mode)
        show_count_suffix = self._resolve(show_count_suffix, self.show_count_suffix)

        show_leaf_only_events = self._resolve(show_leaf_only_events, self.show_leaf_only_events)
        show_self_calls = self._resolve(show_self_calls, self.show_self_calls)
        show_record_label = self._resolve(show_record_label, self.show_record_label)
        show_right_labels = self._resolve(show_right_labels, self.show_right_labels)
        show_idx = self._resolve(show_idx, self.show_idx)

        proc_group_window_seconds = self._resolve(proc_group_window_seconds, self.proc_group_window_seconds)
        show_intra_class_proc_path = self._resolve(show_intra_class_proc_path, self.show_intra_class_proc_path)
        show_only_leaf_fn_in_proc_path = self._resolve(show_only_leaf_fn_in_proc_path, self.show_only_leaf_fn_in_proc_path)

        figsize = self._resolve(figsize, self.figsize)
        title = self._resolve(title, self.title)

        self._validate(label_mode=label_mode)

        # ============================================================
        # 1) NORMALIZE INPUT: sort, parse chains, build lane order
        # ============================================================

        indexed: List[Tuple[datetime, int, Dict[str, Any]]] = []
        for i, rec in enumerate(log_records):
            ts = self._parse_ts(rec["datetime"], "%Y-%m-%d %H:%M:%S") if "datetime" in rec else datetime.min
            indexed.append((ts, i, rec))
        indexed.sort(key=lambda x: (x[0], x[1]))

        lane_order: List[str] = []
        lane_seen = set()

        stream = []  # list of dicts with normalized info per record
        for ts, _, rec in indexed:
            tb_list = rec.get("traceback") or []
            chain = self._chain_origin_to_leaf(tb_list)  # [(cls,meth)] origin->leaf
            if not chain:
                continue

            is_proc = bool(rec.get("is_proc", False))
            rec_label = str(rec.get("label") or "").strip()

            idx_val = rec.get("idx", None)
            idxs = (int(idx_val),) if idx_val is not None else ()

            tb_tuple = tuple(tb_list)
            proc_name = rec.get("proc_name", None)
            call_id = rec.get("call_id", None)

            if call_id is None:
                # IMPORTANT: must be stable across all logs of the same invocation
                call_id = proc_name if is_proc else tb_tuple



            # call_id is NOT unique in your logs (it gets reused), so include tb_tuple to avoid collisions.
            invocation_key = (
                ("proc", proc_name, call_id, tb_tuple) if is_proc
                else ("non_proc", call_id, tb_tuple)
            )


            stream.append({
                "ts": ts,
                "rec": rec,
                "chain": chain,
                "is_proc": is_proc,
                "leaf_cls": chain[-1][0],
                "leaf_m": chain[-1][1],
                "rec_label": rec_label,
                "idxs": idxs,
                "tb_tuple": tb_tuple,
                "proc_name": proc_name,
                "call_id": call_id,
                "invocation_key": invocation_key,
            })

            for cls, _ in chain:
                if cls not in lane_seen:
                    lane_seen.add(cls)
                    lane_order.append(cls)

        if not lane_order:
            raise ValueError("No lanes discovered (empty tracebacks?)")

        # ============================================================
        # 2) BUILD RAW MESSAGES using active-stack + proc burst buffer
        # ============================================================

        msgs: List[LogPlotter._Msg] = []

        active_stack: List[Tuple[str, str]] = []  # origin->...->current owner
        current_owner_cls: Optional[str] = None

        # proc buffer groups repeated proc logs into bursts
        # key groups *visual arrow*, but we count invocations separately later
        proc_buf: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
        proc_key_order: List[Tuple[Any, ...]] = []

        def flush_proc_buffers():
            nonlocal proc_buf, proc_key_order
            for k in proc_key_order:
                info = proc_buf.get(k)
                if not info:
                    continue

                labels = sorted(x for x in (info.get("rec_labels") or set()) if x)
                rec_label_out = "|".join(labels)  # or ", ".join(labels)

                msgs.append(
                    LogPlotter._Msg(
                        kind="proc_group",
                        src=info["src"],
                        dst=info["dst"],
                        label=info["label"],
                        is_proc=True,
                        invocation_key=frozenset(info.get("invocations") or ()),
                        count=len(info.get("invocations") or ()),
                        rec_label=rec_label_out,  # proc groups don't carry a single record label
                        idxs=tuple(info.get("idxs") or ()),
                    )
                )
            proc_buf = {}
            proc_key_order = []

        for item in stream:
            ts = item["ts"]
            chain = item["chain"]
            is_proc = item["is_proc"]
            leaf_cls = item["leaf_cls"]
            leaf_m = item["leaf_m"]
            rec_label = item["rec_label"]
            idxs = item["idxs"]
            invocation_key = item["invocation_key"]
            tb_tuple = item["tb_tuple"]
            proc_name = item["proc_name"]

            # initialize stack
            if not active_stack:
                active_stack = chain[:1]
                current_owner_cls = active_stack[-1][0]

            # ------------------------------------------------------------
            # IMPORTANT: only NON-PROC records are allowed to mutate stack
            # ------------------------------------------------------------
            if not is_proc:
                # LCA pop
                lca = self._lca_prefix_len(active_stack, chain)
                if lca < len(active_stack):
                    if proc_buf:
                        flush_proc_buffers()
                    active_stack = active_stack[:lca]

                # push (calls) compressed by class
                pushed = chain[lca:]
                if pushed:
                    prev_cls = active_stack[-1][0] if active_stack else pushed[0][0]
                    for cls, meth in pushed:
                        if cls != prev_cls:
                            if proc_buf:
                                flush_proc_buffers()
                            msgs.append(
                                LogPlotter._Msg(
                                    kind="call",
                                    src=prev_cls,
                                    dst=cls,
                                    label=self._mk_label(cls, meth, label_mode),
                                    is_proc=False,
                                    invocation_key=invocation_key,
                                    count=1,
                                    rec_label=rec_label,
                                    idxs=idxs,
                                )
                            )
                            prev_cls = cls
                        active_stack.append((cls, meth))

                current_owner_cls = active_stack[-1][0] if active_stack else None

            # -------- proc log: add to burst buffer, don't emit normal event --------
            if is_proc and current_owner_cls:
                src_lane = current_owner_cls
                dst_lane = leaf_cls

                if show_only_leaf_fn_in_proc_path:
                    path_label = self._mk_label(leaf_cls, leaf_m, label_mode)
                else:
                    if show_intra_class_proc_path:
                        inside = [m for (c, m) in chain if c == src_lane]
                        path_label = " -> ".join(inside + [leaf_m]) if inside else self._mk_label(leaf_cls, leaf_m, label_mode)
                    else:
                        path_label = self._mk_label(leaf_cls, leaf_m, label_mode)

                visual_key = (src_lane, dst_lane, leaf_m, path_label)

                info = proc_buf.get(visual_key)
                if info is None:
                    proc_buf[visual_key] = {
                        "src": src_lane,
                        "dst": dst_lane,
                        "label": path_label,
                        "count": 1,
                        "last_ts": ts,
                        "idxs": list(idxs),
                        "invocations": {invocation_key},
                        "rec_labels": set([rec_label]) if rec_label else set(),
                    }

                    proc_key_order.append(visual_key)
                else:
                    gap = (ts - info["last_ts"]).total_seconds()
                    if gap <= proc_group_window_seconds:
                        info["count"] += 1
                        info["last_ts"] = ts
                        info["idxs"].extend(idxs)
                        info["invocations"].add(invocation_key)
                        if rec_label:
                            info["rec_labels"].add(rec_label)
                    else:
                        flush_proc_buffers()
                        proc_buf[visual_key] = {
                            "src": src_lane,
                            "dst": dst_lane,
                            "label": path_label,
                            "count": 1,
                            "last_ts": ts,
                            "idxs": list(idxs),
                            "invocations": {invocation_key},
                            "rec_labels": set([rec_label]) if rec_label else set(),
                        }

                        proc_key_order.append(visual_key)

                continue

            # non-proc record: flush proc bursts before emitting events
            if proc_buf:
                flush_proc_buffers()

            # "event" on owner lane (optional)
            if show_leaf_only_events and current_owner_cls:
                meths = [m for (c, m) in chain if c == current_owner_cls]
                lbl_m = meths[-1] if meths else leaf_m
                msgs.append(
                    LogPlotter._Msg(
                        kind="event",
                        src=current_owner_cls,
                        dst=current_owner_cls,
                        label=self._mk_label(current_owner_cls, lbl_m, label_mode),
                        is_proc=False,
                        invocation_key=invocation_key,
                        count=1,
                        rec_label=rec_label,
                        idxs=idxs,
                    )
                )

        if proc_buf:
            flush_proc_buffers()

        # ============================================================
        # 3) COLLAPSE: merge identical visuals, count invocations properly
        # ============================================================

        collapsed: List[LogPlotter._Msg] = []
        inv_sets: List[set] = []  # per collapsed item: set of invocation keys counted
        proc_inv_sets: List[set] = []  # only used for proc_group (optional)

        def same_visual(a: LogPlotter._Msg, b: LogPlotter._Msg) -> bool:
            return (
                a.kind == b.kind and
                a.src == b.src and
                a.dst == b.dst and
                a.label == b.label and
                a.is_proc == b.is_proc and
                a.rec_label == b.rec_label
            )

        for m in msgs:
            if not collapsed:
                collapsed.append(m)
                inv_sets.append({m.invocation_key})
                continue

            last = collapsed[-1]

            if same_visual(last, m):
                merged_idxs = tuple(last.idxs) + tuple(m.idxs)

                if last.kind == "proc_group":
                    merged_inv = set(last.invocation_key) | set(m.invocation_key)
                    collapsed[-1] = LogPlotter._Msg(
                        kind=last.kind,
                        src=last.src,
                        dst=last.dst,
                        label=last.label,
                        is_proc=last.is_proc,
                        invocation_key=frozenset(merged_inv),
                        count=len(merged_inv),
                        rec_label=last.rec_label,
                        idxs=merged_idxs,
                    )
                else:
                    inv_sets[-1].add(m.invocation_key)
                    new_count = len(inv_sets[-1])

                    collapsed[-1] = LogPlotter._Msg(
                        kind=last.kind,
                        src=last.src,
                        dst=last.dst,
                        label=last.label,
                        is_proc=last.is_proc,
                        invocation_key=last.invocation_key,
                        count=new_count,
                        rec_label=last.rec_label,
                        idxs=merged_idxs,
                    )

            else:
                collapsed.append(m)
                inv_sets.append({m.invocation_key})


        # ============================================================
        # 4) PLOT: unchanged logic, just uses collapsed
        # ============================================================

        if figsize is None:
            figsize = self._auto_figsize(n_rows=len(collapsed), n_lanes=len(lane_order))

        x = {c: i for i, c in enumerate(lane_order)}
        fig, ax = plt.subplots(figsize=figsize)

        y_top = 0
        y_bottom = len(collapsed) + 1

        for c in lane_order:
            xc = x[c]
            ax.plot([xc, xc], [y_top, y_bottom], linestyle="--", linewidth=1, alpha=0.35)
            ax.text(xc, y_top - 0.65, c, ha="center", va="bottom", fontsize=10)

        y = 1
        right_label_x_pad = 0.2
        for m in collapsed:
            xs, xd = x[m.src], x[m.dst]

            lbl = (m.label or "").strip()
            if show_record_label and m.rec_label and not show_right_labels:
                lbl = (lbl + f" [{m.rec_label}]").strip()

            if show_count_suffix and m.count > 1:
                lbl = (lbl + f" ×{m.count}").strip()
            if m.is_proc and lbl:
                lbl = (lbl + " (proc)").strip()

            if show_idx:
                idx_txt = self._format_idxs(m.idxs)
                if idx_txt:
                    ax.text(-0.6, y, idx_txt, fontsize=8, ha="right", va="center", alpha=0.85)
                if show_right_labels and m.rec_label:
                    # put record labels in a right-side "gutter", similar to idx on the left
                    x_right = (len(lane_order) - 0.3) + right_label_x_pad
                    ax.text(x_right, y, str(m.rec_label), fontsize=8, ha="left", va="center", alpha=0.85)

            arrowprops = dict(arrowstyle="->", linewidth=1)
            if m.is_proc:
                arrowprops["linestyle"] = "--"
                arrowprops["alpha"] = 0.75

            y_label_offset = -0.2

            if m.src == m.dst:
                if show_self_calls:
                    loop_w = 0.35
                    ax.plot(
                        [xs, xs + loop_w, xs + loop_w, xs],
                        [y, y, y + 0.25, y + 0.25],
                        linewidth=1,
                        linestyle="--" if m.is_proc else "-",
                        alpha=0.75 if m.is_proc else 1.0,
                    )
                    ax.annotate("", xy=(xs, y + 0.25), xytext=(xs + loop_w, y + 0.25), arrowprops=arrowprops)
                    if lbl:
                        ax.text(xs + loop_w + 0.05, y + y_label_offset, lbl, fontsize=9)
            else:
                ax.annotate("", xy=(xd, y), xytext=(xs, y), arrowprops=arrowprops)
                if lbl:
                    ax.text((xs + xd) / 2, y + y_label_offset, lbl, fontsize=9, ha="center")

            y += 1

        ax.set_title(title)
        
        x_left = -0.6
        x_right = (len(lane_order) - 0.3) + (right_label_x_pad if show_right_labels else 0.0) + 0.2
        ax.set_xlim(x_left, x_right)

        ax.set_ylim(y_bottom + 0.5, -1.2)
        ax.axis("off")
        plt.show()
        return fig, ax

_MISSING = object()
_LOG_ID_COUNTER = itertools.count(1)
_TRACEBACK_CTX = contextvars.ContextVar("shouter_last_traceback", default=[])
_LAST_TASK_CTX = contextvars.ContextVar("shouter_last_task_name", default=None)


__design_choices__ = {
    'logger' : ['underneath shouter is a standard logging so a lot of its capabilities were preserved',
                'custom loggers can be used within shouter, if not it will define one on its own',
                'from normal logging only the commands to log are available'],
    '_format_mess' : ['_format_mess is method where all the predefined custom formats are curretly implemented',
                      '_format_mess method triggeres _select_output_type',
                      'any parameters _select_output_type needs should be passed through class def or the method'],
    '_select_output_type' : ['the type should be selecting automatically in the future based on tracebacks'],
    'supported_classes' : ['supported classes is a required parameter if shouter is to be used within a class',
                           'supported classes is a parameter where all the classes that it visits should be listed',
                           'not listing classes would limit ability of shouter to create readable tracebacks'],
    'debbuging_capabilities' : ['issuing error, critical or fatal will optionally allow to save local variables',
                                'local variables will saved on the level of shouter statement',
                                'object that would be persisted are the ones that could be serialized',
                                'waring statement will apear for the ones that could not be save will dill'],
    'persist_state' : ['persist state happends automatically for logger lvls: error, critical/fatal',
                       'persist state can triggered manually with persist_state funtion',
                       'persist state can potentially perform two things: save tears (logs) and save os.environ',
                       'persisting tears happends in a form of json file',
                       'persisting os.environ happends in a form of dill file',
                       'persisting os.environ is optional and by defaul set to False'],
    'traceback_of_asyncio' : ['awaited functions would be different that processes spawned by asyncio and contain full traceback',
                    'to also have traceback for asyncio processes, some assumptions were made',
                    'each asyncio process is expected to be named and if spawned together should start with Proc-',
                    'last traceback would be used to augment traceback from asyncio which why it is important to log something before and after'],
    '_perform_action' : ['the method is currently does nothing but in the future could be used for user-defined actions']
}


# Metadata for package creation
__package_metadata__ = {
    "author": "Kyrylo Mordan",
    "author_email": "parachute.repo@gmail.com",
    "description": "A custom logging tool that expands normal logger with additional formatting and debug capabilities.",
    "keywords" : ['python', 'logging', 'debug tool']
}


patch_asyncio_proc_naming()

@attrsx.define(
    handler_specs = {"log_plotter" : LogPlotter},
    logger_chaining={
        'logger' : True
        }
)
class Shouter:

    """
    A class for managing and displaying formatted log messages.

    This class uses the logging module to create and manage a logger
    for displaying formatted messages. It provides a method to output
    various types of lines and headers, with customizable message and
    line lengths.
    """

    supported_classes = attrs.field(default=(), type = tuple)
    # Formatting settings
    dotline_length = attrs.field(default = 50, type = int)
    auto_output_type_selection = attrs.field(default = True, type = bool)
    show_function = attrs.field(default = True, type = bool)
    show_traceback = attrs.field(default = False, type = bool)
    show_idx = attrs.field(default = False, type = bool)
    # For saving records
    tears_persist_path = attrs.field(default='log_records.json')
    env_persist_path = attrs.field(default='environment.dill')
    datetime_format = attrs.field(default="%Y-%m-%d %H:%M:%S")
    log_records = attrs.field(factory=list, init=False)
    persist_env = attrs.field(default=False, type = bool)
    lock = attrs.field(default = None)
    last_traceback = attrs.field(factory=list)
   
    def __attrs_post_init__(self):
        self.lock = threading.Lock()
        self._reset_counter()

    __log_kwargs__ = {
        "output_type",
        "dotline_length",
        "auto_output_type_selection",
        "label",
        "save_vars"
    }

    def _reset_counter(self, start=1):
        global _LOG_ID_COUNTER
        _LOG_ID_COUNTER = itertools.count(start)

    def _format_mess(self,
                     mess : str,
                     label : str,
                     save_vars : list,
                     dotline_length : int,
                     output_type : str,
                     method : str,
                     auto_output_type_selection : bool):

        """
        Format message before it is passed to be displayed.
        """

        switch = {
            "default" : lambda : mess,
            "dline": lambda: "=" * dotline_length,
            "line": lambda: "-" * dotline_length,
            "pline": lambda: "." * dotline_length,
            "HEAD1": lambda: "".join(["\n",
                                        "=" * dotline_length,
                                        "\n",
                                        "-" * ((dotline_length - len(mess)) // 2 - 1),
                                        mess,
                                        "-" * ((dotline_length - len(mess)) // 2 - 1),
                                        " \n",
                                        "=" * dotline_length]),
            "HEAD2": lambda: "".join(["\n",
                                        "*" * ((dotline_length - len(mess)) // 2 - 1),
                                        mess,
                                        "*" * ((dotline_length - len(mess)) // 2 - 1)]),
            "HEAD3": lambda: "".join(["\n",
                                        "/" * ((dotline_length - 10 - len(mess)) // 2 - 1),
                                        mess,
                                        "\\" * ((dotline_length - 10 - len(mess)) // 2 - 1)]),
            "title": lambda: f"** {mess}",
            "subtitle": lambda: f"*** {mess}",
            "subtitle0": lambda: f"+ {mess}",
            "subtitle1": lambda: f"++ {mess}",
            "subtitle2": lambda: f"+++ {mess}",
            "subtitle3": lambda: f"++++ {mess}",
            "warning": lambda: f"!!! {mess}",
        }

        tear = self._log_traceback(mess = mess,
                            label = label,
                            method = method,
                            save_vars = save_vars)

        output_type = self._select_output_type(mess = mess,
                                            output_type = output_type,
                                            auto_output_type_selection = auto_output_type_selection)


        out_mess = ""

        if self.show_function:
            out_mess += f"{tear['function']}:"

        if self.show_traceback:
            out_mess += f"{tear['traceback'][::-1]}:"

        out_mess += switch[output_type]()

        return out_mess


    def _select_output_type(self,
                              mess : str,
                              output_type : str,
                              auto_output_type_selection : bool):

        """
        Based on message and some other information, select output_type.
        """

        # select output type automatically if condition is triggered
        if auto_output_type_selection:

            # determining traceback size of last tear
            traceback_size = len(self.log_records[-1]['traceback'])
        else:
            # otherwise set traceback_size to one
            traceback_size = 1

        if output_type is None:

            if mess is not None:

                # use traceback size to select output_type is message is available

                if traceback_size > 4:
                    return 'subtitle3'

                if traceback_size > 3:
                    return 'subtitle2'

                if traceback_size > 2:
                    return 'subtitle1'

                if traceback_size > 1:
                    return 'subtitle0'

                return 'default'

            else:

                # use traceback size to select output_type is message is not available

                if traceback_size > 2:
                    return "pline"

                if traceback_size > 1:
                    return "line"

                return "dline"

        return output_type


    def _log_traceback(self, mess: str, label : str, save_vars : list, method: str):
        """
        Active-stack semantics with explicit Proc handling.

        - Traceback order: LEAF -> ... -> ORIGIN
        - Non-proc logs define the true call chain.
        - Proc logs inherit parents because async stacks are incomplete.
        - Parents are NEVER resurrected after a non-proc step drops them.
        """

        functions = []
        lines = []

        supported_names = {
            (c if isinstance(c, type) else c.__class__).__name__
            for c in (self.supported_classes or ())
        }

        call_id = None

        # ---- collect current synchronous stack (leaf -> origin)
        for frame_info in inspect.stack():
            frame = frame_info.frame
            inst = frame.f_locals.get("self")
            if inst is None:
                continue

            cls_name = inst.__class__.__name__
            if cls_name not in supported_names:
                continue

            if call_id is None:
                call_id = id(frame)

            functions.append(f"{cls_name}.{frame.f_code.co_name}")
            lines.append(frame_info.lineno)

        # fallback if nothing matched
        if not functions:
            caller = inspect.currentframe().f_back
            call_id = id(caller)
            functions = [inspect.getframeinfo(caller).function]
            lines = [caller.f_lineno]

        # ---- asyncio / proc detection
        is_proc = False
        try:
            task = asyncio.current_task()
        except RuntimeError:
            task = None

        task_name = task.get_name() if task else None
        is_task = bool(task_name and task_name.startswith("Task-"))
        is_proc_task = bool(task_name and task_name.startswith("Proc-"))

        if is_proc_task:
            is_proc = True

        # include custom task name as pseudo-frame
        if task_name and not is_task and not is_proc_task:
            functions = functions + [task_name]

        # ---- context propagation (ContextVar-based)
        last_traceback = list(_TRACEBACK_CTX.get())

        if is_proc:
            # Proc: inherit parents (async stack is incomplete)
            if last_traceback:
                leaf = functions[0]
                parents = [f for f in last_traceback if f != leaf]
                functions = [leaf] + parents
        else:
            # Non-proc: authoritative stack, overwrite context
            pass

        # ---- dedupe, preserve order
        seen = set()
        out = []
        for f in functions:
            if f not in seen:
                out.append(f)
                seen.add(f)
        functions = out

        # update context ONLY with authoritative chain
        _TRACEBACK_CTX.set(list(functions))
        log_idx=next(_LOG_ID_COUNTER)

        env = {}
        if save_vars:
            env = self._get_local_vars(save_vars=save_vars, depth = 6)

        tear = {
            "idx" : log_idx,
            "call_id": call_id,
            "datetime": datetime.now().strftime(self.datetime_format),
            "level": method,
            "function": functions[0] if functions else [],
            "mess": mess,
            "line": lines[0] if lines else None,
            "lines": lines,
            "is_proc": is_proc,
            "proc_name" : task_name,
            "traceback": functions,
            "label" : label,
            "env" : env
        }

        self.log_records.append(tear)
        return tear

    def _persist_log_records(self):

        """
        Persists logs records into json file.
        """

        with self.lock:
            with open(self.tears_persist_path, 'a') as file:
                for tear in self.log_records:
                    tear_s = tear.copy()
                    if tear_s.get("env"):
                        tear_s["env"] = dict(self._filter_serializable(tear_s["env"], stype = "json"))
                    file.write(json.dumps(tear_s) + '\n')

    def _is_serializable(self,key,obj):

        """
        Check if object from env can be saved with dill, and if not, issue warning
        """

        try:
            dill.dumps(obj)
            return True
        except (TypeError, dill.PicklingError):
            return False

    def _is_json_serializable(self,key,obj):

        """
        Check if object from env can be saved with dill, and if not, issue warning
        """

        try:
            json.dumps({key : obj})
            return True
        except (TypeError, dill.PicklingError):
            return False


    def _filter_serializable(self,locals_dict, stype = "env"):
        """
        Filter the local variables dictionary, keeping only serializable objects.
        """
        if stype == "env":
            return {k: v for k, v in locals_dict.items() if self._is_serializable(k,v)}
        if stype == "json":
            return {k: v for k, v in locals_dict.items() if self._is_json_serializable(k,v)}


    def _get_local_vars(self, save_vars: list[str] = None, depth: int = 5):
        frame = inspect.currentframe()
        for _ in range(depth - 1):
            frame = frame.f_back

        locals_dict = frame.f_locals

        if not save_vars:
            return locals_dict

        def resolve(dotted: str):
            root, *parts = dotted.split(".")
            if root not in locals_dict:
                return _MISSING

            cur = locals_dict[root]
            for p in parts:
                try:
                    if isinstance(cur, dict):
                        cur = cur[p]
                    else:
                        cur = getattr(cur, p)
                except Exception:
                    return _MISSING
            return cur

        out = {}
        for name in save_vars:
            val = resolve(name)
            if val is not _MISSING:
                out[name] = val

        return out

    def _persist_environment(self):

        """
        Save the current environment variables using dill.
        """

        if self.persist_env:

            local_vars = self._get_local_vars()
            # filtering out local vars that cannot be saved with dill
            serializable_local_vars = dict(self._filter_serializable(local_vars))
            with self.lock:  # Ensure thread-safety if called from multiple threads
                with open(self.env_persist_path, 'wb') as file:
                    dill.dump(serializable_local_vars, file)


    def _perform_action(self,
                        method : str):

        return None

    def _log(self, 
             method, 
             mess : str = None,
             label : str = None,
             save_vars : list = None,
             dotline_length : int = None,
             output_type : str = None,
             auto_output_type_selection : bool = None,
             logger : logging.Logger = None,
             *args, **kwargs):

        if dotline_length is None:
            dotline_length = self.dotline_length

        if auto_output_type_selection is None:
            auto_output_type_selection = self.auto_output_type_selection

        if logger is None:
            logger = self.logger

        formated_mess = self._format_mess(mess = mess,
                                      label = label,
                                      dotline_length = dotline_length,
                                      output_type = output_type,
                                      method = method,
                                      save_vars = save_vars,
                                      auto_output_type_selection = auto_output_type_selection)

        if method == "info":
            logger.info(formated_mess,
                    *args, **kwargs)
        if method == "debug":
            logger.debug(formated_mess,
                    *args, **kwargs)
        if method == "warning":
            logger.warning(formated_mess,
                    *args, **kwargs)
        if method == "error":
            logger.error(formated_mess,
                    *args, **kwargs)
        if method == "fatal":
            logger.fatal(formated_mess,
                    *args, **kwargs)
        if method == "critical":
            logger.critical(formated_mess,
                    *args, **kwargs)

        if method in ["error", "fatal", "critical"]:

            self._persist_log_records()
            self._persist_environment()


    def persist_state(self,
                      tears_persist_path : str = None,
                      env_persist_path : str = None):

        """
        Function for persisting state inteded to be used to extract logs and manually save env.
        """

        # temporarily overwriting class persist paths
        if tears_persist_path is not None:
            prev_tears_persist_path = self.tears_persist_path
            self.tears_persist_path = tears_persist_path
        else:
            prev_tears_persist_path = None

        if env_persist_path is not None:
            prev_env_persist_path = self.env_persist_path
            self.env_persist_path = env_persist_path
        else:
            prev_env_persist_path = None

        # persisting state
        self._persist_log_records()
        self._persist_environment()

        # revert to predefined path for persisting after persist was complete
        if prev_tears_persist_path:
            self.tears_persist_path = prev_tears_persist_path
        if prev_env_persist_path:
            self.env_persist_path = prev_env_persist_path



    def return_logged_tears(self):

        """
        Return list of dictionaries of log records.
        """

        return self.log_records

    def return_last_words(self,
                          env_persist_path : str = None):

        """
        Return debug environment.
        """

        if env_persist_path is None:
            env_persist_path = self.env_persist_path

        with open(env_persist_path, 'rb') as file:
            debug_env = dill.load(file)

        return debug_env

    def show_sequence_diagram(self, 
                              log_records : List[Dict[str, Any]] = None, 
                              *args, **kwargs):

        if log_records is None:
            log_records = self.log_records

        if log_records:

            self._initialize_log_plotter_h()

            self.log_plotter_h.plot_sequence_diagram_from_tracebacks(
                log_records = log_records,
                *args, **kwargs
            )
        else:
            self.warning("No log records were provided!")

    def show_logs_by_id(self, ids : List[int]):

        return [i for i in self.log_records if i.get("idx", 0) in ids ]


    def info(self,
             mess : str = None,
             dotline_length : int = None,
             output_type : str = None,
             auto_output_type_selection : bool = None,
             label : str = None,
             save_vars : list = None,
             logger : logging.Logger = None,
             *args, **kwargs) -> None:

        """
        Prints info message similar to standard logger but with types of output and some additional actions.
        """

        self._log(
            method = "info",
            mess = mess,
            dotline_length = dotline_length,
            output_type = output_type,
            auto_output_type_selection = auto_output_type_selection,
            label = label,
            save_vars = save_vars,
            logger = logger,
            *args, **kwargs
        )

    def debug(self,
             mess : str = None,
             dotline_length : int = None,
             output_type : str = None,
             auto_output_type_selection : bool = None,
             label : str = None,
             save_vars : list = None,
             logger : logging.Logger = None,
             *args, **kwargs) -> None:

        """
        Prints debug message similar to standard logger but with types of output and some additional actions.
        """


        self._log(
            method = "debug",
            mess = mess,
            dotline_length = dotline_length,
            output_type = output_type,
            auto_output_type_selection = auto_output_type_selection,
            label = label,
            save_vars = save_vars,
            logger = logger,
            *args, **kwargs
        )

    def warning(self,
             mess : str = None,
             dotline_length : int = None,
             output_type : str = None,
             auto_output_type_selection : bool = None,
             label : str = None,
             save_vars : list = None,
             logger : logging.Logger = None,
             *args, **kwargs) -> None:

        """
        Prints warning message similar to standard logger but with types of output and some additional actions.
        """


        self._log(
            method = "warning",
            mess = mess,
            dotline_length = dotline_length,
            output_type = output_type,
            auto_output_type_selection = auto_output_type_selection,
            label = label,
            save_vars = save_vars,
            logger = logger,
            *args, **kwargs
        )

    def error(self,
             mess : str = None,
             dotline_length : int = None,
             output_type : str = None,
             auto_output_type_selection : bool = None,
             label : str = None,
             save_vars : list = None,
             logger : logging.Logger = None,
             *args, **kwargs) -> None:

        """
        Prints error message similar to standard logger but with types of output and some additional actions.
        """

        self._log(
            method = "error",
            mess = mess,
            dotline_length = dotline_length,
            output_type = output_type,
            auto_output_type_selection = auto_output_type_selection,
            label = label,
            save_vars = save_vars,
            logger = logger,
            *args, **kwargs
        )

    def fatal(self,
             mess : str = None,
             dotline_length : int = None,
             output_type : str = None,
             auto_output_type_selection : bool = None,
             label : str = None,
             save_vars : list = None,
             logger : logging.Logger = None,
             *args, **kwargs) -> None:

        """
        Prints fatal message similar to standard logger but with types of output and some additional actions.
        """


        self._log(
            method = "fatal",
            mess = mess,
            dotline_length = dotline_length,
            output_type = output_type,
            auto_output_type_selection = auto_output_type_selection,
            label = label,
            save_vars = save_vars,
            logger = logger,
            *args, **kwargs
        )

    def critical(self,
             mess : str = None,
             dotline_length : int = None,
             output_type : str = None,
             auto_output_type_selection : bool = None,
             label : str = None,
             save_vars : list = None,
             logger : logging.Logger = None,
             *args, **kwargs) -> None:

        """
        Prints critical message similar to standard logger but with types of output and some additional actions.
        """

        self._log(
            method = "critical",
            mess = mess,
            dotline_length = dotline_length,
            output_type = output_type,
            auto_output_type_selection = auto_output_type_selection,
            label = label,
            save_vars = save_vars,
            logger = logger,
            *args, **kwargs
        )