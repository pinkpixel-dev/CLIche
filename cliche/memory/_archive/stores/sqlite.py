"""
SQLite Vector Store for CLIche Memory

SQLite-based implementation of the vector store interface.

Made with ❤️ by Pink Pixel
"""
import os
import json
import logging
import sqlite3
import time
import uuid
import threading
import numpy as np
from typing import Any, Dict, List, Optional, Tuple

from .base import VectorStoreBase

logger = logging.getLogger(__name__)


class SQLiteVectorStore(VectorStoreBase):
    """SQLite-based vector store implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SQLite vector store
        
        Args:
            config: Configuration for the vector store
        """
        # Extract configuration
        self.data_dir = config.get("data_dir", os.path.expanduser("~/.config/cliche/memory"))
        self.collection_name = config.get("collection_name", "cliche_memories")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Set up database
        self.db_path = os.path.join(self.data_dir, f"{self.collection_name}.db")
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.lock = threading.Lock()
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database for storing embeddings"""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                # Create table for storing embeddings
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        embedding BLOB NOT NULL,
                        metadata TEXT,
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL
                    )
                ''')
                
                # Create index for faster searches
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_memories_id ON memories(id)
                ''')
                
                self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
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
        try:
            # Generate ID if not provided
            if memory_id is None:
                memory_id = str(uuid.uuid4())
            
            # Convert embedding to bytes for storage
            embedding_bytes = self._embedding_to_bytes(embedding)
            
            # Convert metadata to JSON string
            metadata_str = json.dumps(metadata) if metadata else None
            
            # Get current timestamp
            current_time = int(time.time())
            
            with self.lock:
                cursor = self.connection.cursor()
                
                # Delete existing memory if it exists
                cursor.execute(
                    "DELETE FROM memories WHERE id = ?",
                    (memory_id,)
                )
                
                # Insert new memory
                cursor.execute(
                    """
                    INSERT INTO memories 
                    (id, content, embedding, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (memory_id, content, embedding_bytes, metadata_str, current_time, current_time)
                )
                
                self.connection.commit()
            
            return memory_id
        except Exception as e:
            logger.error(f"Failed to add memory: {str(e)}")
            raise
    
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
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                # Get all memories
                if filters and 'user_id' in filters:
                    cursor.execute(
                        """
                        SELECT id, content, embedding, metadata, created_at, updated_at
                        FROM memories
                        WHERE json_extract(metadata, '$.user_id') = ?
                        """,
                        (filters['user_id'],)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, content, embedding, metadata, created_at, updated_at
                        FROM memories
                        """
                    )
                
                rows = cursor.fetchall()
            
            if not rows:
                return []
            
            # Calculate similarities
            memories_with_scores = []
            for row in rows:
                memory_id, content, embedding_bytes, metadata_str, created_at, updated_at = row
                
                # Convert embedding bytes to list
                memory_embedding = self._bytes_to_embedding(embedding_bytes)
                
                # Parse metadata
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Calculate similarity
                similarity = self._calculate_similarity(query_embedding, memory_embedding)
                
                memories_with_scores.append({
                    "id": memory_id,
                    "content": content,
                    "metadata": metadata,
                    "score": similarity,
                    "created_at": created_at,
                    "updated_at": updated_at
                })
            
            # Sort by similarity and return top results
            memories_with_scores.sort(key=lambda x: x["score"], reverse=True)
            return memories_with_scores[:limit]
        except Exception as e:
            logger.error(f"Failed to search memories: {str(e)}")
            return []
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by ID
        
        Args:
            memory_id: ID of the memory to get
            
        Returns:
            Memory if found, None otherwise
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute(
                    """
                    SELECT id, content, embedding, metadata, created_at, updated_at
                    FROM memories
                    WHERE id = ?
                    """,
                    (memory_id,)
                )
                
                row = cursor.fetchone()
            
            if not row:
                return None
            
            memory_id, content, embedding_bytes, metadata_str, created_at, updated_at = row
            
            # Convert embedding bytes to list
            embedding = self._bytes_to_embedding(embedding_bytes)
            
            # Parse metadata
            metadata = json.loads(metadata_str) if metadata_str else {}
            
            return {
                "id": memory_id,
                "content": content,
                "embedding": embedding,
                "metadata": metadata,
                "created_at": created_at,
                "updated_at": updated_at
            }
        except Exception as e:
            logger.error(f"Failed to get memory: {str(e)}")
            return None
    
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
        try:
            # Get current memory
            current_memory = self.get(memory_id)
            if not current_memory:
                return False
            
            # Update fields
            new_content = content if content is not None else current_memory["content"]
            new_embedding = embedding if embedding is not None else current_memory["embedding"]
            
            # Handle metadata update
            if metadata is not None:
                new_metadata = metadata
            else:
                new_metadata = current_memory["metadata"]
            
            # Convert embedding to bytes
            embedding_bytes = self._embedding_to_bytes(new_embedding)
            
            # Convert metadata to JSON string
            metadata_str = json.dumps(new_metadata) if new_metadata else None
            
            # Get current timestamp
            current_time = int(time.time())
            
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute(
                    """
                    UPDATE memories
                    SET content = ?, embedding = ?, metadata = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (new_content, embedding_bytes, metadata_str, current_time, memory_id)
                )
                
                self.connection.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to update memory: {str(e)}")
            return False
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory from the vector store
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if the memory was deleted, False otherwise
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute(
                    "DELETE FROM memories WHERE id = ?",
                    (memory_id,)
                )
                
                self.connection.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete memory: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all memories from the vector store
        
        Returns:
            True if the vector store was cleared, False otherwise
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute("DELETE FROM memories")
                
                self.connection.commit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear memories: {str(e)}")
            return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count memories in the vector store
        
        Args:
            filters: Filters to apply to the count
            
        Returns:
            Number of memories matching the filters
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                if filters and 'user_id' in filters:
                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM memories
                        WHERE json_extract(metadata, '$.user_id') = ?
                        """,
                        (filters['user_id'],)
                    )
                else:
                    cursor.execute("SELECT COUNT(*) FROM memories")
                
                count = cursor.fetchone()[0]
            
            return count
        except Exception as e:
            logger.error(f"Failed to count memories: {str(e)}")
            return 0
    
    def _embedding_to_bytes(self, embedding: List[float]) -> bytes:
        """Convert embedding to bytes for storage"""
        return json.dumps(embedding).encode()
    
    def _bytes_to_embedding(self, embedding_bytes: bytes) -> List[float]:
        """Convert bytes to embedding"""
        return json.loads(embedding_bytes.decode())
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity (between -1 and 1)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate dot product
        dot_product = np.dot(vec1, vec2)
        
        # Calculate magnitudes
        magnitude1 = np.linalg.norm(vec1)
        magnitude2 = np.linalg.norm(vec2)
        
        # Calculate cosine similarity
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def __del__(self):
        """Close the database connection on deletion"""
        try:
            if hasattr(self, 'connection'):
                self.connection.close()
        except Exception:
            pass 