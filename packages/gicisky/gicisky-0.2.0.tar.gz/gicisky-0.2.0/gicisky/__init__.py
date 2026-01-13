"""
Gicisky - A Python library for interacting with Gicisky electronic ink display tags.
"""

__version__ = "0.2.0"
__author__ = "MassiveBox"
__email__ = "box@boxo.cc"

# Import all public APIs
from .ble import *
from .core import *
from .image import *
from .logger import *

# Define what gets imported with "from gicisky import *"
__all__ = []
__all__.extend(ble.__all__)
__all__.extend(core.__all__)
__all__.extend(image.__all__)
__all__.extend(logger.__all__)