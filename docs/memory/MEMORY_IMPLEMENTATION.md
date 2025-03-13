# CLIche Memory Implementation

## Overview

This document outlines the implementation of the core Memory class for CLIche, which ties together the embedding providers and vector stores for a complete memory management system. Based on the mem0 project's clean architecture, this implementation provides a single, unified interface for all memory operations.

## Memory Class Design

The Memory class serves as the central component of the memory system, coordinating between embedding providers and vector stores. It handles:

1. Memory storage and retrieval
2. Semantic search
3. Metadata filtering
4. Memory management operations (update, delete)

## Implementation

### Memory Configuration

```python
# cliche/memory/config.py

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import os

@dataclass
class EmbeddingConfig:
    """Configuration for embedding providers"""
    provider: str = "ollama"  # Default to ollama
    model: str = "nomic-embed-text"  # Default model
    api_key: Optional[str] = None
    dimensions: Optional[int] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VectorStoreConfig:
    """Configuration for vector stores"""
    provider: str = "chroma"  # Default to ChromaDB
    collection_name: str = "cliche_memories"
    persistent_path: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MemoryConfig:
    """Configuration for the memory system"""
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    data_dir: str = field(default_factory=lambda: os.path.expanduser("~/.config/cliche/memory"))
    user_profile: str = "default"
    enabled: bool = True
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'MemoryConfig':
        """Create a MemoryConfig from a dictionary"""
        embedding_dict = config_dict.get("embedding", {})
        embedding_config = EmbeddingConfig(
            provider=embedding_dict.get("provider", "ollama"),
            model=embedding_dict.get("model", "nomic-embed-text"),
            api_key=embedding_dict.get("api_key"),
            dimensions=embedding_dict.get("dimensions"),
            additional_params=embedding_dict.get("additional_params", {})
        )
        
        vector_store_dict = config_dict.get("vector_store", {})
        vector_store_config = VectorStoreConfig(
            provider=vector_store_dict.get("provider", "chroma"),
            collection_name=vector_store_dict.get("collection_name", "cliche_memories"),
            persistent_path=vector_store_dict.get("persistent_path"),
            host=vector_store_dict.get("host"),
            port=vector_store_dict.get("port"),
            additional_params=vector_store_dict.get("additional_params", {})
        )
        
        return cls(
            embedding=embedding_config,
            vector_store=vector_store_config,
            data_dir=config_dict.get("data_dir", os.path.expanduser("~/.config/cliche/memory")),
            user_profile=config_dict.get("user_profile", "default"),
            enabled=config_dict.get("enabled", True)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert MemoryConfig to a dictionary"""
        return {
            "embedding": {
                "provider": self.embedding.provider,
                "model": self.embedding.model,
                "api_key": self.embedding.api_key,
                "dimensions": self.embedding.dimensions,
                "additional_params": self.embedding.additional_params
            },
            "vector_store": {
                "provider": self.vector_store.provider,
                "collection_name": self.vector_store.collection_name,
                "persistent_path": self.vector_store.persistent_path,
                "host": self.vector_store.host,
                "port": self.vector_store.port,
                "additional_params": self.vector_store.additional_params
            },
            "data_dir": self.data_dir,
            "user_profile": self.user_profile,
            "enabled": self.enabled
        }
```

### Memory Class Implementation

```python
# cliche/memory/memory.py

import os
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple

from .config import MemoryConfig
from .embeddings.factory import EmbeddingProviderFactory
from .vector_stores.factory import VectorStoreFactory

logger = logging.getLogger(__name__)

class Memory:
    """CLIche Memory System"""
    
    def __init__(self, config: Optional[Union[Dict[str, Any], MemoryConfig]] = None):
        """
        Initialize the memory system
        
        Args:
            config: Memory configuration
        """
        # Handle configuration
        if config is None:
            self.config = MemoryConfig()
        elif isinstance(config, dict):
            self.config = MemoryConfig.from_dict(config)
        else:
            self.config = config
            
        # Create data directory if it doesn't exist
        os.makedirs(self.config.data_dir, exist_ok=True)
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embedding provider and vector store"""
        if not self.config.enabled:
            logger.info("Memory system is disabled")
            self.embedding_provider = None
            self.vector_store = None
            return
        
        try:
            # Create embedding provider
            self.embedding_provider = EmbeddingProviderFactory.create(
                self.config.embedding.provider,
                {
                    "model": self.config.embedding.model,
                    "api_key": self.config.embedding.api_key,
                    "dimensions": self.config.embedding.dimensions,
                    **self.config.embedding.additional_params
                }
            )
            
            # Create vector store
            collection_name = f"{self.config.vector_store.collection_name}_{self.config.user_profile}"
            
            vector_store_params = {
                "collection_name": collection_name,
                "persistent_path": self.config.vector_store.persistent_path or os.path.join(self.config.data_dir, "chroma"),
                "host": self.config.vector_store.host,
                "port": self.config.vector_store.port,
                "dimensions": self.embedding_provider.get_dimensions(),
                **self.config.vector_store.additional_params
            }
            
            self.vector_store = VectorStoreFactory.create(
                self.config.vector_store.provider,
                vector_store_params
            )
            
            logger.info(f"Memory system initialized for user profile: {self.config.user_profile}")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory system: {str(e)}")
            self.embedding_provider = None
            self.vector_store = None
            raise
    
    @property
    def is_enabled(self) -> bool:
        """Check if memory system is enabled"""
        return self.config.enabled and self.embedding_provider is not None and self.vector_store is not None
    
    def enable(self):
        """Enable memory system"""
        if not self.config.enabled:
            self.config.enabled = True
            self._initialize_components()
    
    def disable(self):
        """Disable memory system"""
        self.config.enabled = False
        self.embedding_provider = None
        self.vector_store = None
    
    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Add a memory
        
        Args:
            content: Content to add
            metadata: Metadata for the memory
            
        Returns:
            Memory ID if successful, None otherwise
        """
        if not self.is_enabled:
            logger.warning("Memory system is disabled, memory not added")
            return None
        
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            # Add timestamps and user profile
            metadata["created_at"] = int(time.time())
            metadata["updated_at"] = int(time.time())
            metadata["user_profile"] = self.config.user_profile
            
            # Generate embedding
            embedding = self.embedding_provider.embed(content, action="add")
            
            # Add to vector store
            memory_id = self.vector_store.add(content, embedding, metadata)
            
            logger.info(f"Added memory with ID: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to add memory: {str(e)}")
            return None
    
    def search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for memories similar to the query
        
        Args:
            query: Search query
            limit: Maximum number of results
            filters: Metadata filters
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of matching memories
        """
        if not self.is_enabled:
            logger.warning("Memory system is disabled, returning empty search results")
            return []
        
        try:
            # Generate embedding
            query_embedding = self.embedding_provider.embed(query, action="search")
            
            # Add user profile filter if not specified
            if filters is None:
                filters = {}
            
            if "user_profile" not in filters:
                filters["user_profile"] = self.config.user_profile
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding,
                limit=limit,
                filter_metadata=filters,
                min_similarity=min_similarity
            )
            
            logger.info(f"Search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search memories: {str(e)}")
            return []
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by ID
        
        Args:
            memory_id: Memory ID
            
        Returns:
            Memory if found, None otherwise
        """
        if not self.is_enabled:
            logger.warning("Memory system is disabled, memory not retrieved")
            return None
        
        try:
            # Get from vector store
            memory = self.vector_store.get(memory_id)
            
            # Verify memory belongs to current user profile
            if memory and memory.get("metadata", {}).get("user_profile") != self.config.user_profile:
                logger.warning(f"Memory {memory_id} belongs to a different user profile")
                return None
            
            return memory
            
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {str(e)}")
            return None
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: Memory ID
            
        Returns:
            True if memory was deleted, False otherwise
        """
        if not self.is_enabled:
            logger.warning("Memory system is disabled, memory not deleted")
            return False
        
        try:
            # Verify memory belongs to current user profile
            memory = self.get(memory_id)
            if not memory:
                return False
            
            # Delete from vector store
            return self.vector_store.delete(memory_id)
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {str(e)}")
            return False
    
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a memory
        
        Args:
            memory_id: Memory ID
            content: New content
            metadata: New metadata
            
        Returns:
            True if memory was updated, False otherwise
        """
        if not self.is_enabled:
            logger.warning("Memory system is disabled, memory not updated")
            return False
        
        try:
            # Verify memory belongs to current user profile
            memory = self.get(memory_id)
            if not memory:
                return False
            
            # Generate embedding if content is provided
            embedding = None
            if content is not None:
                embedding = self.embedding_provider.embed(content, action="update")
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            # Set updated timestamp
            metadata["updated_at"] = int(time.time())
            
            # Update memory
            return self.vector_store.update(memory_id, content, embedding, metadata)
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {str(e)}")
            return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count memories
        
        Args:
            filters: Metadata filters
            
        Returns:
            Number of memories
        """
        if not self.is_enabled:
            logger.warning("Memory system is disabled, returning 0 count")
            return 0
        
        try:
            # Add user profile filter if not specified
            if filters is None:
                filters = {}
            
            if "user_profile" not in filters:
                filters["user_profile"] = self.config.user_profile
            
            # Count memories
            return self.vector_store.count(filters)
            
        except Exception as e:
            logger.error(f"Failed to count memories: {str(e)}")
            return 0
    
    def status(self) -> Dict[str, Any]:
        """
        Get memory system status
        
        Returns:
            Status information
        """
        status = {
            "enabled": self.is_enabled,
            "user_profile": self.config.user_profile,
            "memory_count": 0,
            "embedding_provider": {
                "name": self.config.embedding.provider,
                "model": self.config.embedding.model,
            },
            "vector_store": {
                "name": self.config.vector_store.provider,
                "collection": f"{self.config.vector_store.collection_name}_{self.config.user_profile}",
            }
        }
        
        if self.is_enabled:
            try:
                status["memory_count"] = self.count()
            except Exception as e:
                logger.error(f"Failed to get memory count: {str(e)}")
        
        return status
    
    def set_user_profile(self, user_profile: str):
        """
        Set user profile
        
        Args:
            user_profile: User profile name
        """
        if user_profile == self.config.user_profile:
            return
        
        self.config.user_profile = user_profile
        
        # Reinitialize components
        if self.config.enabled:
            self._initialize_components()
```

## CLI Commands Implementation

Below is a sample implementation of the CLI commands for the memory system:

```python
# cliche/cli/commands/memory.py

import typer
import json
from typing import Optional, List, Dict, Any
import logging

from cliche.memory.memory import Memory
from cliche.memory.config import MemoryConfig
from cliche.memory.migration import migrate_sqlite_to_chroma
from cliche.utils.config import get_config, save_config

app = typer.Typer(name="memory", help="Memory management commands")
logger = logging.getLogger(__name__)

# Get memory instance
def get_memory():
    """Get memory instance from config"""
    config = get_config()
    memory_config = config.get("memory", {})
    return Memory(memory_config)

@app.command("status")
def status():
    """Show memory system status"""
    memory = get_memory()
    status = memory.status()
    
    typer.echo("\n📝 Memory System Status")
    typer.echo(f"Enabled: {'✅' if status['enabled'] else '❌'}")
    typer.echo(f"User profile: {status['user_profile']}")
    
    if status['enabled']:
        typer.echo(f"Memory count: {status['memory_count']}")
        typer.echo(f"Embedding provider: {status['embedding_provider']['name']} ({status['embedding_provider']['model']})")
        typer.echo(f"Vector store: {status['vector_store']['name']} ({status['vector_store']['collection']})")

@app.command("enable")
def enable():
    """Enable memory system"""
    config = get_config()
    memory_config = config.get("memory", {})
    memory_config["enabled"] = True
    config["memory"] = memory_config
    save_config(config)
    
    typer.echo("Memory system enabled ✅")

@app.command("disable")
def disable():
    """Disable memory system"""
    config = get_config()
    memory_config = config.get("memory", {})
    memory_config["enabled"] = False
    config["memory"] = memory_config
    save_config(config)
    
    typer.echo("Memory system disabled ❌")

@app.command("set-profile")
def set_profile(profile_name: str):
    """Set user profile for memory system"""
    config = get_config()
    memory_config = config.get("memory", {})
    memory_config["user_profile"] = profile_name
    config["memory"] = memory_config
    save_config(config)
    
    typer.echo(f"User profile set to: {profile_name}")

@app.command("remember")
def remember(
    content: str = typer.Argument(..., help="Content to remember"),
    tag: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags for the memory")
):
    """Add new memory"""
    memory = get_memory()
    
    if not memory.is_enabled:
        typer.echo("Memory system is disabled. Enable it with 'cliche memory enable'")
        return
    
    # Prepare metadata
    metadata = {}
    if tag:
        metadata["tags"] = tag
    
    # Add to memory
    memory_id = memory.add(content, metadata)
    
    if memory_id:
        typer.echo(f"Memory added with ID: {memory_id} ✅")
    else:
        typer.echo("Failed to add memory ❌")

@app.command("recall")
def recall(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(5, "--limit", "-l", help="Maximum number of results"),
    tag: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Filter by tags"),
    min_similarity: float = typer.Option(0.0, "--min-similarity", "-m", help="Minimum similarity threshold (0-1)")
):
    """Search memories"""
    memory = get_memory()
    
    if not memory.is_enabled:
        typer.echo("Memory system is disabled. Enable it with 'cliche memory enable'")
        return
    
    # Prepare filters
    filters = {}
    if tag:
        filters["tags"] = {"$in": tag}
    
    # Search memories
    results = memory.search(query, limit=limit, filters=filters, min_similarity=min_similarity)
    
    if not results:
        typer.echo("No memories found matching the query.")
        return
    
    typer.echo(f"\n🔍 Found {len(results)} memories:\n")
    
    for i, result in enumerate(results):
        similarity = result.get("similarity", None)
        similarity_str = f" (Similarity: {similarity:.2f})" if similarity is not None else ""
        
        typer.echo(f"{i+1}. [{result['id']}]{similarity_str}")
        typer.echo(f"   {result['content']}")
        
        # Show tags if present
        tags = result.get("metadata", {}).get("tags", None)
        if tags:
            typer.echo(f"   Tags: {', '.join(tags)}")
        
        typer.echo("")

@app.command("forget")
def forget(memory_id: str):
    """Delete a memory by ID"""
    memory = get_memory()
    
    if not memory.is_enabled:
        typer.echo("Memory system is disabled. Enable it with 'cliche memory enable'")
        return
    
    # Get memory first to verify it exists
    mem = memory.get(memory_id)
    if not mem:
        typer.echo(f"Memory with ID {memory_id} not found.")
        return
    
    # Delete memory
    if memory.delete(memory_id):
        typer.echo(f"Memory {memory_id} deleted ✅")
    else:
        typer.echo(f"Failed to delete memory {memory_id} ❌")

@app.command("show")
def show(memory_id: str):
    """Show a memory by ID"""
    memory = get_memory()
    
    if not memory.is_enabled:
        typer.echo("Memory system is disabled. Enable it with 'cliche memory enable'")
        return
    
    # Get memory
    mem = memory.get(memory_id)
    if not mem:
        typer.echo(f"Memory with ID {memory_id} not found.")
        return
    
    # Display memory
    typer.echo(f"\n📝 Memory {memory_id}")
    typer.echo(f"Content: {mem['content']}")
    
    # Show metadata
    metadata = mem.get("metadata", {})
    
    if "created_at" in metadata:
        import datetime
        created_at = datetime.datetime.fromtimestamp(metadata["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
        typer.echo(f"Created: {created_at}")
    
    if "tags" in metadata:
        typer.echo(f"Tags: {', '.join(metadata['tags'])}")
    
    # Show other metadata
    other_metadata = {k: v for k, v in metadata.items() if k not in ["created_at", "updated_at", "user_profile", "tags"]}
    if other_metadata:
        typer.echo("\nAdditional Metadata:")
        for key, value in other_metadata.items():
            typer.echo(f"  {key}: {value}")

@app.command("migrate")
def migrate(
    confirm: bool = typer.Option(False, "--confirm", help="Confirm migration without prompting")
):
    """Migrate memories from SQLite to ChromaDB"""
    if not confirm:
        confirm = typer.confirm("This will migrate all memories from SQLite to ChromaDB. Continue?")
        if not confirm:
            typer.echo("Migration cancelled.")
            return
    
    config = get_config()
    memory_config = config.get("memory", {})
    
    # Ensure memory system is enabled for migration
    was_enabled = memory_config.get("enabled", True)
    memory_config["enabled"] = True
    
    migrated, total = migrate_sqlite_to_chroma(memory_config)
    
    # Restore original enabled state
    memory_config["enabled"] = was_enabled
    config["memory"] = memory_config
    save_config(config)
    
    if total == 0:
        typer.echo("No memories found in SQLite database.")
    else:
        typer.echo(f"Migration complete: {migrated} of {total} memories migrated to ChromaDB.")
```

## Memory CLI Usage Examples

```
# Show memory system status
cliche memory status

# Add a new memory
cliche memory remember "The capital of France is Paris" --tag geography --tag europe

# Search memories
cliche memory recall "capital of France" --limit 3 --min-similarity 0.7

# Search with tag filter
cliche memory recall "capital" --tag geography

# Show a specific memory
cliche memory show abc123def456

# Delete a memory
cliche memory forget abc123def456  

# Change user profile
cliche memory set-profile work

# Migrate memories from SQLite to ChromaDB
cliche memory migrate --confirm
```

## Integration with Chat and Ask Commands

The memory system can be integrated with the chat and ask commands to provide context from memories:

```python
# cliche/cli/commands/chat.py (excerpt)

def get_context_from_memories(query, limit=3):
    """Get context from memories for the chat/ask commands"""
    memory = get_memory()
    
    if not memory.is_enabled:
        return []
    
    # Search for relevant memories
    results = memory.search(query, limit=limit, min_similarity=0.7)
    
    # Format as context
    context = []
    for result in results:
        context.append({
            "role": "system",
            "content": f"Relevant memory: {result['content']}"
        })
    
    return context

@app.command()
def chat():
    """Start an interactive chat session"""
    # ... existing code ...
    
    # Add memories to context
    if query:
        memory_context = get_context_from_memories(query)
        context.extend(memory_context)
    
    # ... rest of chat implementation ...
```

## Key Features

1. **User Profiles**: Support for multiple user profiles with separate collections
2. **Metadata Support**: Comprehensive metadata handling with filtering
3. **Clean API**: Simple interface for adding, retrieving, and searching memories
4. **Error Handling**: Robust error handling and logging
5. **CLI Integration**: Complete set of CLI commands for memory management
6. **Migration**: Tools for migrating from the old SQLite system

## Conclusion

This memory system implementation provides a clean, modular architecture based on the mem0 project. By using ChromaDB as the single storage backend and supporting multiple embedding providers, it offers significant improvements in reliability, flexibility, and usability over the previous dual-storage approach.

The design makes it easy to extend with additional vector stores or embedding providers in the future, while maintaining a consistent API for the rest of the application. 