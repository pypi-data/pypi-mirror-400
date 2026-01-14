"""
Public handlers API.

Keep this module lightweight: importing `media_muncher.handlers` should NOT
eagerly import all handler implementations (some depend on heavy libraries).
"""

from __future__ import annotations

from typing import Any

from . import factory

__all__ = [
    "factory",
    "ContentHandler",
    "DASHHandler",
    "HLSHandler",
    "JPEGHandler",
    "MP4Handler",
    "PNGHandler",
    "VASTHandler",
    "VMAPHandler",
    "XMLHandler",
]


def __getattr__(name: str) -> Any:
    # Lazy exports for handler classes
    if name == "ContentHandler":
        from .generic import ContentHandler

        return ContentHandler
    if name == "HLSHandler":
        from .hls import HLSHandler

        return HLSHandler
    if name == "DASHHandler":
        from .dash import DASHHandler

        return DASHHandler
    if name == "XMLHandler":
        from .xml import XMLHandler

        return XMLHandler
    if name == "VASTHandler":
        from .vast import VASTHandler

        return VASTHandler
    if name == "VMAPHandler":
        from .vmap import VMAPHandler

        return VMAPHandler
    if name == "JPEGHandler":
        from .jpeg import JPEGHandler

        return JPEGHandler
    if name == "PNGHandler":
        from .png import PNGHandler

        return PNGHandler
    if name == "MP4Handler":
        from .mp4 import MP4Handler

        return MP4Handler

    raise AttributeError(name)
