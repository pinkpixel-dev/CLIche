"""
Vector stores for CLIche memory system.

This module provides vector stores for the memory system.

Made with ❤️ by Pink Pixel
"""
from .base import BaseVectorStore

__all__ = [
    "BaseVectorStore",
]

# Register stores when they're imported
try:
    from .chroma import ChromaVectorStore
    __all__.append("ChromaVectorStore")
except ImportError:
    pass
