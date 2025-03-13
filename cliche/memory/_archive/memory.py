"""
Memory system for CLIche

Provides a unified interface for memory operations.

Made with ❤️ by Pink Pixel
"""
import os
import logging
from typing import Dict, Any, List, Optional

from .provider import MemoryProvider

class CLIcheMemory:
    """Memory system for CLIche"""
    
    def __init__(self, config):
        """
        Initialize the memory system
        
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
        
        # Initialize user profile settings
        self.profile_enabled = memory_config.get("profile_enabled", True)
        self.profile = memory_config.get("profile", {})
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize memory provider
        if self.enabled:
            try:
                self.provider = MemoryProvider(
                    provider=self.provider_name,
                    data_dir=self.data_dir,
                    collection_name=self.collection_name,
                    config=config
                )
                self.logger.info(f"Memory system initialized with provider {self.provider_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize memory provider: {str(e)}")
                self.enabled = False
                self.provider = None
        else:
            self.provider = None
    
    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Add a memory
        
        Args:
            content: Memory content
            metadata: Additional metadata
            
        Returns:
            Memory ID if successful, None otherwise
        """
        if not self.enabled or not self.provider:
            return None
        
        try:
            memory_id = self.provider.add_memory(content, self.user_id, metadata)
            return memory_id
        except Exception as e:
            self.logger.error(f"Failed to add memory: {str(e)}")
            return None
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        if not self.enabled or not self.provider:
            return []
        
        try:
            results = self.provider.search_memories(query, self.user_id, limit)
            return results.get("results", [])
        except Exception as e:
            self.logger.error(f"Failed to search memories: {str(e)}")
            return []
    
    def enhance_with_memories(self, message: str) -> str:
        """
        Enhance a message with relevant memories
        
        Args:
            message: User message
            
        Returns:
            Enhanced message with memory context
        """
        if not self.enabled or not self.provider:
            return message
        
        try:
            # Search for relevant memories
            memories = self.search(message)
            
            # Format memories for inclusion in the prompt
            memories_str = ""
            if memories:
                memories_str += "Here are some relevant memories that might help you provide a better response:\n"
                memories_str += "\n".join([
                    f"- {memory['memory']}" for memory in memories
                ])
                memories_str += "\n\n"
            
            # Add user profile information if enabled
            if self.profile_enabled and self.profile:
                memories_str += "User Profile Information:\n"
                for key, value in self.profile.items():
                    memories_str += f"- {key.capitalize()}: {value}\n"
                memories_str += "\n"
            
            # If we have any context to add, enhance the message
            if memories_str:
                enhanced_message = f"""
{message}

{memories_str}
"""
                return enhanced_message
            
            return message
        except Exception as e:
            self.logger.error(f"Failed to enhance message with memories: {str(e)}")
            return message
    
    def chat_with_memory(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Chat with the AI using memory context
        
        Args:
            message: User message
            system_prompt: Optional custom system prompt
            
        Returns:
            AI response
        """
        if not self.enabled or not self.provider:
            return "Memory system is disabled. Please enable it to use this feature."
        
        try:
            return self.provider.chat_with_memory(message, self.user_id, system_prompt)
        except Exception as e:
            self.logger.error(f"Failed to chat with memory: {str(e)}")
            return f"Error: {str(e)}"
    
    def toggle(self, enabled: bool) -> bool:
        """
        Toggle memory system on/off
        
        Args:
            enabled: Whether to enable the memory system
            
        Returns:
            Success status
        """
        try:
            # Update memory config
            memory_config = self.config.config.get("memory", {})
            memory_config["enabled"] = enabled
            self.config.config["memory"] = memory_config
            
            # Save config
            self.config.save_config(self.config.config)
            
            # Update instance state
            self.enabled = enabled
            
            # Reinitialize provider if enabling
            if enabled and not self.provider:
                self.provider = MemoryProvider(
                    provider=self.provider_name,
                    data_dir=self.data_dir,
                    collection_name=self.collection_name,
                    config=self.config
                )
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to toggle memory system: {str(e)}")
            return False
    
    def set_user_id(self, user_id: str) -> bool:
        """
        Set the user ID for memories
        
        Args:
            user_id: User ID
            
        Returns:
            Success status
        """
        try:
            # Update memory config
            memory_config = self.config.config.get("memory", {})
            memory_config["user_id"] = user_id
            self.config.config["memory"] = memory_config
            
            # Save config
            self.config.save_config(self.config.config)
            
            # Update instance state
            self.user_id = user_id
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to set user ID: {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get memory system status
        
        Returns:
            Dictionary with status information
        """
        return {
            "enabled": self.enabled,
            "provider": self.provider_name,
            "user_id": self.user_id,
            "auto_memory": self.auto_memory,
            "data_dir": self.data_dir,
            "collection_name": self.collection_name,
            "profile_enabled": self.profile_enabled,
            "profile": self.profile
        }
    
    def set_profile_field(self, field: str, value: str) -> bool:
        """
        Set a user profile field
        
        Args:
            field: Profile field name
            value: Profile field value
            
        Returns:
            Success status
        """
        try:
            # Update memory config
            memory_config = self.config.config.get("memory", {})
            
            # Initialize profile if it doesn't exist
            if "profile" not in memory_config:
                memory_config["profile"] = {}
            
            # Update profile field
            memory_config["profile"][field] = value
            self.config.config["memory"] = memory_config
            
            # Save config
            self.config.save_config(self.config.config)
            
            # Update instance state
            self.profile[field] = value
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to set profile field: {str(e)}")
            return False
    
    def toggle_profile(self, enabled: bool) -> bool:
        """
        Toggle user profile on/off
        
        Args:
            enabled: Whether to enable the user profile
            
        Returns:
            Success status
        """
        try:
            # Update memory config
            memory_config = self.config.config.get("memory", {})
            memory_config["profile_enabled"] = enabled
            self.config.config["memory"] = memory_config
            
            # Save config
            self.config.save_config(self.config.config)
            
            # Update instance state
            self.profile_enabled = enabled
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to toggle user profile: {str(e)}")
            return False
    
    def clear_profile(self) -> bool:
        """
        Clear the user profile
        
        Returns:
            Success status
        """
        try:
            # Update memory config
            memory_config = self.config.config.get("memory", {})
            memory_config["profile"] = {}
            self.config.config["memory"] = memory_config
            
            # Save config
            self.config.save_config(self.config.config)
            
            # Update instance state
            self.profile = {}
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear user profile: {str(e)}")
            return False
