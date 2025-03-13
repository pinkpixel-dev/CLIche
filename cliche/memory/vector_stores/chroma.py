"""
ChromaDB vector store for CLIche memory system.

This module provides a vector store implementation using ChromaDB.

Made with ❤️ by Pink Pixel
"""
from typing import List, Dict, Any, Optional, Tuple, Union
import os
import logging
import numpy as np
from pathlib import Path

from ..config import VectorStoreConfig
from .base import BaseVectorStore

# Import ChromaDB conditionally to handle cases where it's not installed
try:
    import chromadb
    from chromadb.utils import embedding_functions
    from chromadb.api.models.Collection import Collection
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class ChromaVectorStore(BaseVectorStore):
    """
    Vector store implementation using ChromaDB.
    """
    
    def __init__(self, config: VectorStoreConfig):
        """
        Initialize the ChromaDB vector store.
        
        Args:
            config: Configuration for the vector store
        """
        super().__init__(config)
        self.client = None
        self.collection = None
        self.embedding_function = None
        
        # Check if ChromaDB is installed
        if not CHROMA_AVAILABLE:
            self.logger.error("ChromaDB is not installed. Please install it with 'pip install chromadb'.")
            return
        
        # Initialize if possible
        self.initialize()
    
    def initialize(self) -> bool:
        """
        Initialize the ChromaDB client and collection.
        
        Returns:
            True if successful, False otherwise
        """
        if not CHROMA_AVAILABLE:
            self.logger.error("ChromaDB is not installed. Please install it with 'pip install chromadb'.")
            return False
        
        try:
            # Create the client
            if self.config.host:
                # Use HTTP client if host is specified
                self.client = chromadb.HttpClient(
                    host=self.config.host,
                    port=self.config.port or 8000
                )
            else:
                # Use persistent client if persist_directory is specified
                persist_directory = self.config.persist_directory
                if not persist_directory:
                    # Default to ~/.config/cliche/memory/chroma
                    config_dir = Path.home() / ".config" / "cliche" / "memory"
                    persist_directory = str(config_dir / "chroma")
                
                # Ensure directory exists
                os.makedirs(persist_directory, exist_ok=True)
                
                self.client = chromadb.PersistentClient(
                    path=persist_directory
                )
            
            # Create or get the collection
            collection_name = self.config.collection_name
            
            # Check if collection exists
            try:
                self.collection = self.client.get_collection(collection_name)
                self.logger.info(f"Using existing collection: {collection_name}")
            except ValueError:
                # Create the collection if it doesn't exist
                self.logger.info(f"Creating new collection: {collection_name}")
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"dimensions": self.config.dimensions}
                )
            
            # Set the flag
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            return False
    
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
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Generate an ID if not provided
        if memory_id is None:
            memory_id = self.generate_id()
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Convert numpy array to list for ChromaDB
        embedding_list = embedding.tolist()
        
        # Add the memory to ChromaDB
        try:
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding_list],
                documents=[content],
                metadatas=[metadata]
            )
            self.logger.debug(f"Added memory with ID: {memory_id}")
            return memory_id
        except Exception as e:
            self.logger.error(f"Failed to add memory: {e}")
            raise
    
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
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Convert numpy array to list for ChromaDB
        embedding_list = query_embedding.tolist()
        
        # Prepare where clause for filtering
        where = None
        if filter_metadata:
            where = self._prepare_where_clause(filter_metadata)
        
        # Search for memories
        try:
            results = self.collection.query(
                query_embeddings=[embedding_list],
                n_results=limit,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process the results
            memories = []
            ids = results.get("ids", [[]])[0]
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            for i in range(len(ids)):
                # ChromaDB returns distance, convert to similarity score (1 - distance)
                score = 1.0 - distances[i]
                
                # Skip if below minimum score
                if score < min_score:
                    continue
                
                memories.append({
                    "id": ids[i],
                    "content": documents[i],
                    "metadata": metadatas[i],
                    "score": score
                })
            
            return memories
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            raise
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to get
            
        Returns:
            Memory if found, None otherwise
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Get the memory from ChromaDB
        try:
            results = self.collection.get(
                ids=[memory_id],
                include=["documents", "metadatas", "embeddings"]
            )
            
            # Check if memory was found
            ids = results.get("ids", [])
            if not ids or memory_id not in ids:
                return None
            
            # Get the index of the memory
            index = ids.index(memory_id)
            
            # Get the memory data
            document = results.get("documents", [])[index]
            metadata = results.get("metadatas", [])[index]
            embedding = results.get("embeddings", [])[index]
            
            # Convert embedding to numpy array
            embedding_array = np.array(embedding)
            
            return {
                "id": memory_id,
                "content": document,
                "metadata": metadata,
                "embedding": embedding_array
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory: {e}")
            return None
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Delete the memory from ChromaDB
        try:
            self.collection.delete(ids=[memory_id])
            self.logger.debug(f"Deleted memory with ID: {memory_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete memory: {e}")
            return False
    
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
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Get the current memory to keep unchanged values
        current = self.get(memory_id)
        if not current:
            self.logger.warning(f"Memory not found for update: {memory_id}")
            return False
        
        # Prepare update values
        update_values = {}
        
        if content is not None:
            update_values["documents"] = [content]
        
        if embedding is not None:
            update_values["embeddings"] = [embedding.tolist()]
        
        if metadata is not None:
            # Merge new metadata with existing metadata
            new_metadata = {**current["metadata"], **metadata}
            update_values["metadatas"] = [new_metadata]
        
        # Skip update if no values to update
        if not update_values:
            self.logger.warning("No values to update")
            return True
        
        # Update the memory in ChromaDB
        try:
            self.collection.update(
                ids=[memory_id],
                **update_values
            )
            self.logger.debug(f"Updated memory with ID: {memory_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update memory: {e}")
            return False
    
    def count(self, filter_metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Count memories.
        
        Args:
            filter_metadata: Metadata to filter by
            
        Returns:
            Number of memories
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Prepare where clause for filtering
        where = None
        if filter_metadata:
            where = self._prepare_where_clause(filter_metadata)
        
        # Count memories
        try:
            # For now, we need to get all IDs and count them
            results = self.collection.get(
                where=where,
                include=[]
            )
            
            # Count the IDs
            return len(results.get("ids", []))
        except Exception as e:
            self.logger.error(f"Failed to count memories: {e}")
            return 0
    
    def _prepare_where_clause(self, filter_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a where clause for ChromaDB from filter metadata.
        
        Args:
            filter_metadata: Metadata to filter by
            
        Returns:
            Where clause for ChromaDB
        """
        # ChromaDB uses a specific format for where clauses
        where_clause = {}
        
        for key, value in filter_metadata.items():
            if isinstance(value, list):
                # For list values, use $in operator
                where_clause[key] = {"$in": value}
            elif isinstance(value, dict) and all(k.startswith('$') for k in value.keys()):
                # For operator dicts, use as is
                where_clause[key] = value
            else:
                # For simple values, use equality
                where_clause[key] = value
        
        return where_clause
    
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        This method is called when the vector store is no longer needed.
        """
        # Nothing to clean up for ChromaDB
        pass
    
    def get_collection_name(self) -> str:
        """
        Get the name of the collection.
        
        Returns:
            Collection name
        """
        return self.config.collection_name
    
    def collection_exists(self) -> bool:
        """
        Check if the collection exists.
        
        Returns:
            True if exists, False otherwise
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                return False
        
        # List collections and check if this one exists
        try:
            collections = self.client.list_collections()
            for collection in collections:
                if collection.name == self.config.collection_name:
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to check if collection exists: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """
        List all collections.
        
        Returns:
            List of collection names
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                return []
        
        # List collections
        try:
            collections = self.client.list_collections()
            return [collection.name for collection in collections]
        except Exception as e:
            self.logger.error(f"Failed to list collections: {e}")
            return []
