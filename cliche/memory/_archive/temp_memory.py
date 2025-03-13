"""
Memory system for CLIche

Provides a unified interface for memory operations.

Made with ❤️ by Pink Pixel
"""
import os
import logging
from typing import Dict, Any, List, Optional

from .provider import MemoryProvider
# Import enhanced memory components
from .enhanced import EnhancedMemory

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
                
                # Initialize enhanced memory system
                self.enhanced = EnhancedMemory(config)
                self.logger.info("Enhanced memory system initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize memory provider: {str(e)}")
                self.enabled = False
                self.provider = None
                self.enhanced = None
        else:
            self.provider = None
            self.enhanced = None
    
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
            # Use enhanced memory system if available, otherwise fall back to provider
            if self.enhanced:
                memory_id = self.enhanced.add_memory(content, self.user_id, metadata)
            else:
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
            # Use enhanced memory system if available, otherwise fall back to provider
            if self.enhanced:
                results = self.enhanced.search_memories(query, self.user_id, limit)
                return results.get("results", [])
            else:
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
        if not self.enabled:
            return message
            
        try:
            # Get relevant memories
            memories = self.search(message, limit=3)
            
            if not memories:
                return message
                
            # Format memories as context
            memory_context = "\n\nRelevant context from your memory:\n"
            for i, memory in enumerate(memories):
                # Handle different memory formats
                if 'content' in memory:
                    memory_content = memory['content']
                elif 'memory' in memory:
                    memory_content = memory['memory']
                else:
                    # Fall back to the first value in the memory dict
                    memory_content = next(iter(memory.values()), "")
                
                memory_context += f"- {memory_content}\n"
                
            # Add memory context to message
            enhanced_message = f"{message}\n{memory_context}"
            
            return enhanced_message
        except Exception as e:
            self.logger.error(f"Failed to enhance message: {str(e)}")
            return message
    
    def detect_memory_request(self, query: str) -> tuple:
        """
        Detect if a query is a memory request
        
        Args:
            query: Query string to analyze
            
        Returns:
            Tuple of (is_memory_request, memory_content, metadata)
        """
        # Check for memory-related keywords
        memory_keywords = [
            "remember", "recall", "memory", "memorize", 
            "don't forget", "note", "store"
        ]
        
        is_memory_request = any(keyword in query.lower() for keyword in memory_keywords)
        
        if is_memory_request:
            # Extract content (removing memory trigger words)
            content = query
            for keyword in memory_keywords:
                content = content.replace(f"remember {keyword}", "")
                content = content.replace(f"{keyword}", "")
            
            content = content.strip()
            metadata = {"source": "direct_request", "type": "memory"}
            
            return True, content, metadata
        
        return False, "", {}
    
    def detect_preference(self, query: str) -> tuple:
        """
        Detect if a query contains a user preference
        
        Args:
            query: Query string to analyze
            
        Returns:
            Tuple of (is_preference, preference_content, metadata)
        """
        # Check for preference indicators
        preference_indicators = [
            "I like", "I love", "I prefer", "I enjoy", 
            "I hate", "I dislike", "I don't like"
        ]
        
        is_preference = any(indicator in query for indicator in preference_indicators)
        
        if is_preference:
            content = query
            metadata = {"source": "conversation", "type": "preference"}
            
            return True, content, metadata
        
        return False, "", {}
    
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
            if self.enhanced:
                return self.enhanced.chat_with_memory(message, self.user_id, system_prompt)
            else:
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
                # Initialize enhanced memory if enabling
                self.enhanced = EnhancedMemory(self.config)
            
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
    
    def extract_personal_info(self, message: str, response: str = None) -> Dict[str, Any]:
        """
        Extract personal information from a message and optionally from the response
        
        Args:
            message: User message to analyze
            response: Optional AI response to analyze
            
        Returns:
            Dictionary of extracted personal information
        """
        if not self.enabled:
            return {}
        
        try:
            # Use enhanced extractor if available
            if self.enhanced:
                # Build conversation text
                conversation = message
                if response:
                    conversation = f"{message}\n{response}"
                return self.enhanced.extract_personal_info(conversation, self.user_id)
            else:
                # Simple rule-based extraction for basic personal info
                info = {}
                
                # Text to analyze (combine message and response if available)
                text_to_analyze = message
                if response:
                    text_to_analyze = f"{message} {response}"
                
                # Extract name
                name_indicators = ["my name is", "I am", "I'm", "call me"]
                for indicator in name_indicators:
                    if indicator.lower() in text_to_analyze.lower():
                        parts = text_to_analyze.lower().split(indicator.lower(), 1)
                        if len(parts) > 1:
                            # Extract the word after the indicator
                            name_part = parts[1].strip().split()[0]
                            if name_part and len(name_part) > 1:  # Ensure it's not just a letter
                                info["name"] = name_part.capitalize()
                
                # Extract location
                location_indicators = ["I live in", "I'm from", "I am from", "I'm in"]
                for indicator in location_indicators:
                    if indicator.lower() in text_to_analyze.lower():
                        parts = text_to_analyze.lower().split(indicator.lower(), 1)
                        if len(parts) > 1:
                            # Extract the phrase after the indicator
                            location_part = parts[1].strip().split('.')[0]  # Stop at period
                            if location_part and len(location_part) > 1:
                                info["location"] = location_part.capitalize()
                
                # Extract profession/role
                role_indicators = ["I work as", "I'm a", "I am a", "my job is"]
                for indicator in role_indicators:
                    if indicator.lower() in text_to_analyze.lower():
                        parts = text_to_analyze.lower().split(indicator.lower(), 1)
                        if len(parts) > 1:
                            # Extract the phrase after the indicator
                            role_part = parts[1].strip().split('.')[0]  # Stop at period
                            if role_part and len(role_part) > 1:
                                info["role"] = role_part.capitalize()
                
                return info
        except Exception as e:
            self.logger.error(f"Failed to extract personal info: {str(e)}")
            return {}
    
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
            
            # Use enhanced memory system if available
            if self.enhanced:
                # Extract facts using the enhanced memory system
                memory_ids = self.enhanced.extract_and_store_memories(conversation, self.user_id)
                
                # If any memories were stored, return the first ID
                if memory_ids:
                    return memory_ids[0]
            else:
                # Fallback to basic memory detection
                is_memory, content, metadata = self.detect_memory_request(message)
                if is_memory:
                    return self.add(content, metadata)
                
                is_preference, content, metadata = self.detect_preference(message)
                if is_preference:
                    return self.add(content, metadata)
                    
            return None
        except Exception as e:
            self.logger.error(f"Failed to auto-add memory: {str(e)}")
            return None
