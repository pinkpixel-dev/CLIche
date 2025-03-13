"""
Factory for creating vector stores for CLIche memory system.

This module provides a factory class for creating vector stores
based on configuration.

Made with ❤️ by Pink Pixel
"""
from typing import Dict, Type, Optional, Any
import logging

from ..config import VectorStoreConfig
from .base import BaseVectorStore


class VectorStoreFactory:
    """
    Factory for creating vector stores.
    
    This class creates vector stores based on configuration.
    """
    
    _store_classes: Dict[str, Type[BaseVectorStore]] = {}
    _logger = logging.getLogger(__name__)
    
    @classmethod
    def register_store(cls, provider_name: str, store_class: Type[BaseVectorStore]) -> None:
        """
        Register a store class.
        
        Args:
            provider_name: Name of the provider
            store_class: Store class
        """
        cls._store_classes[provider_name] = store_class
        cls._logger.debug(f"Registered vector store class: {provider_name}")
        
    @classmethod
    def get_store_class(cls, provider_name: str) -> Optional[Type[BaseVectorStore]]:
        """
        Get a store class by name.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Store class if registered, None otherwise
        """
        return cls._store_classes.get(provider_name)
    
    @classmethod
    def create_store(
        cls,
        provider_name: str,
        **config_args: Any,
    ) -> Optional[BaseVectorStore]:
        """
        Create a store instance.
        
        Args:
            provider_name: Name of the provider
            config_args: Additional configuration arguments
            
        Returns:
            Store instance if successful, None otherwise
        """
        store_class = cls.get_store_class(provider_name)
        if store_class is None:
            cls._logger.warning(f"Unknown vector store: {provider_name}")
            
            # First try to import the store
            try:
                # Dynamically import the store module
                if provider_name == "chroma":
                    from .chroma import ChromaVectorStore
                    store_class = ChromaVectorStore
                    cls.register_store("chroma", ChromaVectorStore)
            except ImportError as e:
                cls._logger.error(f"Failed to import vector store {provider_name}: {e}")
                return None
                
            if store_class is None:
                cls._logger.error(f"No store class found for {provider_name}")
                return None
        
        # Create the configuration
        config = VectorStoreConfig(provider=provider_name, **{k: v for k, v in config_args.items() if v is not None})
        
        # Create the store
        try:
            store = store_class(config)
            cls._logger.info(f"Created vector store: {provider_name}")
            return store
        except Exception as e:
            cls._logger.error(f"Failed to create vector store {provider_name}: {e}")
            return None
    
    @classmethod
    def create_store_from_config(cls, config: VectorStoreConfig) -> Optional[BaseVectorStore]:
        """
        Create a store instance from configuration.
        
        Args:
            config: Store configuration
            
        Returns:
            Store instance if successful, None otherwise
        """
        provider_name = config.provider
        store_class = cls.get_store_class(provider_name)
        
        if store_class is None:
            # Try to import the store
            try:
                # Dynamically import the store module
                if provider_name == "chroma":
                    from .chroma import ChromaVectorStore
                    store_class = ChromaVectorStore
                    cls.register_store("chroma", ChromaVectorStore)
            except ImportError as e:
                cls._logger.error(f"Failed to import vector store {provider_name}: {e}")
                return None
                
            if store_class is None:
                cls._logger.error(f"No store class found for {provider_name}")
                return None
        
        # Create the store
        try:
            store = store_class(config)
            cls._logger.info(f"Created vector store: {provider_name}")
            return store
        except Exception as e:
            cls._logger.error(f"Failed to create vector store {provider_name}: {e}")
            return None
