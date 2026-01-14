"""
k3color creates colored text on terminal.
"""

from .color import Str
from .color import blue
from .color import cyan
from .color import danger
from .color import dark
from .color import fading_color
from .color import green
from .color import loaded
from .color import normal
from .color import optimal
from .color import percentage
from .color import purple
from .color import red
from .color import warn
from .color import white
from .color import yellow

from .color import darkblue
from .color import darkcyan
from .color import darkgreen
from .color import darkyellow
from .color import darkred
from .color import darkpurple
from .color import darkwhite

from importlib.metadata import version

__version__ = version("k3color")

__all__ = [
    "Str",
    "blue",
    "cyan",
    "danger",
    "dark",
    "fading_color",
    "green",
    "loaded",
    "normal",
    "optimal",
    "percentage",
    "purple",
    "red",
    "warn",
    "white",
    "yellow",
    "darkblue",
    "darkcyan",
    "darkgreen",
    "darkyellow",
    "darkred",
    "darkpurple",
    "darkwhite",
]
