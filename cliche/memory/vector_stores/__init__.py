"""
Vector stores for CLIche memory system.

This module provides vector stores for the memory system.

Made with ❤️ by Pink Pixel
"""
from .base import BaseVectorStore
from .factory import VectorStoreFactory

__all__ = [
    "BaseVectorStore",
    "VectorStoreFactory",
]

# Register stores when they're imported
try:
    from .chroma import ChromaVectorStore
    VectorStoreFactory.register_store("chroma", ChromaVectorStore)
    __all__.append("ChromaVectorStore")
except ImportError:
    pass
