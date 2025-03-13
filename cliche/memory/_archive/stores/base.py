"""
Base Vector Store Interface for CLIche Memory

Defines the interface for vector store implementations.

Made with ❤️ by Pink Pixel
"""
import abc
from typing import Any, Dict, List, Optional, Tuple, Union


class VectorStoreBase(abc.ABC):
    """Base class for vector store implementations"""
    
    @abc.abstractmethod
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the vector store
        
        Args:
            config: Configuration for the vector store
        """
        pass
    
    @abc.abstractmethod
    def add(
        self,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """
        Add a memory to the vector store
        
        Args:
            content: Content of the memory
            embedding: Embedding vector for the memory
            metadata: Metadata for the memory
            memory_id: ID for the memory (if None, a new ID will be generated)
            
        Returns:
            ID of the added memory
        """
        pass
    
    @abc.abstractmethod
    def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for memories similar to the query embedding
        
        Args:
            query_embedding: Embedding vector for the query
            limit: Maximum number of results to return
            filters: Filters to apply to the search
            
        Returns:
            List of memories, each with ID, content, metadata, and similarity score
        """
        pass
    
    @abc.abstractmethod
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by ID
        
        Args:
            memory_id: ID of the memory to get
            
        Returns:
            Memory if found, None otherwise
        """
        pass
    
    @abc.abstractmethod
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a memory in the vector store
        
        Args:
            memory_id: ID of the memory to update
            content: New content for the memory (if None, content is not updated)
            embedding: New embedding for the memory (if None, embedding is not updated)
            metadata: New metadata for the memory (if None, metadata is not updated)
            
        Returns:
            True if the memory was updated, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory from the vector store
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if the memory was deleted, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def clear(self) -> bool:
        """
        Clear all memories from the vector store
        
        Returns:
            True if the vector store was cleared, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count memories in the vector store
        
        Args:
            filters: Filters to apply to the count
            
        Returns:
            Number of memories matching the filters
        """
        pass


class VectorStoreFactory:
    """Factory for creating vector store instances"""
    
    @staticmethod
    def create(provider_type: str, config: Dict[str, Any]) -> VectorStoreBase:
        """
        Create a vector store instance
        
        Args:
            provider_type: Type of vector store to create
            config: Configuration for the vector store
            
        Returns:
            Instance of the requested vector store
            
        Raises:
            ValueError: If the provider type is not supported
        """
        # Import implementations here to avoid circular imports
        from .sqlite import SQLiteVectorStore
        
        # Check if ChromaDB is available
        try:
            from .chroma import ChromaVectorStore
            has_chroma = True
        except ImportError:
            has_chroma = False
        
        # Create the appropriate vector store
        if provider_type == "sqlite":
            return SQLiteVectorStore(config)
        elif provider_type == "chroma" and has_chroma:
            return ChromaVectorStore(config)
        elif provider_type == "chroma":
            raise ImportError(
                "ChromaDB is not installed. Install it with: pip install chromadb"
            )
        else:
            raise ValueError(f"Unsupported vector store provider: {provider_type}") 