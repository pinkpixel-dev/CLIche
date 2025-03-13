"""
Enhanced Memory system for CLIche

Handles memory storage, retrieval, and enhancement with improved capabilities.

Made with ❤️ by Pink Pixel
"""
import json
import logging
import re
import time
from typing import Dict, List, Any, Optional, Tuple

from .provider import MemoryProvider
from .enhanced import EnhancedMemory

class CLIcheMemory:
    """Memory system for CLIche"""
    
    def __init__(self, config=None):
        """
        Initialize the memory system
        
        Args:
            config: Configuration for the memory system
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize memory provider
        provider_name = "ollama" if config and config.get("provider") == "ollama" else "openai"
        self.provider = MemoryProvider(provider=provider_name, config=config)
        
        # Initialize enhanced memory system
        self.enhanced = EnhancedMemory(config)
        
        # Set default values
        self.enabled = config.get("enabled", True) if config else True
        self.auto_memory = config.get("auto_memory", False) if config else False
        self.user_id = config.get("user_id", "default_user") if config else "default_user"
        self.profile_enabled = config.get("profile_enabled", True) if config else True
    
    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Add a memory
        
        Args:
            content: Memory content
            metadata: Additional metadata
            
        Returns:
            Memory ID if successful, None otherwise
        """
        if not self.enabled:
            self.logger.warning("Memory system is disabled")
            return None
            
        try:
            # Use enhanced memory system
            return self.enhanced.add_memory(content, self.user_id, metadata)
        except Exception as e:
            self.logger.error(f"Failed to add memory: {str(e)}")
            return None
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories related to a query
        
        Args:
            query: Query to search for
            limit: Maximum number of results to return
            
        Returns:
            List of matching memories
        """
        if not self.enabled:
            self.logger.warning("Memory system is disabled")
            return []
            
        try:
            # Use enhanced memory system
            results = self.enhanced.search_memories(query, self.user_id, limit)
            return results.get("results", [])
        except Exception as e:
            self.logger.error(f"Failed to search memories: {str(e)}")
            return []
    
    def enhance_with_memories(self, message: str) -> str:
        """
        Enhance a message with relevant memories
        
        Args:
            message: Message to enhance
            
        Returns:
            Enhanced message
        """
        if not self.enabled:
            return message
            
        try:
            # Use enhanced memory system
            return self.enhanced.enhance_with_memories(message, self.user_id)
        except Exception as e:
            self.logger.error(f"Failed to enhance with memories: {str(e)}")
            return message
    
    def detect_memory_request(self, query: str) -> tuple[bool, str, dict]:
        """
        Detect if a query is a memory request
        
        Args:
            query: Query to check
            
        Returns:
            Tuple of (is_memory_request, memory_content, metadata)
        """
        if not self.enabled:
            return False, "", {}
            
        try:
            # Use enhanced memory system
            return self.enhanced.detect_memory_request(query)
        except Exception as e:
            self.logger.error(f"Failed to detect memory request: {str(e)}")
            return False, "", {}
    
    def extract_and_store_memories(self, conversation: str) -> List[str]:
        """
        Extract facts from a conversation and store them as memories
        
        Args:
            conversation: Conversation to extract facts from
            
        Returns:
            List of memory IDs for the stored memories
        """
        if not self.enabled:
            self.logger.warning("Memory system is disabled")
            return []
            
        try:
            # Use enhanced memory system
            return self.enhanced.extract_and_store_memories(conversation, self.user_id)
        except Exception as e:
            self.logger.error(f"Failed to extract and store memories: {str(e)}")
            return []
    
    def chat_with_memory(self, query: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response to a query using relevant memories as context
        
        Args:
            query: User's query
            system_prompt: Optional system prompt
            
        Returns:
            Generated response
        """
        if not self.enabled:
            return "Memory system is disabled"
            
        try:
            # Use enhanced memory system
            return self.enhanced.chat_with_memory(query, self.user_id, system_prompt)
        except Exception as e:
            self.logger.error(f"Failed to chat with memory: {str(e)}")
            return f"Error: {str(e)}"
    
    def toggle(self, enabled: bool) -> bool:
        """
        Toggle the memory system on or off
        
        Args:
            enabled: Whether to enable the memory system
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.enabled = enabled
            
            # Update config
            if self.config:
                self.config["enabled"] = enabled
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to toggle memory system: {str(e)}")
            return False
    
    def set_user_id(self, user_id: str) -> bool:
        """
        Set the user ID for memories
        
        Args:
            user_id: User ID to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.user_id = user_id
            
            # Update config
            if self.config:
                self.config["user_id"] = user_id
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to set user ID: {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the memory system
        
        Returns:
            Dictionary with memory system status
        """
        try:
            # Get profile
            profile = {}
            if self.profile_enabled:
                try:
                    profile = self.provider.get_profile(self.user_id)
                except:
                    profile = {}
            
            return {
                "enabled": self.enabled,
                "provider": self.config.get("provider", "openai") if self.config else "openai",
                "user_id": self.user_id,
                "auto_memory": self.auto_memory,
                "data_dir": self.config.get("data_dir", "~/.cliche/memory") if self.config else "~/.cliche/memory",
                "collection_name": self.config.get("collection_name", "memories") if self.config else "memories",
                "profile_enabled": self.profile_enabled,
                "profile": profile
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory status: {str(e)}")
            return {
                "enabled": self.enabled,
                "provider": "unknown",
                "user_id": self.user_id,
                "auto_memory": self.auto_memory,
                "data_dir": "unknown",
                "collection_name": "unknown",
                "profile_enabled": self.profile_enabled,
                "profile": {}
            }
    
    def set_profile_field(self, field: str, value: str) -> bool:
        """
        Set a user profile field
        
        Args:
            field: Field to set
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            self.logger.warning("Memory system is disabled")
            return False
            
        if not self.profile_enabled:
            self.logger.warning("User profile is disabled")
            return False
            
        try:
            return self.provider.set_profile_field(self.user_id, field, value)
        except Exception as e:
            self.logger.error(f"Failed to set profile field: {str(e)}")
            return False
    
    def toggle_profile(self, enabled: bool) -> bool:
        """
        Toggle the user profile on or off
        
        Args:
            enabled: Whether to enable the user profile
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.profile_enabled = enabled
            
            # Update config
            if self.config:
                self.config["profile_enabled"] = enabled
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to toggle user profile: {str(e)}")
            return False
    
    def clear_profile(self) -> bool:
        """
        Clear the user profile
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            self.logger.warning("Memory system is disabled")
            return False
            
        if not self.profile_enabled:
            self.logger.warning("User profile is disabled")
            return False
            
        try:
            return self.provider.clear_profile(self.user_id)
        except Exception as e:
            self.logger.error(f"Failed to clear user profile: {str(e)}")
            return False
            
    def auto_add(self, message: str, response: str) -> Optional[str]:
        """
        Automatically extract and store facts from a conversation
        
        Args:
            message: User message
            response: AI response
            
        Returns:
            Memory ID if a memory was created, None otherwise
        """
        if not self.enabled or not self.auto_memory:
            return None
            
        try:
            # Build the conversation text
            conversation = f"User: {message}\nAI: {response}"
            
            # Extract facts using the enhanced memory system
            memory_ids = self.enhanced.extract_and_store_memories(conversation, self.user_id)
            
            # If any memories were stored, return the first ID
            if memory_ids:
                return memory_ids[0]
                
            return None
        except Exception as e:
            self.logger.error(f"Failed to auto-add memory: {str(e)}")
            return None
