"""
Stub memory system for CLIche during transition to new memory architecture

This is a temporary stub implementation that maintains compatibility
while the new memory system is being implemented.

Made with ❤️ by Pink Pixel
"""
import os
import logging
import time
from typing import Dict, Any, List, Optional, Tuple

class StubMemory:
    """Stub memory system for CLIche"""
    
    def __init__(self, config):
        """
        Initialize the stub memory system
        
        Args:
            config: CLIche configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get memory configuration
        memory_config = config.config.get("memory", {})
        
        # Initialize memory settings
        self.enabled = memory_config.get("enabled", True)
        self.provider_name = memory_config.get("provider", config.config.get("provider", "openai"))
        self.data_dir = memory_config.get("data_dir", os.path.join(config.config_dir, "memory"))
        self.collection_name = memory_config.get("collection_name", "cliche_memories")
        self.user_id = memory_config.get("user_id", "default_user")
        self.auto_memory = memory_config.get("auto_memory", True)
        
        # Create stub messages
        self.COMING_SOON = "⚠️ New memory system coming soon! This feature is currently being rebuilt."
        self.stub_memory_id = "stub-memory-id"
        
        # Log initialization
        self.logger.info("Stub memory system initialized")
        
    @property
    def enhanced_memory(self):
        """Stub enhanced memory property"""
        return None
        
    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Stub method to add a memory
        
        Args:
            content: Content to store
            metadata: Metadata for the memory
            
        Returns:
            Stub memory ID
        """
        self.logger.info(f"Stub memory add called with content: {content[:50]}...")
        return self.stub_memory_id
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Stub method to search memories
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Empty list
        """
        self.logger.info(f"Stub memory search called with query: {query}")
        return []
    
    def enhance_with_memories(self, message: str) -> str:
        """
        Stub method to enhance a message with memories
        
        Args:
            message: Message to enhance
            
        Returns:
            Original message unchanged
        """
        return message
    
    def detect_memory_request(self, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Stub method for memory request detection"""
        return False, query, {}
    
    def detect_preference(self, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Stub method for preference detection"""
        return False, query, {}
    
    def chat_with_memory(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Stub method for memory-based chat"""
        return self.COMING_SOON
    
    def toggle(self, enabled: bool) -> bool:
        """
        Toggle memory system on/off
        
        Args:
            enabled: True to enable, False to disable
            
        Returns:
            Current state
        """
        self.enabled = enabled
        return self.enabled
    
    def toggle_auto_memory(self, enabled: bool) -> bool:
        """
        Toggle auto-memory on/off
        
        Args:
            enabled: True to enable, False to disable
            
        Returns:
            Current state
        """
        self.auto_memory = enabled
        return self.auto_memory
    
    def extract_and_store_memories(self, conversation: str) -> List[str]:
        """Stub method for memory extraction"""
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get memory system status
        
        Returns:
            Status information
        """
        return {
            "enabled": self.enabled,
            "profile_enabled": False,
            "provider": self.provider_name,
            "message": self.COMING_SOON,
            "vector_store": None,
            "user_id": self.user_id,
            "memory_count": 0,
            "auto_memory": self.auto_memory
        }
    
    def set_profile_field(self, field: str, value: str) -> bool:
        """Stub method for profile field setting"""
        return False
    
    def toggle_profile(self, enabled: bool) -> bool:
        """Stub method for profile toggling"""
        return False
    
    def clear_profile(self) -> bool:
        """Stub method for profile clearing"""
        return False
    
    def auto_add(self, message: str, response: str) -> Optional[str]:
        """Stub method for auto memory addition"""
        return None
    
    def extract_personal_info(self, message: str, response: str = None, context: Dict[str, Any] = None) -> Dict[str, str]:
        """Stub method for personal info extraction"""
        return {}
    
    def set_auto_memory(self, enabled: bool) -> bool:
        """
        Set auto-memory status
        
        Args:
            enabled: True to enable, False to disable
            
        Returns:
            Current state
        """
        self.auto_memory = enabled
        return self.auto_memory
        
    # Additional stub methods for remaining functionality
    def remove_memory(self, term: str) -> Tuple[bool, str]:
        """Stub method for memory removal"""
        return False, self.COMING_SOON 