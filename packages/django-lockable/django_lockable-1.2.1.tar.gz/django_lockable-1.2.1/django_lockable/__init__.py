"""
django-lockable provides ``Lockable``, a base django model that allow to forbid some fields to be
updated
"""

from importlib.metadata import version

__version__ = version("django-lockable")
VERSION = tuple(int(part) for part in __version__.split(".") if str(part).isnumeric())
