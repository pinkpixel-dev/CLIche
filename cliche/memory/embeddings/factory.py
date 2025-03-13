"""
Factory for creating embedding providers for CLIche memory system.

This module provides a factory class for creating embedding providers
based on configuration.

Made with ❤️ by Pink Pixel
"""
from typing import Dict, Type, Optional, Any
import logging

from ..config import (
    BaseEmbeddingConfig,
    OllamaEmbeddingConfig,
    OpenAIEmbeddingConfig,
    AnthropicEmbeddingConfig,
)
from .base import BaseEmbeddingProvider


class EmbeddingProviderFactory:
    """
    Factory for creating embedding providers.
    
    This class creates embedding providers based on configuration.
    """
    
    _provider_classes: Dict[str, Type[BaseEmbeddingProvider]] = {}
    _provider_config_classes: Dict[str, Type[BaseEmbeddingConfig]] = {
        "ollama": OllamaEmbeddingConfig,
        "openai": OpenAIEmbeddingConfig,
        "anthropic": AnthropicEmbeddingConfig,
    }
    _logger = logging.getLogger(__name__)
    
    @classmethod
    def register_provider(cls, provider_name: str, provider_class: Type[BaseEmbeddingProvider]) -> None:
        """
        Register a provider class.
        
        Args:
            provider_name: Name of the provider
            provider_class: Provider class
        """
        cls._provider_classes[provider_name] = provider_class
        cls._logger.debug(f"Registered embedding provider class: {provider_name}")
        
    @classmethod
    def get_provider_class(cls, provider_name: str) -> Optional[Type[BaseEmbeddingProvider]]:
        """
        Get a provider class by name.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider class if registered, None otherwise
        """
        return cls._provider_classes.get(provider_name)
    
    @classmethod
    def get_config_class(cls, provider_name: str) -> Type[BaseEmbeddingConfig]:
        """
        Get a provider configuration class by name.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider configuration class
        """
        return cls._provider_config_classes.get(provider_name, BaseEmbeddingConfig)
    
    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        **config_args: Any,
    ) -> Optional[BaseEmbeddingProvider]:
        """
        Create a provider instance.
        
        Args:
            provider_name: Name of the provider
            config_args: Additional configuration arguments
            
        Returns:
            Provider instance if successful, None otherwise
        """
        provider_class = cls.get_provider_class(provider_name)
        if provider_class is None:
            cls._logger.warning(f"Unknown embedding provider: {provider_name}")
            
            # First try to import the provider
            try:
                # Dynamically import the provider module
                if provider_name == "ollama":
                    from .ollama import OllamaEmbeddingProvider
                    provider_class = OllamaEmbeddingProvider
                    cls.register_provider("ollama", OllamaEmbeddingProvider)
                elif provider_name == "openai":
                    from .openai import OpenAIEmbeddingProvider
                    provider_class = OpenAIEmbeddingProvider
                    cls.register_provider("openai", OpenAIEmbeddingProvider)
                elif provider_name == "anthropic":
                    from .anthropic import AnthropicEmbeddingProvider
                    provider_class = AnthropicEmbeddingProvider
                    cls.register_provider("anthropic", AnthropicEmbeddingProvider)
                elif provider_name == "google":
                    from .google import GoogleEmbeddingProvider
                    provider_class = GoogleEmbeddingProvider
                    cls.register_provider("google", GoogleEmbeddingProvider)
                elif provider_name == "deepseek":
                    from .deepseek import DeepSeekEmbeddingProvider
                    provider_class = DeepSeekEmbeddingProvider
                    cls.register_provider("deepseek", DeepSeekEmbeddingProvider)
                elif provider_name == "openrouter":
                    from .openrouter import OpenRouterEmbeddingProvider
                    provider_class = OpenRouterEmbeddingProvider
                    cls.register_provider("openrouter", OpenRouterEmbeddingProvider)
            except ImportError as e:
                cls._logger.error(f"Failed to import embedding provider {provider_name}: {e}")
                return None
                
            if provider_class is None:
                cls._logger.error(f"No provider class found for {provider_name}")
                return None
        
        # Create the configuration
        config_class = cls.get_config_class(provider_name)
        config = config_class(**{k: v for k, v in config_args.items() if v is not None})
        
        # Create the provider
        try:
            provider = provider_class(config)
            cls._logger.info(f"Created embedding provider: {provider_name}")
            return provider
        except Exception as e:
            cls._logger.error(f"Failed to create embedding provider {provider_name}: {e}")
            return None
    
    @classmethod
    def create_provider_from_config(cls, config: BaseEmbeddingConfig) -> Optional[BaseEmbeddingProvider]:
        """
        Create a provider instance from configuration.
        
        Args:
            config: Provider configuration
            
        Returns:
            Provider instance if successful, None otherwise
        """
        provider_name = config.provider
        provider_class = cls.get_provider_class(provider_name)
        
        if provider_class is None:
            # Try to import the provider
            try:
                # Dynamically import the provider module
                if provider_name == "ollama":
                    from .ollama import OllamaEmbeddingProvider
                    provider_class = OllamaEmbeddingProvider
                    cls.register_provider("ollama", OllamaEmbeddingProvider)
                elif provider_name == "openai":
                    from .openai import OpenAIEmbeddingProvider
                    provider_class = OpenAIEmbeddingProvider
                    cls.register_provider("openai", OpenAIEmbeddingProvider)
                elif provider_name == "anthropic":
                    from .anthropic import AnthropicEmbeddingProvider
                    provider_class = AnthropicEmbeddingProvider
                    cls.register_provider("anthropic", AnthropicEmbeddingProvider)
                elif provider_name == "google":
                    from .google import GoogleEmbeddingProvider
                    provider_class = GoogleEmbeddingProvider
                    cls.register_provider("google", GoogleEmbeddingProvider)
                elif provider_name == "deepseek":
                    from .deepseek import DeepSeekEmbeddingProvider
                    provider_class = DeepSeekEmbeddingProvider
                    cls.register_provider("deepseek", DeepSeekEmbeddingProvider)
                elif provider_name == "openrouter":
                    from .openrouter import OpenRouterEmbeddingProvider
                    provider_class = OpenRouterEmbeddingProvider
                    cls.register_provider("openrouter", OpenRouterEmbeddingProvider)
            except ImportError as e:
                cls._logger.error(f"Failed to import embedding provider {provider_name}: {e}")
                return None
                
            if provider_class is None:
                cls._logger.error(f"No provider class found for {provider_name}")
                return None
        
        # Create the provider
        try:
            provider = provider_class(config)
            cls._logger.info(f"Created embedding provider: {provider_name}")
            return provider
        except Exception as e:
            cls._logger.error(f"Failed to create embedding provider {provider_name}: {e}")
            return None
