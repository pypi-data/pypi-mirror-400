"""
Rivalite - A lightweight collection containing a multitude of helper functions to help you with your Python projects.

This package exposes functions like ensure_list(value) which can help your project by, for example, making sure that something is a list and that it
doesn't iterate over every letter of a string.

You can find all of the available modules by using rivalite.about().
"""

from importlib.metadata import version, PackageNotFoundError
import importlib
import inspect
from .core import about

_modules = about()

__all__ = []

for m in _modules:
    module = importlib.import_module(f".{m}", __name__)
    for name in dir(module):
        obj = getattr(module, name)
        if not name.startswith("_") and getattr(obj, "__module__", None) == module.__name__:
            globals()[name] = obj
            __all__.append(name)

try:
    __version__ = version("rivalite")
except PackageNotFoundError:
    __version__ = "0.0.0"
