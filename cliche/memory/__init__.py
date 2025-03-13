"""
Memory module for CLIche.

This module provides memory capabilities for CLIche, allowing it to remember information
across sessions and interactions.

Made with ❤️ by Pink Pixel
"""
import logging
import os
from typing import Dict, Any, List, Optional, Tuple
import uuid

# Set up logging
logger = logging.getLogger(__name__)

# Import configuration classes
from .config import (
    MemoryConfig, 
    BaseEmbeddingConfig, 
    OllamaEmbeddingConfig,
    OpenAIEmbeddingConfig,
    VectorStoreConfig
)

# Import factory classes
from .factory import EmbeddingProviderFactory, VectorStoreFactory

# Import base classes
from .embeddings.base import BaseEmbeddingProvider
from .vector_stores.base import BaseVectorStore

# Import memory manager
from .manager import MemoryManager

# Log information about the memory system
logger.info("CLIche memory system initialized")

# CLIcheMemory class that adapts MemoryManager to provide backward compatibility
class CLIcheMemory:
    """
    Memory system for CLIche.
    
    This class provides a backward-compatible interface for the memory system,
    while using the new MemoryManager under the hood.
    """
    
    def __init__(self, config):
        """
        Initialize the CLIche memory system
        
        Args:
            config: CLIche configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get memory configuration from CLIche config
        memory_config = config.config.get("memory", {})
        
        # Set up basic settings from config
        self.enabled = memory_config.get("enabled", True)
        self.provider_name = memory_config.get("provider", config.config.get("provider", "openai"))
        self.data_dir = memory_config.get("data_dir", os.path.join(config.config_dir, "memory"))
        self.collection_name = memory_config.get("collection_name", "cliche_memories")
        self.user_id = memory_config.get("user_id", "default_user")
        self.auto_memory = memory_config.get("auto_memory", True)
        
        # Create memory config for new memory system
        if self.provider_name == "ollama":
            embedding_config = OllamaEmbeddingConfig(
                provider="ollama",
                model_name="nomic-embed-text",
                dimensions=768,
                host="http://localhost:11434"
            )
        else:
            embedding_config = OpenAIEmbeddingConfig(
                provider="openai",
                model_name="text-embedding-3-small",
                dimensions=1536,
                api_key=config.config.get("api_keys", {}).get(self.provider_name)
            )
        
        vector_store_config = VectorStoreConfig(
            provider="chroma",
            collection_name=self.collection_name,
            dimensions=embedding_config.dimensions,
            persist_directory=os.path.join(self.data_dir, "chroma")
        )
        
        memory_config = MemoryConfig(
            embedding=embedding_config,
            vector_store=vector_store_config,
            enabled=self.enabled,
            auto_memory=self.auto_memory,
            user_id=self.user_id,
            data_dir=self.data_dir
        )
        
        # Initialize the memory manager
        try:
            self.manager = MemoryManager(memory_config)
            self.logger.info("Memory system initialized with new MemoryManager")
        except Exception as e:
            self.logger.error(f"Failed to initialize memory manager: {e}")
            self.manager = None
    
    @property
    def enhanced_memory(self):
        """Enhanced memory property (for backward compatibility)"""
        return None
    
    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Add a memory
        
        Args:
            content: Memory content
            metadata: Memory metadata
            
        Returns:
            Memory ID if successful, None otherwise
        """
        if not self.enabled or not self.manager or not self.manager.is_ready():
            self.logger.warning("Memory system not ready or disabled")
            return None
        
        try:
            # Create default metadata if none provided
            if metadata is None:
                metadata = {
                    "user_id": self.user_id,
                    "timestamp": str(uuid.uuid4()),
                    "type": "user_memory"
                }
            
            # Add the memory
            memory_id = self.manager.add_memory(content, metadata)
            self.logger.info(f"Added memory with ID: {memory_id}")
            return memory_id
        except Exception as e:
            self.logger.error(f"Failed to add memory: {e}")
            return None
    
    def search(self, query: str, limit: int = 5, semantic: bool = True) -> List[Dict[str, Any]]:
        """
        Search for memories
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            semantic: Whether to use semantic search
            
        Returns:
            List of memories
        """
        if not self.enabled or not self.manager or not self.manager.is_ready():
            self.logger.warning("Memory system not ready or disabled")
            return []
        
        try:
            # Always use semantic search for now
            results = self.manager.search_memories(query, limit=limit)
            self.logger.info(f"Found {len(results)} memories for query: {query}")
            return results
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []
    
    def enhance_with_memories(self, message: str) -> str:
        """
        Enhance a message with memories (for backward compatibility)
        
        Args:
            message: Message to enhance
            
        Returns:
            Enhanced message
        """
        # For now, just return the original message
        return message
    
    def chat_with_memory(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Chat with memory (for backward compatibility)
        
        Args:
            message: User message
            system_prompt: System prompt
            
        Returns:
            Response from the assistant
        """
        # For now, just return a stub message
        return "Memory-enhanced chat is being rebuilt with the new memory system."
    
    def toggle(self, enabled: bool) -> bool:
        """
        Toggle memory system
        
        Args:
            enabled: Whether to enable or disable the memory system
            
        Returns:
            New state
        """
        self.enabled = enabled
        
        # Update the config
        memory_config = self.config.config.get("memory", {})
        memory_config["enabled"] = enabled
        self.config.config["memory"] = memory_config
        self.config.save_config(self.config.config)
        
        return self.enabled
    
    def set_auto_memory(self, enabled: bool) -> bool:
        """
        Set auto-memory
        
        Args:
            enabled: Whether to enable or disable auto-memory
            
        Returns:
            New state
        """
        try:
            self.auto_memory = enabled
            
            # Update the config
            memory_config = self.config.config.get("memory", {})
            memory_config["auto_memory"] = enabled
            self.config.config["memory"] = memory_config
            
            # Try to save the config but don't return False if it fails
            # This allows the auto-memory state to be set in memory even if saving to disk fails
            try:
                self.config.save_config(self.config.config)
            except Exception as e:
                self.logger.warning(f"Warning: Failed to save config when setting auto-memory: {e}")
                # We continue anyway since the auto-memory state is set in memory
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting auto-memory: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get memory status
        
        Returns:
            Dictionary with memory status
        """
        status = {
            "enabled": self.enabled,
            "auto_memory": self.auto_memory,
            "user_id": self.user_id,
            "provider": self.provider_name,
            "collection": self.collection_name,
            "data_dir": self.data_dir,
            "ready": (self.manager is not None and self.manager.is_ready()),
        }
        
        # Add count if manager is ready
        if self.manager and self.manager.is_ready():
            try:
                status["memory_count"] = self.manager.count_memories()
            except Exception:
                status["memory_count"] = 0
        else:
            status["memory_count"] = 0
            
        return status
    
    def remove_memory(self, memory_id: str) -> bool:
        """
        Remove memory by ID
        
        Args:
            memory_id: Memory ID
            
        Returns:
            Success flag
        """
        if not self.enabled or not self.manager or not self.manager.is_ready():
            self.logger.warning("Memory system not ready or disabled")
            return False
        
        try:
            # Delete the memory
            success = self.manager.delete_memory(memory_id)
            
            if success:
                self.logger.info(f"Deleted memory with ID: {memory_id}")
            else:
                self.logger.warning(f"Failed to delete memory with ID: {memory_id}")
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to remove memory: {e}")
            return False
    
    def clear_memories(self) -> bool:
        """
        Clear all memories
        
        Returns:
            Success status
        """
        if not self.enabled or not self.manager or not self.manager.is_ready():
            self.logger.warning("Memory system not ready or disabled")
            return False
        
        try:
            success = self.manager.clear_memories()
            if success:
                self.logger.info("All memories cleared")
            return success
        except Exception as e:
            self.logger.error(f"Failed to clear memories: {e}")
            return False
            
    def set_user_id(self, user_id: str) -> bool:
        """
        Set user ID
        
        Args:
            user_id: New user ID
            
        Returns:
            Success status
        """
        if not self.enabled:
            self.logger.warning("Memory system is disabled")
            return False
        
        try:
            self.user_id = user_id
            
            # Update the config
            memory_config = self.config.config.get("memory", {})
            memory_config["user_id"] = user_id
            self.config.config["memory"] = memory_config
            
            # Try to save the config but don't return False if it fails
            # This allows the user ID to be set in memory even if saving to disk fails
            try:
                self.config.save_config(self.config.config)
            except Exception as e:
                self.logger.warning(f"Warning: Failed to save config when setting user ID: {e}")
                # We continue anyway since the user ID is set in memory
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to set user ID: {e}")
            return False
    
    def set_profile_field(self, field: str, value: Any) -> bool:
        """
        Set a field in the user profile
        
        Args:
            field: Field name
            value: Field value
            
        Returns:
            Success status
        """
        if not self.enabled or not self.manager or not self.manager.is_ready():
            self.logger.warning("Memory system not ready or disabled")
            return False
        
        try:
            success = self.manager.set_profile_field(self.user_id, field, value)
            return success
        except Exception as e:
            self.logger.error(f"Failed to set profile field: {e}")
            return False
    
    def get_profile_field(self, field: str) -> Any:
        """
        Get a field from the user profile
        
        Args:
            field: Field name
            
        Returns:
            Field value
        """
        if not self.enabled or not self.manager or not self.manager.is_ready():
            self.logger.warning("Memory system not ready or disabled")
            return None
        
        try:
            value = self.manager.get_profile_field(self.user_id, field)
            return value
        except Exception as e:
            self.logger.error(f"Failed to get profile field: {e}")
            return None
    
    def get_profile(self) -> Dict[str, Any]:
        """
        Get the entire user profile
        
        Returns:
            User profile dictionary
        """
        if not self.enabled or not self.manager or not self.manager.is_ready():
            self.logger.warning("Memory system not ready or disabled")
            return {}
        
        try:
            profile = self.manager.get_profile(self.user_id)
            return profile or {}
        except Exception as e:
            self.logger.error(f"Failed to get profile: {e}")
            return {}
    
    def clear_profile(self) -> bool:
        """
        Clear the user profile
        
        Returns:
            Success status
        """
        if not self.enabled or not self.manager or not self.manager.is_ready():
            self.logger.warning("Memory system not ready or disabled")
            return False
        
        try:
            success = self.manager.clear_profile(self.user_id)
            return success
        except Exception as e:
            self.logger.error(f"Failed to clear profile: {e}")
            return False
            
    def extract_memories(self, limit: int = 10) -> List[str]:
        """
        Extract memories from recent conversations
        
        Args:
            limit: Maximum number of memories to extract
            
        Returns:
            List of extracted memories
        """
        # For future implementation
        return []
    
    def analyze_memories(self, query: str) -> str:
        """
        Analyze memories related to a query
        
        Args:
            query: Query to analyze
            
        Returns:
            Analysis text
        """
        # For future implementation
        return ""
    
    def categorize_memories(self, limit: int = 50) -> Dict[str, Any]:
        """
        Categorize memories
        
        Args:
            limit: Maximum number of memories to categorize
            
        Returns:
            Dictionary with categorization results
        """
        # For future implementation
        return {"categorized": 0, "categories": {}}

# Define what's available when importing from this module
__all__ = [
    'MemoryConfig',
    'BaseEmbeddingConfig',
    'OllamaEmbeddingConfig',
    'OpenAIEmbeddingConfig',
    'VectorStoreConfig',
    'EmbeddingProviderFactory',
    'VectorStoreFactory',
    'BaseEmbeddingProvider',
    'BaseVectorStore',
    'MemoryManager',
    'CLIcheMemory',
] 