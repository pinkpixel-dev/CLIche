"""
Base vector store for CLIche memory system.

This module defines the abstract base class for vector stores, adapted from mem0.

Made with ❤️ by Pink Pixel
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Union
import uuid
import logging
import numpy as np

from ..config import VectorStoreConfig


class BaseVectorStore(ABC):
    """
    Abstract base class for vector stores.
    
    All vector stores must implement this interface.
    """
    
    def __init__(self, config: VectorStoreConfig):
        """
        Initialize the vector store.
        
        Args:
            config: Configuration for the vector store
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the vector store.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def create_col(self, name: str, vector_size: int = None, distance: str = "cosine"):
        """
        Create a new collection.
        
        Args:
            name: Name of the collection
            vector_size: Size of the vectors
            distance: Distance metric to use (e.g., "cosine", "euclidean")
        """
        pass
    
    @abstractmethod
    def add(
        self, 
        content: str, 
        embedding: np.ndarray, 
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """
        Add a memory to the vector store.
        
        Args:
            content: Memory content
            embedding: Embedding for the content
            metadata: Metadata for the memory
            memory_id: Optional ID for the memory. If None, a new ID will be generated.
            
        Returns:
            ID of the added memory
        """
        pass
    
    @abstractmethod
    def insert(
        self,
        vectors: List[list],
        payloads: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ):
        """
        Insert vectors into a collection.
        
        Args:
            vectors: List of vectors to insert
            payloads: List of payloads (metadata) for each vector
            ids: List of IDs for each vector
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query_embedding: np.ndarray,
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for memories by embedding.
        
        Args:
            query_embedding: Embedding to search for
            limit: Maximum number of results to return
            filter_metadata: Metadata to filter by
            min_score: Minimum similarity score (0 to 1)
            
        Returns:
            List of memories, each with id, content, metadata, and score
        """
        pass
    
    @abstractmethod
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to get
            
        Returns:
            Memory if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        embedding: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update a memory.
        
        Args:
            memory_id: ID of the memory to update
            content: New content (if None, keep existing)
            embedding: New embedding (if None, keep existing)
            metadata: New metadata (if None, keep existing)
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self, filter_metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Count memories.
        
        Args:
            filter_metadata: Metadata to filter by
            
        Returns:
            Number of memories
        """
        pass
    
    def generate_id(self) -> str:
        """
        Generate a unique ID for a memory.
        
        Returns:
            Unique ID
        """
        return str(uuid.uuid4())
    
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        This method is called when the vector store is no longer needed.
        """
        # Default implementation does nothing
        pass
    
    @abstractmethod
    def get_collection_name(self) -> str:
        """
        Get the name of the collection.
        
        Returns:
            Collection name
        """
        pass
    
    @abstractmethod
    def collection_exists(self) -> bool:
        """
        Check if the collection exists.
        
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def list_collections(self) -> List[str]:
        """
        List all collections.
        
        Returns:
            List of collection names
        """
        pass
        
    @abstractmethod
    def delete_collection(self) -> bool:
        """
        Delete the collection.
        
        Returns:
            True if successful, False otherwise
        """
        pass
        
    @abstractmethod
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Dictionary with collection information
        """
        pass
        
    @abstractmethod
    def list(self, filter_metadata: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all memories.
        
        Args:
            filter_metadata: Metadata to filter by
            limit: Maximum number of memories to return
            
        Returns:
            List of memories
        """
        pass
