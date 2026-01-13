__all__ = ['add', 'sub']

from .calculator import add, sub
from importlib.metadata import version

__version__ = version("testpythonsamplepackage")
