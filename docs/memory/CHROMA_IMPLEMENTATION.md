# CLIche ChromaDB Implementation

## Overview

This document details the implementation of the ChromaDB vector store for CLIche, following mem0's simplified approach of using a single storage system rather than the current dual storage model. By using only ChromaDB, we'll simplify the architecture and improve reliability.

## Design Goals

1. **Simplification**: Use ChromaDB as the sole storage mechanism for memories
2. **Reliability**: Ensure consistent behavior for storage and retrieval
3. **Performance**: Optimize for fast similarity search
4. **Flexibility**: Support different embedding dimensions and providers

## Implementation

### 1. Base Vector Store Interface

```python
# cliche/memory/vector_stores/base.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class VectorStoreBase(ABC):
    """Base class for vector stores"""
    
    @abstractmethod
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
    
    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for memories similar to the query
        
        Args:
            query_embedding: Embedding vector for the query
            limit: Maximum number of results to return
            filter_metadata: Filters to apply to the search
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of memories, each with ID, content, metadata, and similarity score
        """
        pass
    
    @abstractmethod
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory as a dictionary, or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if memory was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a memory
        
        Args:
            memory_id: ID of the memory to update
            content: New content for the memory
            embedding: New embedding vector for the memory
            metadata: New metadata for the memory
            
        Returns:
            True if memory was updated, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count memories matching the filters
        
        Args:
            filters: Filters to apply
            
        Returns:
            Number of matching memories
        """
        pass
```

### 2. ChromaDB Vector Store Implementation

```python
# cliche/memory/vector_stores/chroma.py

import os
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    raise ImportError(
        "ChromaDB is required but not installed. Install with: pip install chromadb"
    )

from .base import VectorStoreBase

logger = logging.getLogger(__name__)

class ChromaVectorStore(VectorStoreBase):
    """ChromaDB-based vector store implementation"""
    
    def __init__(
        self,
        collection_name: str = "cliche_memories",
        persistent_path: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        dimensions: Optional[int] = None
    ):
        """
        Initialize the ChromaDB vector store
        
        Args:
            collection_name: Name of the collection to use
            persistent_path: Path to store ChromaDB data (if None, uses ~/.config/cliche/memory/chroma)
            host: Host for remote ChromaDB (if None, uses local persistence)
            port: Port for remote ChromaDB
            dimensions: Dimensions for embeddings (only used for validation)
        """
        self.collection_name = collection_name
        self.dimensions = dimensions
        
        # Set up persistent path
        if persistent_path is None:
            home_dir = os.path.expanduser("~")
            persistent_path = os.path.join(home_dir, ".config", "cliche", "memory", "chroma")
        
        os.makedirs(persistent_path, exist_ok=True)
        
        # Initialize ChromaDB settings
        settings = Settings(anonymized_telemetry=False)
        
        # Use remote client if host is provided, otherwise use local
        if host and port:
            logger.info(f"Connecting to ChromaDB at {host}:{port}")
            settings.chroma_server_host = host
            settings.chroma_server_http_port = port
            settings.chroma_api_impl = "chromadb.api.fastapi.FastAPI"
            self.client = chromadb.HttpClient(settings)
        else:
            logger.info(f"Using local ChromaDB at {persistent_path}")
            settings.persist_directory = persistent_path
            settings.is_persistent = True
            self.client = chromadb.PersistentClient(path=persistent_path, settings=settings)
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Using existing collection: {collection_name}")
        except Exception as e:
            logger.info(f"Creating new collection: {collection_name}")
            self.collection = self.client.create_collection(name=collection_name)
    
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
        # Generate ID if not provided
        if memory_id is None:
            memory_id = str(uuid.uuid4())
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Add timestamps if not present
        current_time = int(time.time())
        if "created_at" not in metadata:
            metadata["created_at"] = current_time
        metadata["updated_at"] = current_time
        
        # Make sure metadata is JSON serializable
        metadata = self._ensure_json_serializable(metadata)
        
        try:
            # Try adding with embeddings
            self.collection.upsert(
                ids=[memory_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            logger.info(f"Added memory with ID {memory_id} using provided embedding")
        except ValueError as e:
            # Handle dimension mismatch by letting ChromaDB generate embeddings
            if "Embedding dimension" in str(e) and "does not match" in str(e):
                logger.warning(f"Dimension mismatch: {str(e)}, letting ChromaDB generate embeddings")
                
                # Add without embeddings (let ChromaDB generate them)
                self.collection.upsert(
                    ids=[memory_id],
                    documents=[content],
                    metadatas=[metadata]
                )
                logger.info(f"Added memory with ID {memory_id} using auto-generated embedding")
            else:
                # Re-raise other ValueError exceptions
                raise
        
        return memory_id
    
    def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for memories similar to the query
        
        Args:
            query_embedding: Embedding vector for the query
            limit: Maximum number of results to return
            filter_metadata: Filters to apply to the search
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of memories, each with ID, content, metadata, and similarity score
        """
        # Convert filter_metadata to ChromaDB where clause
        where_clause = self._metadata_to_where_clause(filter_metadata)
        
        try:
            # Search using query embedding
            results = self.collection.query(
                query_embeddings=[query_embedding],
                where=where_clause,
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            memories = []
            
            ids = results.get("ids", [[]])[0]
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            for i in range(len(ids)):
                # Skip results with similarity below threshold
                # Note: ChromaDB returns distances, not similarities (lower is better)
                # We convert to similarity (0-1 scale) where 1 is identical
                if distances[i] is not None:
                    # Convert distance to similarity (approximate, depends on distance metric)
                    # This assumes cosine distance; adjust formula if using different metrics
                    similarity = 1.0 - min(distances[i], 2.0) / 2.0
                    
                    if similarity < min_similarity:
                        continue
                else:
                    similarity = None
                
                memories.append({
                    "id": ids[i],
                    "content": documents[i],
                    "metadata": metadatas[i] if metadatas[i] else {},
                    "similarity": similarity
                })
            
            return memories
        except ValueError as e:
            # Handle dimension mismatch by trying query without embeddings
            if "Embedding dimension" in str(e) and "does not match" in str(e):
                logger.warning(f"Search dimension mismatch: {str(e)}, falling back to get() with filters")
                # Retrieve all memories matching the filter
                return self._get_filtered(where_clause, limit)
            else:
                # Re-raise other ValueError exceptions
                raise
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory as a dictionary, or None if not found
        """
        try:
            result = self.collection.get(
                ids=[memory_id],
                include=["documents", "metadatas"]
            )
            
            # Check if memory was found
            if not result or not result["ids"]:
                return None
            
            # Extract memory
            return {
                "id": result["ids"][0],
                "content": result["documents"][0] if result["documents"] else "",
                "metadata": result["metadatas"][0] if result["metadatas"] else {}
            }
        except Exception as e:
            logger.error(f"Error retrieving memory {memory_id}: {str(e)}")
            return None
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if memory was deleted, False otherwise
        """
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {str(e)}")
            return False
    
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a memory
        
        Args:
            memory_id: ID of the memory to update
            content: New content for the memory
            embedding: New embedding vector for the memory
            metadata: New metadata for the memory
            
        Returns:
            True if memory was updated, False otherwise
        """
        # Get existing memory
        existing = self.get(memory_id)
        if not existing:
            return False
        
        # Update only provided fields
        updated_content = content if content is not None else existing["content"]
        updated_metadata = existing["metadata"].copy()
        
        if metadata:
            updated_metadata.update(metadata)
        
        # Set updated timestamp
        updated_metadata["updated_at"] = int(time.time())
        
        # Make sure metadata is JSON serializable
        updated_metadata = self._ensure_json_serializable(updated_metadata)
        
        try:
            if embedding is not None:
                # Update with new embedding
                self.collection.update(
                    ids=[memory_id],
                    documents=[updated_content],
                    embeddings=[embedding],
                    metadatas=[updated_metadata]
                )
            else:
                # Update without embedding (let ChromaDB regenerate)
                self.collection.update(
                    ids=[memory_id],
                    documents=[updated_content],
                    metadatas=[updated_metadata]
                )
            
            return True
        except Exception as e:
            logger.error(f"Error updating memory {memory_id}: {str(e)}")
            return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count memories matching the filters
        
        Args:
            filters: Filters to apply
            
        Returns:
            Number of matching memories
        """
        where_clause = self._metadata_to_where_clause(filters)
        
        try:
            # Get filtered results (limited to a large number)
            result = self.collection.get(where=where_clause, limit=10000)
            
            # Return the count of IDs
            return len(result["ids"]) if "ids" in result else 0
        except Exception as e:
            logger.error(f"Error counting memories: {str(e)}")
            return 0
    
    def _metadata_to_where_clause(self, metadata: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Convert metadata filter to ChromaDB where clause
        
        Args:
            metadata: Metadata filter
            
        Returns:
            ChromaDB where clause
        """
        if not metadata:
            return None
        
        # Make a copy to avoid modifying the original
        where_clause = {}
        
        # Process each key
        for key, value in metadata.items():
            # Handle special operators ($eq, $gt, $lt, etc.)
            if isinstance(value, dict) and all(k.startswith("$") for k in value.keys()):
                # This is an operator clause
                where_clause[key] = value
            else:
                # Regular equality
                where_clause[key] = {"$eq": value}
        
        return where_clause
    
    def _get_filtered(self, where_clause: Optional[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """
        Get memories matching filters without embedding search
        
        Args:
            where_clause: ChromaDB where clause
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        try:
            # Get filtered results
            result = self.collection.get(
                where=where_clause,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            # Format results
            memories = []
            
            ids = result.get("ids", [])
            documents = result.get("documents", [])
            metadatas = result.get("metadatas", [])
            
            for i in range(len(ids)):
                memories.append({
                    "id": ids[i],
                    "content": documents[i] if i < len(documents) else "",
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "similarity": None  # No similarity score for non-embedding search
                })
            
            return memories
        except Exception as e:
            logger.error(f"Error getting filtered memories: {str(e)}")
            return []
    
    def _ensure_json_serializable(self, obj: Any) -> Any:
        """
        Ensure object is JSON serializable by converting non-serializable types
        
        Args:
            obj: Object to make serializable
            
        Returns:
            JSON serializable object
        """
        if isinstance(obj, dict):
            return {k: self._ensure_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._ensure_json_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # Convert non-serializable types to string
            return str(obj)
```

### 3. Vector Store Factory

```python
# cliche/memory/vector_stores/factory.py

from typing import Dict, Any, Optional
import logging

from .base import VectorStoreBase
from .chroma import ChromaVectorStore

logger = logging.getLogger(__name__)

class VectorStoreFactory:
    """Factory for creating vector stores"""
    
    # Map of vector store names to classes
    VECTOR_STORES = {
        "chroma": ChromaVectorStore,
        # We can add more vector stores in the future
    }
    
    @classmethod
    def create(cls, store_type: str, config: Optional[Dict[str, Any]] = None) -> VectorStoreBase:
        """
        Create a vector store instance
        
        Args:
            store_type: Type of vector store to create
            config: Configuration for the vector store
            
        Returns:
            Vector store instance
            
        Raises:
            ValueError: If store_type is not supported
        """
        if store_type not in cls.VECTOR_STORES:
            supported = ", ".join(cls.VECTOR_STORES.keys())
            raise ValueError(f"Unsupported vector store type: {store_type}. Supported types: {supported}")
        
        # Get vector store class
        vector_store_class = cls.VECTOR_STORES[store_type]
        
        # Create and return instance
        if config is None:
            config = {}
            
        try:
            return vector_store_class(**config)
        except Exception as e:
            logger.error(f"Error creating vector store {store_type}: {str(e)}")
            raise
```

## Usage Example

Here's how the ChromaDB vector store would be used in the Memory class:

```python
# Example usage in memory/main.py

from .vector_stores.factory import VectorStoreFactory
from .embeddings.factory import EmbeddingProviderFactory

class Memory:
    def __init__(self, config=None):
        if config is None:
            config = {}
        
        # Get embedding provider
        embedding_config = config.get("embedding", {})
        embedding_provider_name = embedding_config.get("provider", "ollama")
        self.embedding_provider = EmbeddingProviderFactory.create(
            embedding_provider_name,
            embedding_config.get("config", {})
        )
        
        # Get vector store configuration
        vector_store_config = config.get("vector_store", {})
        vector_store_name = vector_store_config.get("provider", "chroma")
        
        # Create vector store
        vector_store_params = vector_store_config.get("config", {})
        
        # Set dimensions from embedding provider
        vector_store_params["dimensions"] = self.embedding_provider.get_dimensions()
        
        self.vector_store = VectorStoreFactory.create(vector_store_name, vector_store_params)
        
    def add(self, content, metadata=None):
        """Add content to memory"""
        # Generate embedding
        embedding = self.embedding_provider.embed(content, action="add")
        
        # Add to vector store
        return self.vector_store.add(content, embedding, metadata)
    
    def search(self, query, limit=5, filters=None):
        """Search for similar content"""
        # Generate embedding
        query_embedding = self.embedding_provider.embed(query, action="search")
        
        # Search vector store
        return self.vector_store.search(query_embedding, limit=limit, filter_metadata=filters)
    
    def get(self, memory_id):
        """Get memory by ID"""
        return self.vector_store.get(memory_id)
    
    def delete(self, memory_id):
        """Delete memory by ID"""
        return self.vector_store.delete(memory_id)
    
    def update(self, memory_id, content=None, metadata=None):
        """Update memory"""
        embedding = None
        if content is not None:
            embedding = self.embedding_provider.embed(content, action="update")
        
        return self.vector_store.update(memory_id, content, embedding, metadata)
    
    def count(self, filters=None):
        """Count memories"""
        return self.vector_store.count(filters)
```

## Migration Strategy

To transition from the current dual storage system to ChromaDB-only storage, we'll need a migration script:

```python
# cliche/memory/migration.py

import os
import sqlite3
import logging
from typing import Dict, List, Any, Tuple

from .vector_stores.factory import VectorStoreFactory
from .embeddings.factory import EmbeddingProviderFactory
from .config import MemoryConfig

logger = logging.getLogger(__name__)

def migrate_sqlite_to_chroma(config: Dict[str, Any] = None) -> Tuple[int, int]:
    """
    Migrate memories from SQLite to ChromaDB
    
    Args:
        config: Memory configuration
        
    Returns:
        Tuple of (number of memories migrated, total memories in SQLite)
    """
    if config is None:
        config = {}
    
    # Create embedding provider
    embedding_config = config.get("embedding", {})
    embedding_provider_name = embedding_config.get("provider", "ollama")
    embedding_provider = EmbeddingProviderFactory.create(
        embedding_provider_name,
        embedding_config.get("config", {})
    )
    
    # Create vector store
    vector_store_config = config.get("vector_store", {})
    vector_store_name = vector_store_config.get("provider", "chroma")
    vector_store_params = vector_store_config.get("config", {}).copy()
    
    # Set dimensions from embedding provider
    vector_store_params["dimensions"] = embedding_provider.get_dimensions()
    
    vector_store = VectorStoreFactory.create(vector_store_name, vector_store_params)
    
    # Get SQLite database path
    data_dir = config.get("data_dir", os.path.expanduser("~/.config/cliche/memory"))
    collection_name = config.get("collection_name", "cliche_memories")
    db_path = os.path.join(data_dir, f"{collection_name}.db")
    
    # Check if SQLite database exists
    if not os.path.exists(db_path):
        logger.info(f"SQLite database not found at {db_path}")
        return (0, 0)
    
    # Open SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if memories table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
    if not cursor.fetchone():
        logger.info("Memories table not found in SQLite database")
        conn.close()
        return (0, 0)
    
    # Get all memories from SQLite
    cursor.execute("SELECT id, content, timestamp, embedding, metadata FROM memories")
    memories = cursor.fetchall()
    
    # Count memories
    total_memories = len(memories)
    migrated_memories = 0
    
    # Migrate each memory
    for memory_id, content, timestamp, embedding_json, metadata_json in memories:
        try:
            # Parse embedding and metadata
            embedding = None
            metadata = {}
            
            if metadata_json:
                try:
                    import json
                    metadata = json.loads(metadata_json)
                except Exception as e:
                    logger.warning(f"Failed to parse metadata for memory {memory_id}: {str(e)}")
            
            # Set timestamps
            if "created_at" not in metadata:
                metadata["created_at"] = timestamp
            if "updated_at" not in metadata:
                metadata["updated_at"] = timestamp
            
            # Generate new embedding
            try:
                embedding = embedding_provider.embed(content, action="add")
            except Exception as e:
                logger.warning(f"Failed to generate embedding for memory {memory_id}: {str(e)}")
                # Continue without embedding, ChromaDB will generate one
            
            # Add to ChromaDB
            vector_store.add(content, embedding, metadata, memory_id)
            migrated_memories += 1
            
        except Exception as e:
            logger.error(f"Failed to migrate memory {memory_id}: {str(e)}")
    
    conn.close()
    
    logger.info(f"Migrated {migrated_memories} of {total_memories} memories from SQLite to ChromaDB")
    return (migrated_memories, total_memories)
```

## Key Advantages of ChromaDB-Only Approach

1. **Single Source of Truth**: All memory data is stored in one place, eliminating synchronization issues
2. **Simplified Architecture**: Cleaner codebase with fewer components and failure points
3. **Better Semantic Search**: ChromaDB is optimized for vector similarity search
4. **Dimension Handling**: Automatic handling of different embedding dimensions
5. **Filtered Search**: Support for metadata filtering combined with similarity search
6. **Persistence**: Built-in persistence with no additional database needed
7. **Active Development**: ChromaDB is actively maintained and improved

## Handling Edge Cases

1. **Embedding Dimension Mismatches**:
   - Automatic fallback to let ChromaDB generate embeddings
   - Consistent dimension handling across add and search operations

2. **Metadata Filtering**:
   - Support for complex query operators ($eq, $gt, $lt, etc.)
   - Conversion of simple filters to ChromaDB where clauses

3. **Error Handling**:
   - Graceful handling of ChromaDB errors
   - Detailed logging for troubleshooting
   - Fallbacks for common error scenarios

4. **Performance**:
   - Optimized for large collections with many embeddings
   - Efficient handling of metadata filtering
   - Fast similarity search for finding relevant memories

## Conclusion

By adopting a ChromaDB-only approach for memory storage, CLIche will gain a simpler, more reliable, and more efficient memory system. The implementation leverages ChromaDB's strengths in vector similarity search while providing a clean abstraction through the VectorStoreBase interface. This design will make it easier to maintain and extend the memory system, while also improving the user experience through more consistent behavior. 