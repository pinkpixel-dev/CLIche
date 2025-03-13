"""
Factory classes for CLIche memory system.

This module provides factory classes for creating embedding providers,
vector stores, and other components, adapted from mem0.

Made with ❤️ by Pink Pixel
"""
import importlib
import logging
from typing import Dict, Type, Optional, Any

from .config import (
    BaseEmbeddingConfig,
    OllamaEmbeddingConfig,
    OpenAIEmbeddingConfig,
    AnthropicEmbeddingConfig,
    VectorStoreConfig,
)
from .embeddings.base import BaseEmbeddingProvider
from .vector_stores.base import BaseVectorStore


def load_class(class_type: str):
    """
    Load a class dynamically from a string.
    
    Args:
        class_type: String representation of the class
        
    Returns:
        The class
    """
    module_path, class_name = class_type.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


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
    
    provider_to_class = {
        "openai": "cliche.memory.embeddings.openai.OpenAIEmbeddingProvider",
        "ollama": "cliche.memory.embeddings.ollama.OllamaEmbeddingProvider",
        "huggingface": "cliche.memory.embeddings.huggingface.HuggingFaceEmbeddingProvider",
        "azure_openai": "cliche.memory.embeddings.azure_openai.AzureOpenAIEmbeddingProvider",
        "gemini": "cliche.memory.embeddings.gemini.GeminiEmbeddingProvider",
        "vertexai": "cliche.memory.embeddings.vertexai.VertexAIEmbeddingProvider",
        "together": "cliche.memory.embeddings.together.TogetherEmbeddingProvider",
        "anthropic": "cliche.memory.embeddings.anthropic.AnthropicEmbeddingProvider",
        "google": "cliche.memory.embeddings.google.GoogleEmbeddingProvider",
        "deepseek": "cliche.memory.embeddings.deepseek.DeepSeekEmbeddingProvider",
        "openrouter": "cliche.memory.embeddings.openrouter.OpenRouterEmbeddingProvider",
    }
    
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
        # First try from registered classes
        if provider_name in cls._provider_classes:
            return cls._provider_classes[provider_name]
        
        # Then try to load dynamically
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            try:
                provider_class = load_class(class_type)
                cls.register_provider(provider_name, provider_class)
                return provider_class
            except (ImportError, AttributeError) as e:
                cls._logger.error(f"Failed to load embedding provider class {provider_name}: {e}")
        
        return None
    
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


class VectorStoreFactory:
    """
    Factory for creating vector stores.
    
    This class creates vector stores based on configuration.
    """
    
    _store_classes: Dict[str, Type[BaseVectorStore]] = {}
    _logger = logging.getLogger(__name__)
    
    provider_to_class = {
        "chroma": "cliche.memory.vector_stores.chroma.ChromaVectorStore",
        "qdrant": "cliche.memory.vector_stores.qdrant.QdrantVectorStore",
        "pgvector": "cliche.memory.vector_stores.pgvector.PGVectorStore",
        "milvus": "cliche.memory.vector_stores.milvus.MilvusVectorStore",
        "azure_ai_search": "cliche.memory.vector_stores.azure_ai_search.AzureAISearchVectorStore",
        "redis": "cliche.memory.vector_stores.redis.RedisVectorStore",
        "elasticsearch": "cliche.memory.vector_stores.elasticsearch.ElasticsearchVectorStore",
        "vertex_ai_vector_search": "cliche.memory.vector_stores.vertex_ai_vector_search.VertexAIVectorSearchStore",
        "opensearch": "cliche.memory.vector_stores.opensearch.OpenSearchVectorStore",
        "supabase": "cliche.memory.vector_stores.supabase.SupabaseVectorStore",
    }
    
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
        # First try from registered classes
        if provider_name in cls._store_classes:
            return cls._store_classes[provider_name]
        
        # Then try to load dynamically
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            try:
                store_class = load_class(class_type)
                cls.register_store(provider_name, store_class)
                return store_class
            except (ImportError, AttributeError) as e:
                cls._logger.error(f"Failed to load vector store class {provider_name}: {e}")
        
        return None
    
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