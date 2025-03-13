"""
Memory module for CLIche.

This module provides memory capabilities for CLIche, allowing it to remember information
across sessions and interactions.

Made with ❤️ by Pink Pixel
"""
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Import configuration classes
from .config import MemoryConfig, BaseEmbeddingConfig, VectorStoreConfig

# Import factory classes
from .factory import EmbeddingProviderFactory, VectorStoreFactory

# Import memory manager
from .manager import MemoryManager

# Log information about the memory system
logger.info("CLIche memory system initialized")
logger.info("Memory commands will be available in future releases")

# Define what's available when importing from this module
__all__ = [
    'MemoryConfig',
    'BaseEmbeddingConfig',
    'VectorStoreConfig',
    'EmbeddingProviderFactory',
    'VectorStoreFactory',
    'MemoryManager',
] 