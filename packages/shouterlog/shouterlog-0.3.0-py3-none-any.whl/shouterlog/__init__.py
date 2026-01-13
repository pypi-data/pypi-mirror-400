
"""
This is an alternative logging module with extra capabilities.
It provides a method to output various types of lines and headers, with customizable message and line lengths, 
traces additional information and provides some debug capabilities based on that.
Its purpose is to be integrated into other classes that also use logger, primerally based on [`attrsx`](https://kiril-mordan.github.io/reusables/attrsx/).
"""
from .shouterlog import *
__version__='0.3.0'