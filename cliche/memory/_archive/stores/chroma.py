"""
ChromaDB Vector Store for CLIche Memory

ChromaDB-based implementation of the vector store interface.

Made with ❤️ by Pink Pixel
"""
import os
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

# Import ChromaDB - will raise ImportError if not installed
try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    raise ImportError(
        "ChromaDB is not installed. Install it with: pip install chromadb"
    )

from .base import VectorStoreBase

logger = logging.getLogger(__name__)


class ChromaVectorStore(VectorStoreBase):
    """ChromaDB-based vector store implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ChromaDB vector store
        
        Args:
            config: Configuration for the vector store
        """
        # Extract configuration
        self.data_dir = os.path.expanduser(config.get("data_dir", "~/.config/cliche/memory/chroma"))
        self.collection_name = config.get("collection_name", "cliche_memories")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize ChromaDB client
        try:
            self.client = chromadb.PersistentClient(path=self.data_dir)
            
            # Check if collection exists
            collection_exists = False
            try:
                collections = self.client.list_collections()
                for coll in collections:
                    if coll.name == self.collection_name:
                        collection_exists = True
                        break
            except Exception as e:
                logger.warning(f"Error listing collections: {str(e)}")
            
            # If collection exists, either use it or recreate it
            if collection_exists:
                try:
                    self.collection = self.client.get_collection(
                        name=self.collection_name
                    )
                    logger.info(f"Using existing ChromaDB collection: {self.collection_name}")
                    
                    # Validate the collection by trying a simple query
                    try:
                        self.collection.query(
                            query_texts=["test query"], 
                            n_results=1
                        )
                    except Exception as query_err:
                        # If query fails, collection might be corrupted - recreate it
                        logger.warning(f"Error querying collection: {str(query_err)}, will recreate")
                        self.client.delete_collection(self.collection_name)
                        self.collection = self.client.create_collection(
                            name=self.collection_name,
                            metadata={"description": "CLIche memories collection"}
                        )
                        logger.info(f"Recreated ChromaDB collection: {self.collection_name}")
                except Exception as get_err:
                    logger.warning(f"Error getting collection: {str(get_err)}, will create new")
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        metadata={"description": "CLIche memories collection"}
                    )
                    logger.info(f"Created new ChromaDB collection: {self.collection_name}")
            else:
                # Create a new collection
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "CLIche memories collection"}
                )
                logger.info(f"Created new ChromaDB collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
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
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            # Add timestamp if not present
            if "created_at" not in metadata:
                metadata["created_at"] = int(time.time())
            
            metadata["updated_at"] = int(time.time())
            
            # Add the memory to ChromaDB - let ChromaDB handle embeddings
            try:
                # First try using provided embedding
                self.collection.upsert(
                    ids=[memory_id],
                    documents=[content],
                    embeddings=[embedding],
                    metadatas=[metadata]
                )
                logger.info(f"Successfully added memory to ChromaDB with provided embedding")
            except ValueError as ve:
                if "Embedding dimension" in str(ve) and "does not match" in str(ve):
                    logger.warning(f"Dimension mismatch: {str(ve)}, letting ChromaDB generate embeddings")
                    
                    # Let ChromaDB generate embeddings
                    self.collection.upsert(
                        ids=[memory_id],
                        documents=[content],
                        metadatas=[metadata]
                    )
                    logger.info(f"Successfully added memory to ChromaDB with auto-generated embedding")
                else:
                    # Other ValueError that we can't handle
                    raise
            
            return memory_id
        except Exception as e:
            logger.error(f"Failed to add memory to ChromaDB: {str(e)}")
            raise
    
    def search(
        self,
        query_embedding: Optional[List[float]] = None,
        query_text: Optional[str] = None,
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_similarity: float = 0.0,
        skip_embedding_search: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for memories similar to the query
        
        Args:
            query_embedding: Embedding vector for the query
            query_text: Text query (used if query_embedding is None)
            limit: Maximum number of results to return
            filter_metadata: Filters to apply to the search
            min_similarity: Minimum similarity threshold
            skip_embedding_search: Whether to skip embedding search
            
        Returns:
            List of memories, each with ID, content, metadata, and similarity score
        """
        try:
            # Convert filters to ChromaDB where clause
            where_clause = self._filters_to_where_clause(filter_metadata)
            
            # Determine search method
            if skip_embedding_search or (query_embedding is None and query_text is None):
                # Just get memories matching filters
                result = self.collection.get(
                    where=where_clause,
                    limit=limit
                )
                
                # Process results
                memories = []
                
                if result["ids"]:
                    for i in range(len(result["ids"])):
                        memory_id = result["ids"][i]
                        content = result["documents"][i] if "documents" in result and result["documents"] else ""
                        metadata = result["metadatas"][i] if "metadatas" in result and result["metadatas"] else {}
                        
                        memories.append({
                            "id": memory_id,
                            "content": content,
                            "metadata": metadata,
                            "score": 1.0  # Default score for non-embedding search
                        })
                
                return memories
            
            # Perform embedding search
            try:
                if query_embedding is not None:
                    # Use provided embedding
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=limit,
                        where=where_clause
                    )
                elif query_text is not None:
                    # Let ChromaDB generate embedding from text
                    results = self.collection.query(
                        query_texts=[query_text],
                        n_results=limit,
                        where=where_clause
                    )
                else:
                    # No query provided
                    return []
                
                # Process results
                memories = []
                
                # Check if we got any results
                if results["ids"] and len(results["ids"][0]) > 0:
                    for i in range(len(results["ids"][0])):
                        memory_id = results["ids"][0][i]
                        content = results["documents"][0][i] if results["documents"] else ""
                        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                        
                        # Get similarity score (ChromaDB returns distances, so convert to similarity)
                        # ChromaDB cosine distance is 1 - cosine_similarity, so we convert it back
                        if "distances" in results and results["distances"] and len(results["distances"][0]) > i:
                            distance = results["distances"][0][i]
                            score = 1.0 - distance  # Convert distance to similarity
                        else:
                            score = 0.0
                        
                        # Apply similarity threshold
                        if score >= min_similarity:
                            memories.append({
                                "id": memory_id,
                                "content": content,
                                "metadata": metadata,
                                "score": score
                            })
                
                return memories
            except Exception as search_err:
                logger.error(f"Error during embedding search: {str(search_err)}")
                # Fall back to non-embedding search
                result = self.collection.get(
                    where=where_clause,
                    limit=limit
                )
                
                # Process results
                memories = []
                
                if result["ids"]:
                    for i in range(len(result["ids"])):
                        memory_id = result["ids"][i]
                        content = result["documents"][i] if "documents" in result and result["documents"] else ""
                        metadata = result["metadatas"][i] if "metadatas" in result and result["metadatas"] else {}
                        
                        memories.append({
                            "id": memory_id,
                            "content": content,
                            "metadata": metadata,
                            "score": 1.0  # Default score for non-embedding search
                        })
                
                return memories
        except Exception as e:
            logger.error(f"Failed to search memories in ChromaDB: {str(e)}")
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
            result = self.collection.get(
                ids=[memory_id],
                include=["embeddings", "documents", "metadatas"]
            )
            
            if not result["ids"]:
                return None
            
            idx = result["ids"].index(memory_id) if memory_id in result["ids"] else -1
            if idx == -1:
                return None
            
            return {
                "id": memory_id,
                "content": result["documents"][idx] if "documents" in result and result["documents"] else "",
                "embedding": result["embeddings"][idx] if "embeddings" in result and result["embeddings"] else [],
                "metadata": result["metadatas"][idx] if "metadatas" in result and result["metadatas"] else {}
            }
        except Exception as e:
            logger.error(f"Failed to get memory from ChromaDB: {str(e)}")
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
            current = self.get(memory_id)
            if not current:
                return False
            
            # Prepare update parameters
            update_params = {}
            
            if content is not None:
                update_params["documents"] = [content]
            
            if embedding is not None:
                update_params["embeddings"] = [embedding]
            
            if metadata is not None:
                # Merge with existing metadata
                updated_metadata = current.get("metadata", {}).copy()
                updated_metadata.update(metadata)
                
                # Update timestamp
                updated_metadata["updated_at"] = int(time.time())
                
                update_params["metadatas"] = [updated_metadata]
            else:
                # Just update the timestamp
                metadata_with_time = current.get("metadata", {}).copy()
                metadata_with_time["updated_at"] = int(time.time())
                update_params["metadatas"] = [metadata_with_time]
            
            # Update the memory
            if update_params:
                try:
                    self.collection.update(
                        ids=[memory_id],
                        **update_params
                    )
                except ValueError as ve:
                    if "Embedding dimension" in str(ve) and "does not match" in str(ve) and "embeddings" in update_params:
                        # Handle dimension mismatch by removing the embedding parameter
                        logger.warning(f"Dimension mismatch during update: {str(ve)}")
                        del update_params["embeddings"]
                        
                        # Try again without embeddings
                        self.collection.update(
                            ids=[memory_id],
                            **update_params
                        )
                    else:
                        raise
            
            return True
        except Exception as e:
            logger.error(f"Failed to update memory in ChromaDB: {str(e)}")
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
            # Check if memory exists
            current = self.get(memory_id)
            if not current:
                return False
            
            # Delete the memory
            self.collection.delete(ids=[memory_id])
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory from ChromaDB: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all memories from the vector store
        
        Returns:
            True if the vector store was cleared, False otherwise
        """
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            
            # Recreate the collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "CLIche memories collection"}
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear memories from ChromaDB: {str(e)}")
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
            # Print debug information
            logger.info(f"ChromaVectorStore.count called with filters: {filters}")
            
            # Convert filters to ChromaDB where clause
            where_clause = self._filters_to_where_clause(filters)
            logger.info(f"Converted to where_clause: {where_clause}")
            
            # Get the count
            if where_clause:
                try:
                    result = self.collection.get(where=where_clause)
                except Exception as e:
                    logger.error(f"Error querying with where clause: {e}")
                    # Try without where clause as fallback
                    result = self.collection.get()
            else:
                result = self.collection.get()
            
            # Print debug information about the result
            count = len(result["ids"]) if "ids" in result else 0
            logger.info(f"Count result: {count}")
            return count
        except Exception as e:
            logger.error(f"Failed to count memories in ChromaDB: {str(e)}")
            return 0
    
    def _filters_to_where_clause(self, filters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Convert filters dictionary to ChromaDB where clause
        
        Args:
            filters: Filters to convert
            
        Returns:
            ChromaDB where clause
        """
        if not filters:
            return None
        
        # ChromaDB only supports exact matches on metadata fields
        # We'll convert the filters to a simple where clause
        where_clause = {}
        
        # Special handling for user_id filter
        if "user_id" in filters:
            where_clause["user_id"] = filters["user_id"]
        
        # Copy other filters directly
        for key, value in filters.items():
            if key != "user_id":
                where_clause[key] = value
        
        return where_clause if where_clause else None
