"""
Core functionality for CLIche
"""
import os
import json
import click
from pathlib import Path
from enum import Enum
from typing import Optional, Dict, Any
import logging

from .providers import get_provider_class
from .providers.base import LLMBase
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.google import GoogleProvider
from .providers.ollama import OllamaProvider
from .providers.deepseek import DeepSeekProvider
from .providers.openrouter import OpenRouterProvider

class Config:
    def __init__(self, config_path=None):
        self.config_dir = Path.home() / ".config" / "cliche"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()
        self._load_services_env()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            # Create default config
            default_config = {
                "provider": "openai",
                "providers": {
                    "openai": {"api_key": "", "model": "gpt-3.5-turbo", "max_tokens": 16000},
                    "anthropic": {"api_key": "", "model": "claude-instant", "max_tokens": 100000},
                    "google": {"api_key": "", "model": "gemini-pro", "max_tokens": 32000},
                    "ollama": {"model": "phi4", "max_tokens": 100000},
                    "deepseek": {"api_key": "", "model": "deepseek-chat", "max_tokens": 8192},
                    "openrouter": {"api_key": "", "model": "openai/gpt-3.5-turbo", "max_tokens": 100000}
                },
                "services": {
                    "unsplash": {"api_key": ""},
                    "stability_ai": {"api_key": ""},
                    "dalle": {"use_openai_key": False},
                    "brave_search": {"api_key": ""}
                },
                "image_generation": {
                    "default_provider": "dalle",  # Options: dalle, stability
                    "default_size": "1024x1024",
                    "default_quality": "standard"  # Options: standard, hd
                }
            }
            self.save_config(default_config)
            return default_config

        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            click.echo("Error reading config file. Using defaults.")
            return {"provider": "openai", "providers": {}, "services": {}}

    def _load_services_env(self) -> None:
        """Load service API keys into environment variables."""
        # Load Unsplash API key if configured
        if 'services' in self.config and 'unsplash' in self.config['services']:
            unsplash_key = self.config['services']['unsplash'].get('api_key')
            if unsplash_key:
                os.environ['UNSPLASH_API_KEY'] = unsplash_key
        
        # Load Stability AI key if configured
        if 'services' in self.config and 'stability_ai' in self.config['services']:
            stability_key = self.config['services']['stability_ai'].get('api_key')
            if stability_key:
                os.environ['STABILITY_API_KEY'] = stability_key
        
        # Handle DALL-E configuration (uses OpenAI key)
        if 'services' in self.config and 'dalle' in self.config['services']:
            use_openai_key = self.config['services']['dalle'].get('use_openai_key')
            if use_openai_key:
                # Get the OpenAI key
                openai_key = self.config.get('providers', {}).get('openai', {}).get('api_key')
                if openai_key:
                    # Make it available to DALL-E utilities
                    os.environ['OPENAI_API_KEY'] = openai_key

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Write config file
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)
        
        self.config = config
        # Reload service API keys
        self._load_services_env()

    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        return self.config.get("providers", {}).get(provider_name, {})

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"

def get_llm():
    """Get the configured LLM provider."""
    cliche = get_cliche_instance()
    return cliche.provider

class CLIche:
    def __init__(self, config_path=None):
        """Initialize CLIche with configuration"""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = Config(config_path)
        self.config_dir = self.config.config_dir
        
        # Initialize memory system
        try:
            from .memory import CLIcheMemory
            self.memory = CLIcheMemory(self.config)
            self.logger.info("Memory system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize memory system: {str(e)}")
            self.memory = None
        
        # Initialize LLM provider
        self.provider = self._initialize_provider()
        
    def _initialize_provider(self):
        """Initialize the LLM provider."""
        provider_name = self.config.config.get("provider", "ollama")
        
        # Get the provider class (loaded on demand)
        provider_class = get_provider_class(provider_name)
        
        if provider_class:
            try:
                return provider_class(self.config)
            except Exception as e:
                self.logger.error(f"Failed to initialize provider {provider_name}: {str(e)}")
                return None
        else:
            self.logger.error(f"Provider {provider_name} not available")
            return None
            
    async def ask_llm(self, message, system_prompt=None, include_sys_info=False, professional_mode=False):
        """Ask the LLM a question and get a response"""
        if not self.provider:
            return "Error: LLM provider not initialized. Please check your configuration."
        
        try:
            return await self.provider.ask(message, system_prompt, include_sys_info, professional_mode)
        except Exception as e:
            self.logger.error(f"Error asking LLM: {str(e)}")
            return f"Error: {str(e)}"
    
    async def ask_with_memory(self, message, system_prompt=None, include_sys_info=False, professional_mode=False):
        """Ask the LLM a question with memory context"""
        if not self.provider:
            return "Error: LLM provider not initialized. Please check your configuration."
        
        if not self.memory or not self.memory.enabled:
            return await self.ask_llm(message, system_prompt, include_sys_info, professional_mode)
        
        try:
            # Enhance message with relevant memories
            enhanced_message = self.memory.enhance_with_memories(message)
            
            # Get response from LLM
            response = await self.provider.ask(enhanced_message, system_prompt, include_sys_info, professional_mode)
            
            return response
        except Exception as e:
            self.logger.error(f"Error asking LLM with memory: {str(e)}")
            return f"Error: {str(e)}"

# Create the main CLI group
@click.group()
def cli():
    """CLIche: Your terminal's snarky genius assistant"""
    pass

# Singleton instance of CLIche
_cliche_instance = None

def get_cliche_instance():
    """Get the singleton instance of CLIche"""
    global _cliche_instance
    if _cliche_instance is None:
        _cliche_instance = CLIche()
    return _cliche_instance

# Register commands
def register_all_commands():
    from .commands.registry import register_commands
    register_commands(cli)

register_all_commands()
