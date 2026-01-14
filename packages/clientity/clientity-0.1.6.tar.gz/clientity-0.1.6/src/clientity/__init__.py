"""
clientity
"""
__author__ = "Joel Yisrael"
__version__ = "0.1.6"

VERSION = tuple(map(int, __version__.split('.')))

from .core import client, endpoint, resource, namespace
