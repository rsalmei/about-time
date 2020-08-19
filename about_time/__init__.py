# coding=utf-8
from __future__ import absolute_import, division, unicode_literals

import sys

from .core import about_time

VERSION = (3, 1, 0)

__author__ = 'Rogério Sampaio de Almeida'
__email__ = 'rsalmei@gmail.com'
__version__ = '.'.join(map(str, VERSION))

__all__ = ('__author__', '__version__', 'about_time')
if sys.version_info < (3,):  # pragma: no cover
    __all__ = [bytes(x) for x in __all__]
