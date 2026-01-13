from setuptools import setup

import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
path_to_readme = os.path.join(here, "README.md")

long_description = """# Shouterlog

This is an alternative logging module with extra capabilities.
It provides a method to output various types of lines and headers, with customizable message and line lengths, 
traces additional information and provides some debug capabilities based on that.
Its purpose is to be integrated into other classes that also use logger, primerally based on [`attrsx`](https://kiril-mordan.github.io/reusables/attrsx/).

"""

if os.path.exists(path_to_readme):
  with codecs.open(path_to_readme, encoding="utf-8") as fh:
      long_description += fh.read()

setup(
    name="shouterlog",
    packages=["shouterlog"],
    install_requires=['matplotlib', 'dill>=0.3.7', 'attrs', 'attrsx'],
    classifiers=['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'Intended Audience :: Science/Research', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.9', 'Programming Language :: Python :: 3.10', 'Programming Language :: Python :: 3.11', 'Programming Language :: Python :: 3.12', 'License :: OSI Approved :: MIT License', 'Topic :: Scientific/Engineering'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Kyrylo Mordan",
    author_email="parachute.repo@gmail.com",
    description="A custom logging tool that expands normal logger with additional formatting and debug capabilities.",
    keywords=['python', 'logging', 'debug tool', 'aa-paa-tool'],
    version="0.3.0",
    license = "mit",
    include_package_data = True,
    package_data = {'shouterlog': ['mkdocs/**/*', '.paa.tracking/version_logs.csv', '.paa.tracking/release_notes.md', '.paa.tracking/lsts_package_versions.yml', '.paa.tracking/notebook.ipynb', '.paa.tracking/package_mapping.json', '.paa.tracking/package_licenses.json', 'tests/**/*', '.paa.tracking/.paa.config', '.paa.tracking/python_modules/shouterlog.py', '.paa.tracking/python_modules/components/shouterlog/asyncio_patch.py', '.paa.tracking/python_modules/components/shouterlog/log_plotter.py', '.paa.tracking/.paa.version']} ,
    )
