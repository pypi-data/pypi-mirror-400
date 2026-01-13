"""
KmBiT Kernel - The AI Filesystem

A non-conversational routing kernel for AI agents.
Like a filesystem indexes files, KmBiT indexes capabilities.

This is not a chatbot. This is the operating system underneath.

Part of HumoticaOS - One Love, One fAmIly!
"""

__version__ = "0.1.0"

from .kernel import Kernel
from .fs import AIFileSystem, Path
from .router import Router, Route
from .index import Index

__all__ = [
    "Kernel",
    "AIFileSystem",
    "Path",
    "Router",
    "Route",
    "Index",
]
