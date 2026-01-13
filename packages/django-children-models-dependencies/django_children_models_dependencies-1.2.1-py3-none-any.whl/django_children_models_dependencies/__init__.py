"""
django-children-models-dependencies provides tools to get the dependencies in a tree of django models
"""

from importlib.metadata import version

__version__ = version("django-children-models-dependencies")
VERSION = tuple(int(part) for part in __version__.split(".") if str(part).isnumeric())
