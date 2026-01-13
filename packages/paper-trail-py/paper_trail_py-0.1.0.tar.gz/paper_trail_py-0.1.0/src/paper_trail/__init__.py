"""
PaperTrail - SQLAlchemy Model Versioning Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A modern Python library for tracking changes to SQLAlchemy models.

:copyright: (c) 2026
:license: MIT
"""

from .config import configure
from .context import get_whodunnit, set_whodunnit
from .decorators import track_versions
from .models import Version
from .query import VersionQuery
from .reify import reify_version

__version__ = "0.1.0"

__all__ = [
    "configure",
    "track_versions",
    "Version",
    "set_whodunnit",
    "get_whodunnit",
    "VersionQuery",
    "reify_version",
]
