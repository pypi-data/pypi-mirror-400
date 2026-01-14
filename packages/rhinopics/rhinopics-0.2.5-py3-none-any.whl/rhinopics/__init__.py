"""Rhinopics module."""

import logging

from ._version import get_versions

# Logging configuration.
FORMAT = "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.ERROR)

__version__ = get_versions()["version"]
del get_versions

from . import _version

__version__ = _version.get_versions()["version"]
