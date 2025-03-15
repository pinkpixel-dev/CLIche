"""
CLIche Memory System - SQLite-based memory implementation.

This module provides a simple memory implementation that uses SQLite for storage
without the complexity of embeddings and vector search. It's designed to be reliable
and work consistently across all providers.

Made with ❤️ by Pink Pixel
"""
import os
import time
import uuid
import json
import sqlite3
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class CLIcheMemory:
    """
    SQLite-based memory system for CLIche.
    
    This class provides a memory system that uses SQLite for storage
    without the complexity of embeddings and vector search.
    """
    
    def __init__(self, config=None):
        """
        Initialize the memory system.
        
        Args:
            config: Configuration dictionary for the memory system
        """
        self.config = config or {}
        self.lock = threading.Lock()
        
        # Get memory configuration
        memory_config = self.config.config.get("memory", {}) if hasattr(self.config, "config") else self.config
        
        # Set up data directory
        self.data_dir = memory_config.get("data_dir", os.path.expanduser("~/.config/cliche/memory"))
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Set up SQLite database
        self.db_path = os.path.join(self.data_dir, "cliche_memories.db")
        
        # Check for old database file and migrate if needed
        old_db_path = os.path.join(self.data_dir, "simple_memories.db")
        if os.path.exists(old_db_path) and not os.path.exists(self.db_path):
            logger.info(f"Found old database at {old_db_path}, migrating to {self.db_path}")
            import shutil
            shutil.copy2(old_db_path, self.db_path)
            
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # User profile
        self.user_id = memory_config.get("user_id", "default")
        
        # Memory enabled
        self.enabled = memory_config.get("enabled", True)
        
        # Auto-memory
        self.auto_memory = memory_config.get("auto_memory", True)
        
        # Retention settings
        self.retention_days = memory_config.get("retention_days", 0)  # 0 = keep forever
        self.max_memories = memory_config.get("max_memories", 0)  # 0 = unlimited
        
        # Initialize database
        self._setup_database()
        
        # Provider name (for informational purposes)
        self.provider_name = memory_config.get("provider", self.config.config.get("provider", "default")) if hasattr(self.config, "config") else "default"
        
        logger.info(f"CLIche memory system initialized with user ID: {self.user_id}")
        
    def _setup_database(self):
        """Set up the SQLite database tables"""
        with self.lock:
            cursor = self.conn.cursor()
            
            # Create memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    updated_at INTEGER,
                    metadata TEXT
                )
            """)
            
            # Create tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id TEXT PRIMARY KEY,
                    memory_id TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
                )
            """)
            
            # Create search index on content
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                    id, content, user_id, 
                    content='memories', 
                    content_rowid='rowid'
                )
            """)
            
            # Create triggers to keep FTS index updated
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                    INSERT INTO memory_fts(id, content, user_id) VALUES (new.id, new.content, new.user_id);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
                    UPDATE memory_fts SET content = new.content WHERE id = new.id;
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                    DELETE FROM memory_fts WHERE id = old.id;
                END
            """)
            
            self.conn.commit()
    
    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a new memory.
        
        Args:
            content: Content to store
            metadata: Metadata for the memory
            
        Returns:
            ID of the new memory
        """
        if not self.enabled:
            logger.info("Memory system is disabled, not adding memory")
            return None
        
        metadata = metadata or {}
        
        # Generate a unique ID
        memory_id = str(uuid.uuid4())
        
        # Get current timestamp
        timestamp = int(time.time())
        
        # Prepare tags
        tags = []
        if "tags" in metadata:
            if isinstance(metadata["tags"], str):
                tags = [tag.strip() for tag in metadata["tags"].split(",") if tag.strip()]
            elif isinstance(metadata["tags"], list):
                tags = metadata["tags"]
        
        with self.lock:
            cursor = self.conn.cursor()
            
            # Insert memory
            cursor.execute(
                "INSERT INTO memories (id, content, user_id, timestamp, updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (memory_id, content, self.user_id, timestamp, timestamp, json.dumps(metadata))
            )
            
            # Insert tags
            for tag in tags:
                tag_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO tags (id, memory_id, tag) VALUES (?, ?, ?)",
                    (tag_id, memory_id, tag)
                )
            
            self.conn.commit()
            
        logger.info(f"Added memory with ID: {memory_id}")
        
        # Apply retention policy
        self._apply_retention_policy()
        
        return memory_id
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory as a dictionary, or None if not found
        """
        if not self.enabled:
            logger.info("Memory system is disabled, not retrieving memory")
            return None
        
        with self.lock:
            cursor = self.conn.cursor()
            
            # Get memory
            cursor.execute(
                "SELECT id, content, user_id, timestamp, updated_at, metadata FROM memories WHERE id = ?",
                (memory_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Get tags
            cursor.execute(
                "SELECT tag FROM tags WHERE memory_id = ?",
                (memory_id,)
            )
            tags = [tag[0] for tag in cursor.fetchall()]
            
            # Parse metadata
            metadata = json.loads(row[5]) if row[5] else {}
            metadata["tags"] = tags
            
            # Create memory dict
            memory = {
                "id": row[0],
                "content": row[1],
                "user_id": row[2],
                "timestamp": row[3],
                "updated_at": row[4],
                "metadata": metadata
            }
            
            return memory
    
    def search(self, query: str, limit: int = 5, semantic: bool = False) -> List[Dict[str, Any]]:
        """
        Search for memories.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            semantic: Whether to use semantic search (ignored in this implementation)
            
        Returns:
            List of matching memories
        """
        if not self.enabled:
            logger.info("Memory system is disabled, not searching for memories")
            return []
        
        with self.lock:
            cursor = self.conn.cursor()
            
            # Clean the query for FTS5: remove special characters or convert to simple search terms
            cleaned_query = self._clean_query_for_fts(query)
            
            fts_success = False
            rows = []
            
            if cleaned_query:
                # Use FTS to search for memories with similar content
                try:
                    cursor.execute(
                        """
                        SELECT m.id, m.content, m.user_id, m.timestamp, m.updated_at, m.metadata,
                            highlight(memory_fts, 0, '<mark>', '</mark>') as highlighted
                        FROM memory_fts
                        JOIN memories m ON memory_fts.id = m.id
                        WHERE memory_fts MATCH ? AND m.user_id = ?
                        ORDER BY rank
                        LIMIT ?
                        """,
                        (cleaned_query, self.user_id, limit)
                    )
                    
                    rows = cursor.fetchall()
                    if rows:
                        fts_success = True
                except sqlite3.OperationalError as e:
                    # Handle specific FTS errors silently
                    error_msg = str(e)
                    if "no such column" in error_msg or "syntax error" in error_msg:
                        logger.debug(f"FTS search failed with benign error: {error_msg}")
                    else:
                        # Log other operational errors but still fall back to LIKE search
                        logger.warning(f"FTS search failed: {e}. Falling back to LIKE search.")
                except Exception as e:
                    # Log other errors but still fall back
                    logger.warning(f"FTS search failed: {e}. Falling back to LIKE search.")
            
            # If no results from FTS or FTS failed, try a simple LIKE search
            if not fts_success:
                # Extract words from query and create LIKE patterns
                words = [w for w in query.split() if len(w) > 2]
                if not words:
                    words = query.split()
                
                like_patterns = []
                params = []
                
                for word in words:
                    like_patterns.append("content LIKE ?")
                    params.append(f"%{word}%")
                
                if not like_patterns:
                    like_patterns.append("content LIKE ?")
                    params.append(f"%{query}%")
                
                where_clause = " OR ".join(like_patterns)
                
                query_sql = f"""
                    SELECT id, content, user_id, timestamp, updated_at, metadata
                    FROM memories
                    WHERE ({where_clause}) AND user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                
                params.append(self.user_id)
                params.append(limit)
                
                cursor.execute(query_sql, params)
                rows = cursor.fetchall()
            
            # Build memories list
            memories = []
            for row in rows:
                memory_id = row[0]
                
                # Get tags
                cursor.execute(
                    "SELECT tag FROM tags WHERE memory_id = ?",
                    (memory_id,)
                )
                tags = [tag[0] for tag in cursor.fetchall()]
                
                # Parse metadata
                metadata = json.loads(row[5]) if row[5] else {}
                metadata["tags"] = tags
                
                # Create memory dict
                memory = {
                    "id": row[0],
                    "content": row[1],
                    "user_id": row[2],
                    "timestamp": row[3],
                    "updated_at": row[4],
                    "metadata": metadata
                }
                
                # Add highlighted content if available
                if len(row) > 6:
                    memory["highlighted"] = row[6]
                
                memories.append(memory)
            
            return memories
    
    def _clean_query_for_fts(self, query: str) -> str:
        """
        Clean a query string for FTS5 search.
        
        Args:
            query: Original query string
            
        Returns:
            Cleaned query suitable for FTS5
        """
        # Remove special characters that could cause FTS5 syntax errors
        
        # Remove all special characters
        special_chars = r'[?*^$():"~&|{}\[\]\\]'
        cleaned = re.sub(special_chars, ' ', query)
        
        # Split into words, keep words longer than 2 characters
        words = [word for word in cleaned.split() if len(word) > 2]
        
        # If no words left, return empty string
        if not words:
            return ""
        
        # Join with AND operator for better precision
        return " OR ".join(words)
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if memory was deleted, False otherwise
        """
        if not self.enabled:
            logger.info("Memory system is disabled, not deleting memory")
            return False
        
        with self.lock:
            # First check if memory exists
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM memories WHERE id = ? AND user_id = ?", (memory_id, self.user_id))
            if not cursor.fetchone():
                logger.warning(f"Memory {memory_id} not found or belongs to another user")
                return False
            
            # Delete memory (tags will be deleted via CASCADE)
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            self.conn.commit()
            
            return True
    
    def remove_memory(self, memory_id: str) -> bool:
        """
        Remove a memory by ID. This is an alias for delete() to maintain compatibility.
        
        Args:
            memory_id: ID of the memory to remove
            
        Returns:
            True if memory was removed, False otherwise
        """
        return self.delete(memory_id)
    
    def update(self, memory_id: str, content: str = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Update a memory by ID.
        
        Args:
            memory_id: ID of the memory to update
            content: New content (if None, content won't be updated)
            metadata: New metadata (if None, metadata won't be updated)
            
        Returns:
            True if memory was updated, False otherwise
        """
        if not self.enabled:
            logger.info("Memory system is disabled, not updating memory")
            return False
        
        with self.lock:
            cursor = self.conn.cursor()
            
            # Check if memory exists
            cursor.execute("SELECT content, metadata FROM memories WHERE id = ? AND user_id = ?", (memory_id, self.user_id))
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Memory {memory_id} not found or belongs to another user")
                return False
            
            # Get existing content and metadata
            existing_content = row[0]
            existing_metadata = json.loads(row[1]) if row[1] else {}
            
            # Prepare updates
            update_parts = []
            params = []
            
            # Update timestamp
            update_parts.append("updated_at = ?")
            params.append(int(time.time()))
            
            # Update content if provided
            if content is not None:
                update_parts.append("content = ?")
                params.append(content)
            else:
                content = existing_content
            
            # Update metadata if provided
            if metadata is not None:
                # Merge metadata
                combined_metadata = {**existing_metadata, **metadata}
                update_parts.append("metadata = ?")
                params.append(json.dumps(combined_metadata))
                
                # Handle tags if in metadata
                tags = []
                if "tags" in combined_metadata:
                    if isinstance(combined_metadata["tags"], str):
                        tags = [tag.strip() for tag in combined_metadata["tags"].split(",") if tag.strip()]
                    elif isinstance(combined_metadata["tags"], list):
                        tags = combined_metadata["tags"]
                
                # Delete existing tags
                cursor.execute("DELETE FROM tags WHERE memory_id = ?", (memory_id,))
                
                # Insert new tags
                for tag in tags:
                    tag_id = str(uuid.uuid4())
                    cursor.execute(
                        "INSERT INTO tags (id, memory_id, tag) VALUES (?, ?, ?)",
                        (tag_id, memory_id, tag)
                    )
            
            # If nothing to update, return success
            if not update_parts:
                return True
            
            # Build and execute update query
            query = f"UPDATE memories SET {', '.join(update_parts)} WHERE id = ?"
            params.append(memory_id)
            
            cursor.execute(query, params)
            self.conn.commit()
            
            return True
    
    def count(self) -> int:
        """
        Get count of memories for current user.
        
        Returns:
            Number of memories
        """
        if not self.enabled:
            logger.info("Memory system is disabled, not counting memories")
            return 0
        
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories WHERE user_id = ?", (self.user_id,))
            return cursor.fetchone()[0]
    
    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all memories for current user.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of memories
        """
        if not self.enabled:
            logger.info("Memory system is disabled, not retrieving memories")
            return []
        
        with self.lock:
            cursor = self.conn.cursor()
            
            # Get memories
            cursor.execute(
                """
                SELECT id, content, user_id, timestamp, updated_at, metadata
                FROM memories
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (self.user_id, limit)
            )
            
            rows = cursor.fetchall()
            
            # Build memories list
            memories = []
            for row in rows:
                memory_id = row[0]
                
                # Get tags
                cursor.execute(
                    "SELECT tag FROM tags WHERE memory_id = ?",
                    (memory_id,)
                )
                tags = [tag[0] for tag in cursor.fetchall()]
                
                # Parse metadata
                metadata = json.loads(row[5]) if row[5] else {}
                metadata["tags"] = tags
                
                # Create memory dict
                memory = {
                    "id": row[0],
                    "content": row[1],
                    "user_id": row[2],
                    "timestamp": row[3],
                    "updated_at": row[4],
                    "metadata": metadata
                }
                
                memories.append(memory)
            
            return memories
    
    def reset(self) -> bool:
        """
        Reset the memory system by clearing all memories.
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            cursor = self.conn.cursor()
            
            # Delete all memories for current user
            cursor.execute("DELETE FROM memories WHERE user_id = ?", (self.user_id,))
            self.conn.commit()
            
            return True
    
    def set_user_id(self, user_id: str) -> bool:
        """
        Set the user ID.
        
        Args:
            user_id: New user ID
            
        Returns:
            True if successful, False otherwise
        """
        if not user_id:
            logger.warning("User ID cannot be empty")
            return False
        
        self.user_id = user_id
        
        # Update config
        if hasattr(self.config, "config"):
            if "memory" not in self.config.config:
                self.config.config["memory"] = {}
            
            self.config.config["memory"]["user_id"] = user_id
            
            # Save config if possible
            if hasattr(self.config, "save_config"):
                self.config.save_config(self.config.config)
        
        logger.info(f"User ID set to: {user_id}")
        return True
    
    def set_auto_memory(self, enabled: bool) -> bool:
        """
        Enable or disable auto-memory.
        
        Args:
            enabled: Whether auto-memory should be enabled
            
        Returns:
            True if successful, False otherwise
        """
        self.auto_memory = enabled
        
        # Update config
        if hasattr(self.config, "config"):
            if "memory" not in self.config.config:
                self.config.config["memory"] = {}
            
            self.config.config["memory"]["auto_memory"] = enabled
            
            # Save config if possible
            if hasattr(self.config, "save_config"):
                self.config.save_config(self.config.config)
        
        logger.info(f"Auto-memory {'enabled' if enabled else 'disabled'}")
        return True
    
    def toggle(self, enabled: bool) -> bool:
        """
        Enable or disable the memory system.
        
        Args:
            enabled: Whether memory should be enabled
            
        Returns:
            True if successful, False otherwise
        """
        self.enabled = enabled
        
        # Update config
        if hasattr(self.config, "config"):
            if "memory" not in self.config.config:
                self.config.config["memory"] = {}
            
            self.config.config["memory"]["enabled"] = enabled
            
            # Save config if possible
            if hasattr(self.config, "save_config"):
                self.config.save_config(self.config.config)
        
        logger.info(f"Memory system {'enabled' if enabled else 'disabled'}")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get memory system status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "enabled": self.enabled,
            "auto_memory": self.auto_memory,
            "user_id": self.user_id,
            "memory_count": self.count(),
            "data_dir": self.data_dir,
            "db_path": self.db_path,
            "provider": self.provider_name,
            "retention_days": self.retention_days,
            "max_memories": self.max_memories,
        }
    
    def _apply_retention_policy(self):
        """Apply retention policy by deleting old memories if needed"""
        # Apply max_memories limit if set
        if self.max_memories > 0:
            with self.lock:
                cursor = self.conn.cursor()
                
                # Get count of memories
                cursor.execute("SELECT COUNT(*) FROM memories WHERE user_id = ?", (self.user_id,))
                count = cursor.fetchone()[0]
                
                if count > self.max_memories:
                    # Get oldest memories to delete
                    cursor.execute(
                        """
                        SELECT id FROM memories 
                        WHERE user_id = ? 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                        """,
                        (self.user_id, count - self.max_memories)
                    )
                    
                    to_delete = [row[0] for row in cursor.fetchall()]
                    
                    # Delete memories
                    for memory_id in to_delete:
                        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                    
                    self.conn.commit()
                    logger.info(f"Deleted {len(to_delete)} memories due to max_memories limit")
        
        # Apply retention_days limit if set
        if self.retention_days > 0:
            with self.lock:
                cursor = self.conn.cursor()
                
                # Calculate cutoff timestamp
                cutoff = int(time.time()) - (self.retention_days * 24 * 60 * 60)
                
                # Delete memories older than cutoff
                cursor.execute(
                    "DELETE FROM memories WHERE user_id = ? AND timestamp < ?",
                    (self.user_id, cutoff)
                )
                
                deleted = cursor.rowcount
                self.conn.commit()
                
                if deleted > 0:
                    logger.info(f"Deleted {deleted} memories due to retention_days limit")
    
    def detect_memory_request(self, message: str) -> Tuple[bool, Optional[str], Optional[List[str]]]:
        """
        Detect if a message is requesting to store a memory.
        
        Args:
            message: Message to analyze
            
        Returns:
            Tuple of (is_memory_request, memory_content, memory_tags)
        """
        message_lower = message.lower()
        memory_terms = [
            "remember this",
            "remember that",
            "make a memory",
            "create a memory",
            "save this",
            "save that",
            "save progress",
            "record progress",
            "log memory",
            "enter memory",
            "create a save",
            "new save",
        ]
        
        is_memory_request = any(term in message_lower for term in memory_terms)
        
        if not is_memory_request:
            return (False, None, None)
        
        # Simple extraction - just use the whole message as content
        memory_content = message
        memory_tags = []
        
        return (True, memory_content, memory_tags)
    
    def detect_preference(self, message: str) -> Tuple[bool, Optional[str], Optional[List[str]]]:
        """
        Detect if a message contains user preferences.
        
        Args:
            message: Message to analyze
            
        Returns:
            Tuple of (is_preference, preference_content, preference_tags)
        """
        message_lower = message.lower()
        preference_terms = [
            "i like",
            "i love",
            "i prefer",
            "i enjoy",
            "i don't like",
            "i hate",
            "i dislike",
            "my favorite",
            "i'm a fan of",
        ]
        
        is_preference = any(term in message_lower for term in preference_terms)
        
        if not is_preference:
            return (False, None, None)
        
        # Simple extraction - just use the whole message as content
        preference_content = message
        preference_tags = ["preference"]
        
        return (True, preference_content, preference_tags)
    
    def repair_database(self) -> bool:
        """
        Repair the database by rebuilding the FTS index.
        This fixes 'database disk image is malformed' errors.
        
        Returns:
            True if repair was successful, False otherwise
        """
        logger.info("Repairing memory database by rebuilding FTS index")
        
        with self.lock:
            try:
                cursor = self.conn.cursor()
                
                # Drop the FTS table if it exists
                cursor.execute("DROP TABLE IF EXISTS memory_fts")
                
                # Recreate the FTS table
                cursor.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                        id, content, user_id, 
                        content='memories', 
                        content_rowid='rowid'
                    )
                """)
                
                # Recreate the triggers
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                        INSERT INTO memory_fts(id, content, user_id) VALUES (new.id, new.content, new.user_id);
                    END
                """)
                
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
                        UPDATE memory_fts SET content = new.content WHERE id = new.id;
                    END
                """)
                
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                        DELETE FROM memory_fts WHERE id = old.id;
                    END
                """)
                
                # Repopulate the FTS table with existing memories
                cursor.execute("""
                    INSERT INTO memory_fts(id, content, user_id)
                    SELECT id, content, user_id FROM memories
                """)
                
                self.conn.commit()
                logger.info("Database repair completed successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error repairing database: {str(e)}")
                self.conn.rollback()
                return False

    def auto_add(self, message: str, response: str) -> Optional[str]:
        """
        Automatically add a message and response as a memory.
        
        Args:
            message: The user's message/query
            response: The AI's response
            
        Returns:
            ID of the new memory if created, None otherwise
        """
        if not self.enabled or not self.auto_memory:
            logger.debug("Auto-memory disabled, not adding memory")
            return None
            
        try:
            # Store the interaction as a memory
            memory_id = self.add(message, {
                "type": "interaction",
                "response": response,
                "timestamp": int(time.time())
            })
            
            logger.debug(f"Auto-added memory with ID: {memory_id}")
            return memory_id
        except Exception as e:
            logger.error(f"Failed to auto-add memory: {str(e)}")
            return None
    
    def close(self):
        """Close the database connection"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close() 