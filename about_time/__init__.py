from importlib import metadata

from .core import about_time
from .features import FEATURES
from .human_count import HumanCount
from .human_duration import HumanDuration
from .human_throughput import HumanThroughput

try:
    pkg_metadata = metadata.metadata('about-time')
    __version__ = pkg_metadata['Version']
    __author__ = pkg_metadata['Author-Email']
    __email__ = __author__.split('<')[1][:-1]  # simple parser for "Name <email@addr.com>".
except metadata.PackageNotFoundError:  # pragma: no cover
    # the package is not installed, so we can't get the metadata; common during development.
    __version__ = '0.0.0'
    __author__ = None
    __email__ = None

VERSION = tuple(map(int, __version__.split('.')))

__all__ = ('__author__', '__version__', 'about_time', 'HumanCount', 'HumanDuration',
           'HumanThroughput', 'FEATURES')
