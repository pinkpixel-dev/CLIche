"""
Enhanced memory system for CLIche

Integrates memory extraction, embeddings, and categorization for improved memory capabilities.

Made with ❤️ by Pink Pixel
"""
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import uuid
import sqlite3
import os
import json
import time
from pathlib import Path

from .extraction import MemoryExtractor
from .embeddings import OllamaEmbeddingProvider, MemoryEmbeddingStore
from .categorization import MemoryCategorizer
from .provider import MemoryProvider

logger = logging.getLogger(__name__)

class EnhancedMemory:
    """
    Enhanced memory system that integrates extraction, embeddings, and categorization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced memory system
        
        Args:
            config: Configuration for the memory system
        """
        # Handle different config types
        provider_name = "ollama"
        provider_config = {}
        memory_config = {}
        
        # Handle Config object from core.py
        if hasattr(config, "config") and isinstance(config.config, dict):
            # This is a Config object from core.py
            provider_config = config.config.get("providers", {})
            memory_config = config.config.get("memory", {})
            provider_name = memory_config.get("provider", config.config.get("provider", "ollama"))
        # Handle direct dictionary config
        elif config and isinstance(config, dict):
            provider_config = config.get("providers", {})
            memory_config = config
            provider_name = memory_config.get("provider", "ollama")
        # Handle any other type of config object
        elif config is not None:
            # Try to access config dictionary differently if it's not a regular dict
            try:
                if hasattr(config, "get") and callable(config.get):
                    # Config object has a get method
                    provider_config = config.get("providers", {})
                    memory_config = config.get("memory", {}) or {}
                    provider_name = memory_config.get("provider", config.get("provider", "ollama"))
                else:
                    # Last resort, try to use dictionary-like access
                    try:
                        provider_config = config["providers"] if "providers" in config else {}
                        memory_config = config["memory"] if "memory" in config else {}
                        provider_name = memory_config.get("provider", config.get("provider", "ollama"))
                    except (TypeError, KeyError):
                        # If we can't access it as a dictionary, use defaults
                        pass
            except Exception as e:
                # Log the error but continue with defaults
                logger.warning(f"Error accessing config properties: {str(e)}")
        
        self.config = memory_config
        
        # Set up data directory - ensure this is defined before using it
        from pathlib import Path
        self.data_dir = memory_config.get("data_dir", str(Path.home() / ".config" / "cliche" / "memory"))
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize memory provider with safer config handling
        provider_specific_config = {}
        if isinstance(provider_config, dict) and provider_name in provider_config:
            provider_specific_config = provider_config[provider_name]
            
        # Initialize memory provider
        self.provider = MemoryProvider(
            provider=provider_name,
            config=provider_specific_config,
            data_dir=self.data_dir  # Pass the data_dir explicitly
        )
        
        # Initialize memory extractor
        self.extractor = MemoryExtractor(self.provider.llm)
        
        # Initialize embedding provider and store - ensure we use the Ollama provider
        self.embedding_provider = OllamaEmbeddingProvider(config)
        self.embedding_store = MemoryEmbeddingStore(self.embedding_provider, self.data_dir)
        
        # Initialize memory categorizer
        self.categorizer = MemoryCategorizer()

    def add_memory(self, content: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Add a memory to the system
        
        Args:
            content: Memory content
            user_id: User ID
            metadata: Additional metadata
            
        Returns:
            Memory ID if successful, None otherwise
        """
        try:
            # Initialize metadata if not provided
            if metadata is None:
                metadata = {}
                
            # Add user ID to metadata
            metadata["user_id"] = user_id
            
            # Log information about the memory being added
            logger.info(f"Adding memory for user {user_id}: '{content[:30]}...'")
            
            # First try using the provider method, which handles ChromaDB
            try:
                logger.info("Attempting to add memory via provider")
                memory_id = self.provider.add_memory(
                    content=content,
                    metadata=metadata,
                    user_id=user_id
                )
                if memory_id:
                    logger.info(f"Successfully added memory via provider (ID: {memory_id})")
                    return memory_id
                else:
                    logger.warning("Provider failed to add memory, falling back to direct database approach")
            except Exception as e:
                logger.warning(f"Provider method failed: {e}, falling back to direct database approach")
            
            # If the provider method failed, try the direct database approach
            try:
                # Generate a memory ID
                memory_id = str(uuid.uuid4())
                
                # Create database directory if it doesn't exist
                db_dir = os.path.join(self.data_dir)
                os.makedirs(db_dir, exist_ok=True)
                
                # Connect to the database
                db_path = os.path.join(db_dir, "cliche_memories.db")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Create memories table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        timestamp INTEGER NOT NULL
                    )
                ''')
                
                # Convert metadata to JSON
                metadata_str = json.dumps(metadata)
                
                # Insert into memories table
                cursor.execute(
                    """
                    INSERT INTO memories (id, content, user_id, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (memory_id, content, user_id, metadata_str, int(time.time()))
                )
                
                conn.commit()
                conn.close()
                
                logger.info(f"Successfully added memory via direct database (ID: {memory_id})")
                return memory_id
                
            except Exception as direct_error:
                logger.error(f"Direct database storage failed: {direct_error}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return None
    
    def search_memories(self, query: str, user_id: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search for memories by query
        
        Args:
            query: Search query
            user_id: User ID to filter memories by
            limit: Maximum number of results
            
        Returns:
            Dictionary with search results
        """
        if not query.strip():
            return {"results": [], "query": query}
        
        # First, try semantic search with embeddings
        try:
            # Get query embedding
            embedding = self.embedding_provider.get_embedding(query)
            
            if embedding:
                # Search for similar memories using embedding
                results = self.embedding_store.search_with_scores(query, limit)
                
                if results:
                    logger.info(f"Found {len(results)} results using semantic search")
                    
                    # Get memory details from database
                    # Ensure sqlite3 is imported
                    import sqlite3
                    
                    # Determine database path
                    if hasattr(self.provider, "db_path") and os.path.exists(self.provider.db_path):
                        db_path = self.provider.db_path
                    else:
                        # Default path
                        data_dir = Path.home() / ".config" / "cliche" / "memory"
                        db_path = str(data_dir / "cliche_memories.db")
                    
                    # Query memory details
                    conn = sqlite3.connect(db_path)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    memories = []
                    
                    for memory_id, similarity_score in results:
                        # Build query to get memory details
                        query = "SELECT * FROM memories WHERE id = ? AND user_id = ?"
                        cursor.execute(query, (memory_id, user_id))
                        row = cursor.fetchone()
                        
                        if row:
                            # Convert row to dictionary and add similarity score
                            memory = dict(row)
                            memory["score"] = similarity_score
                            memories.append(memory)
                    
                    conn.close()
                    
                    return {
                        "results": memories,
                        "query": query,
                        "method": "semantic_search"
                    }
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            print(f"Semantic search failed: {e}")
        
        # Fall back to SQLite-based search
        try:
            # Import sqlite3 if not already imported
            import sqlite3
            
            # Determine database path
            if hasattr(self.provider, "db_path") and os.path.exists(self.provider.db_path):
                db_path = self.provider.db_path
            else:
                # Default path
                data_dir = Path.home() / ".config" / "cliche" / "memory"
                db_path = str(data_dir / "cliche_memories.db")
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Use SQLite full-text search
            search_terms = query.split()
            search_pattern = " OR ".join([f"%{term}%" for term in search_terms])
            
            query_sql = """
                SELECT * FROM memories 
                WHERE user_id = ? AND content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            
            cursor.execute(query_sql, (user_id, f"%{search_pattern}%", limit))
            results = cursor.fetchall()
            
            # Convert to dictionaries
            memories = [dict(row) for row in results]
            
            conn.close()
            
            return {
                "results": memories,
                "query": query,
                "method": "keyword_search"
            }
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"results": [], "query": query, "error": str(e)}
    
    def detect_memory_request(self, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Detect if a query is a memory request
        
        Args:
            query: Query to check
            
        Returns:
            Tuple of (is_memory_request, memory_content, metadata)
        """
        try:
            return self.extractor.detect_memory_request(query)
        except Exception as e:
            logger.error(f"Failed to detect memory request: {e}")
            return False, "", {}
    
    def enhance_with_memories(self, message: str, user_id: str) -> str:
        """
        Enhance a message with relevant memories
        
        Args:
            message: Message to enhance
            user_id: User ID
            
        Returns:
            Enhanced message
        """
        try:
            # Search for relevant memories
            search_results = self.search_memories(message, user_id)
            
            # Handle different return types from search_memories
            if isinstance(search_results, dict):
                memories = search_results.get("results", [])
            elif isinstance(search_results, list):
                memories = search_results
            else:
                logger.warning(f"Unexpected search_memories result type: {type(search_results)}")
                memories = []
            
            if not memories:
                return message
            
            # Format memories for inclusion
            memory_text = "\n\nRelevant memories:\n"
            for memory in memories:
                # Handle different memory object types
                if isinstance(memory, dict):
                    content = memory.get("content", "")
                elif hasattr(memory, "content"):
                    # Could be an object with a content attribute
                    content = memory.content
                else:
                    # Last resort - convert to string
                    content = str(memory)
                
                if content:
                    memory_text += f"- {content}\n"
            
            # Add memories to the message
            enhanced_message = f"{message}\n{memory_text}"
            return enhanced_message
        except Exception as e:
            logger.error(f"Failed to enhance with memories: {e}")
            return message
    
    def extract_and_store_memories(self, conversation: str, user_id: str) -> List[str]:
        """
        Extract facts from a conversation and store them as memories
        
        Args:
            conversation: Conversation to extract facts from
            user_id: User ID to associate with the memories
            
        Returns:
            List of memory IDs for stored memories
        """
        try:
            # Extract facts from the conversation
            facts = []
            try:
                facts = self.extractor.extract_facts(conversation)
            except Exception as e:
                logger.warning(f"Advanced fact extraction failed: {e}")
                # Basic extraction fallback
                try:
                    if hasattr(self.extractor, '_basic_extract_facts'):
                        facts = self.extractor._basic_extract_facts(conversation)
                except Exception as basic_error:
                    logger.error(f"Basic fact extraction failed: {basic_error}")
                    # No facts extracted
            
            # Store each fact as a memory
            memory_ids = []
            for fact in facts:
                fact_content = fact.get("content", "") if isinstance(fact, dict) else str(fact)
                if not fact_content:
                    continue
                
                # Get metadata from the fact
                metadata = fact.get("metadata", {}) if isinstance(fact, dict) else {}
                
                # Add source information
                metadata["source"] = "auto_extraction"
                metadata["extraction_time"] = datetime.now().isoformat()
                
                # Store the memory using our updated add_memory method
                memory_id = self.add_memory(fact_content, user_id, metadata)
                if memory_id:
                    memory_ids.append(memory_id)
            
            return memory_ids
        except Exception as e:
            logger.error(f"Failed to extract and store memories: {e}")
            return []
            
    def chat_with_memory(self, message: str, user_id: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response to a query using relevant memories as context
        
        Args:
            message: User message
            user_id: User ID
            system_prompt: Optional system prompt
            
        Returns:
            Generated response
        """
        try:
            # Search for relevant memories using our updated search method
            search_results = self.search_memories(message, user_id)
            memories = search_results.get("results", [])
            
            # Format memories as context
            memory_context = ""
            if memories:
                memory_context = "\nRelevant memories:\n"
                for memory in memories:
                    content = memory.get("content", "") if isinstance(memory, dict) else str(memory)
                    if content:
                        memory_context += f"- {content}\n"
            
            # Build the prompt
            if system_prompt is None:
                system_prompt = """You are a helpful assistant with access to the user's memories.
Your goal is to provide helpful, accurate responses based on what you know about the user.
Always use the provided memories to personalize your responses.
If you don't have relevant memories, acknowledge this and provide a general response."""
            
            # Construct the full prompt with memory context
            full_prompt = message
            if memory_context:
                full_prompt = f"{message}\n\n{memory_context}"
            
            # Try to generate response with provider's LLM
            try:
                if hasattr(self.provider, "llm") and self.provider.llm is not None:
                    response = self.provider.llm.generate_response(
                        prompt=full_prompt,
                        system_prompt=system_prompt
                    )
                    return response
                else:
                    # Fallback if LLM is not available
                    logger.warning("LLM provider not available for chat response")
                    return "I couldn't access my AI capabilities. Here's what I know from your memories:\n" + memory_context
            except Exception as llm_error:
                logger.error(f"LLM generation failed: {llm_error}")
                return f"I encountered an issue processing your request, but I found these memories that might be relevant:\n{memory_context}"
            
        except Exception as e:
            logger.error(f"Failed to chat with memory: {e}")
            return f"I couldn't process your request due to an error: {str(e)}"

    def rebuild_embeddings(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Rebuild embeddings for all memories in the database
        
        Args:
            user_id: Optional user ID to filter memories (if None, all memories are processed)
            
        Returns:
            Dictionary with rebuild statistics
        """
        try:
            # Connect to database
            from pathlib import Path
            
            # Determine database path
            if hasattr(self.provider, "db_path") and os.path.exists(self.provider.db_path):
                db_path = self.provider.db_path
            else:
                # Default path
                data_dir = Path.home() / ".config" / "cliche" / "memory"
                db_path = str(data_dir / "cliche_memories.db")
            
            # Query memories
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query
            sql = "SELECT id, content FROM memories"
            params = []
            
            if user_id:
                sql += " WHERE user_id = ?"
                params.append(user_id)
            
            # Execute query
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            conn.close()
            
            # Process memories in batches
            batch_size = 10
            total = len(rows)
            processed = 0
            successful = 0
            failed = 0
            
            logger.info(f"Starting embedding rebuild for {total} memories")
            
            for i in range(0, total, batch_size):
                batch = rows[i:i+batch_size]
                items = [(row['id'], row['content']) for row in batch]
                
                # Add embeddings in batch
                results = self.embedding_store.add_embeddings_batch(items)
                
                # Update statistics
                processed += len(batch)
                successful += sum(1 for r in results if r)
                failed += sum(1 for r in results if not r)
                
                # Log progress
                logger.info(f"Processed {processed}/{total} memories, {successful} successful, {failed} failed")
            
            return {
                "total": total,
                "processed": processed,
                "successful": successful,
                "failed": failed
            }
        except Exception as e:
            logger.error(f"Failed to rebuild embeddings: {e}")
            return {
                "total": 0,
                "processed": 0,
                "successful": 0,
                "failed": 0,
                "error": str(e)
            }
