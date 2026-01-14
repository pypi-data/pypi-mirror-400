"""
clacks_gnu_middleware
A FastAPI middleware to handle the GNU Headers (Memorial Headers) of the Clacks (Going Postal Terry Pratchett) for "sending people home".
"""

__version__ = "0.0.2"
__author__ = "Tobias Heimig-Elschner <Tobias@heimig.de>"
__license__ = "GPL-3.0-or-later"
__url__ = "https://gitlab.com/THE-Git/clacks-gnu-middleware/"

from .clacks_middleware import clacks_middleware, clacks_config, ClacksConfig

__all__ = ["clacks_middleware", "clacks_config", "ClacksConfig"]