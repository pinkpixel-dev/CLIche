"""
Memory Manager for CLIche memory system.

This module provides a high-level interface for working with memories in the CLIche memory system.

Made with ❤️ by Pink Pixel
"""
import logging
import uuid
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np

from .config import MemoryConfig, BaseEmbeddingConfig, VectorStoreConfig
from .factory import EmbeddingProviderFactory, VectorStoreFactory
from .embeddings.base import BaseEmbeddingProvider
from .vector_stores.base import BaseVectorStore


class MemoryManager:
    """
    Memory Manager for CLIche memory system.
    
    This class provides a high-level interface for working with memories in the CLIche memory system.
    It handles the creation of embedding providers and vector stores, and provides methods for
    adding, retrieving, and searching memories.
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        """
        Initialize the memory manager.
        
        Args:
            config: Configuration for the memory system. If None, default configuration will be used.
        """
        self.logger = logging.getLogger(__name__)
        
        # Use default config if none provided
        self.config = config or MemoryConfig()
        
        # Initialize embedding provider
        self.embedding_provider = None
        self.embedding_config = self.config.embedding
        
        # Initialize vector store
        self.vector_store = None
        self.vector_store_config = self.config.vector_store
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self) -> bool:
        """
        Initialize the embedding provider and vector store.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize embedding provider
            self.logger.info(f"Initializing embedding provider: {self.embedding_config.provider}")
            self.embedding_provider = EmbeddingProviderFactory.create_provider_from_config(self.embedding_config)
            
            # Initialize vector store
            self.logger.info(f"Initializing vector store: {self.vector_store_config.provider}")
            self.vector_store = VectorStoreFactory.create_store_from_config(self.vector_store_config)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize memory components: {e}")
            return False
    
    def is_ready(self) -> bool:
        """
        Check if the memory manager is ready to use.
        
        Returns:
            True if ready, False otherwise
        """
        if not self.embedding_provider:
            self.logger.warning("Embedding provider not initialized")
            return False
        
        if not self.vector_store:
            self.logger.warning("Vector store not initialized")
            return False
        
        return self.embedding_provider.is_available() and self.vector_store.is_initialized
    
    def add_memory(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Add a memory to the system.
        
        Args:
            content: Memory content
            metadata: Metadata for the memory
            memory_id: Optional ID for the memory. If None, a new ID will be generated.
            
        Returns:
            ID of the added memory, or None if failed
        """
        if not self.is_ready():
            self.logger.error("Memory system not ready")
            return None
        
        try:
            # Generate embedding
            embedding = self.embedding_provider.embed(content)
            
            if embedding is None or len(embedding) == 0:
                self.logger.error("Failed to generate embedding")
                return None
            
            # Add to vector store
            memory_id = self.vector_store.add(
                content=content,
                embedding=embedding[0],  # Use first embedding
                metadata=metadata,
                memory_id=memory_id
            )
            
            self.logger.info(f"Added memory with ID: {memory_id}")
            return memory_id
        except Exception as e:
            self.logger.error(f"Failed to add memory: {e}")
            return None
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to get
            
        Returns:
            Memory if found, None otherwise
        """
        if not self.is_ready():
            self.logger.error("Memory system not ready")
            return None
        
        try:
            memory = self.vector_store.get(memory_id)
            return memory
        except Exception as e:
            self.logger.error(f"Failed to get memory: {e}")
            return None
    
    def search_memories(
        self, 
        query: str, 
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for memories by query.
        
        Args:
            query: Query to search for
            limit: Maximum number of results to return
            filter_metadata: Metadata to filter by
            min_score: Minimum similarity score (0 to 1)
            
        Returns:
            List of memories, each with id, content, metadata, and score
        """
        if not self.is_ready():
            self.logger.error("Memory system not ready")
            return []
        
        try:
            # Generate embedding for query
            query_embedding = self.embedding_provider.embed(query)
            
            if query_embedding is None or len(query_embedding) == 0:
                self.logger.error("Failed to generate embedding for query")
                return []
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding=query_embedding[0],
                limit=limit,
                filter_metadata=filter_metadata,
                min_score=min_score
            )
            
            self.logger.info(f"Found {len(results)} memories for query: '{query}'")
            return results
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_ready():
            self.logger.error("Memory system not ready")
            return False
        
        try:
            success = self.vector_store.delete(memory_id)
            if success:
                self.logger.info(f"Deleted memory with ID: {memory_id}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete memory: {e}")
            return False
    
    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update a memory.
        
        Args:
            memory_id: ID of the memory to update
            content: New content (if None, keep existing)
            metadata: New metadata (if None, keep existing)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_ready():
            self.logger.error("Memory system not ready")
            return False
        
        try:
            # Generate new embedding if content is updated
            embedding = None
            if content is not None:
                embedding_result = self.embedding_provider.embed(content)
                if embedding_result is None or len(embedding_result) == 0:
                    self.logger.error("Failed to generate embedding for updated content")
                    return False
                embedding = embedding_result[0]
            
            # Update the memory
            success = self.vector_store.update(
                memory_id=memory_id,
                content=content,
                embedding=embedding,
                metadata=metadata
            )
            
            if success:
                self.logger.info(f"Updated memory with ID: {memory_id}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to update memory: {e}")
            return False
    
    def count_memories(self, filter_metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Count memories.
        
        Args:
            filter_metadata: Metadata to filter by
            
        Returns:
            Number of memories
        """
        if not self.is_ready():
            self.logger.error("Memory system not ready")
            return 0
        
        try:
            count = self.vector_store.count(filter_metadata)
            return count
        except Exception as e:
            self.logger.error(f"Failed to count memories: {e}")
            return 0
    
    def list_memories(
        self, 
        filter_metadata: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all memories.
        
        Args:
            filter_metadata: Metadata to filter by
            limit: Maximum number of memories to return
            
        Returns:
            List of memories
        """
        if not self.is_ready():
            self.logger.error("Memory system not ready")
            return []
        
        try:
            memories = self.vector_store.list(filter_metadata, limit)
            return memories
        except Exception as e:
            self.logger.error(f"Failed to list memories: {e}")
            return []
    
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        This method is called when the memory manager is no longer needed.
        """
        if self.embedding_provider:
            self.embedding_provider.cleanup()
        
        if self.vector_store:
            self.vector_store.cleanup()
    
    def save_config(self, path: str) -> bool:
        """
        Save the configuration to a file.
        
        Args:
            path: Path to save the configuration to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.config.save(path)
            self.logger.info(f"Saved configuration to {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    @classmethod
    def load_config(cls, path: str) -> Optional[MemoryConfig]:
        """
        Load configuration from a file.
        
        Args:
            path: Path to load the configuration from
            
        Returns:
            Loaded configuration, or None if failed
        """
        try:
            config = MemoryConfig.load(path)
            return config
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            return None
    
    @classmethod
    def from_config_file(cls, path: str) -> Optional['MemoryManager']:
        """
        Create a memory manager from a configuration file.
        
        Args:
            path: Path to the configuration file
            
        Returns:
            Memory manager, or None if failed
        """
        config = cls.load_config(path)
        if config:
            return cls(config)
        return None 