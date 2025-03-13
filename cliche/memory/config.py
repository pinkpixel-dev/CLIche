"""
Configuration classes for the CLIche memory system.

This module provides configuration classes for the memory system components,
including embedding providers and vector stores.

Made with ❤️ by Pink Pixel
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
import os
import json
from pathlib import Path


@dataclass
class BaseEmbeddingConfig:
    """Base configuration for embedding providers"""
    provider: str
    model_name: str
    dimensions: int = 384  # Default dimension
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    batch_size: int = 8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "provider": self.provider,
            "model_name": self.model_name,
            "dimensions": self.dimensions,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "batch_size": self.batch_size,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEmbeddingConfig':
        """Create configuration from dictionary"""
        return cls(
            provider=data.get("provider", "ollama"),
            model_name=data.get("model_name", "nomic-embed-text"),
            dimensions=data.get("dimensions", 384),
            api_key=data.get("api_key"),
            api_base=data.get("api_base"),
            batch_size=data.get("batch_size", 8)
        )


@dataclass
class OllamaEmbeddingConfig(BaseEmbeddingConfig):
    """Configuration for Ollama embedding provider"""
    provider: str = "ollama"
    model_name: str = "nomic-embed-text"
    host: str = "http://localhost:11434"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        data = super().to_dict()
        data["host"] = self.host
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OllamaEmbeddingConfig':
        """Create configuration from dictionary"""
        config = super().from_dict(data)
        return cls(
            provider=config.provider,
            model_name=config.model_name,
            dimensions=config.dimensions,
            api_key=config.api_key,
            api_base=config.api_base,
            batch_size=config.batch_size,
            host=data.get("host", "http://localhost:11434")
        )


@dataclass
class OpenAIEmbeddingConfig(BaseEmbeddingConfig):
    """Configuration for OpenAI embedding provider"""
    provider: str = "openai"
    model_name: str = "text-embedding-3-small"
    dimensions: int = 1536
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OpenAIEmbeddingConfig':
        """Create configuration from dictionary"""
        config = super().from_dict(data)
        # OpenAI models have specific dimension sizes
        if config.model_name == "text-embedding-3-small":
            config.dimensions = 1536
        elif config.model_name == "text-embedding-3-large":
            config.dimensions = 3072
        elif config.model_name == "text-embedding-ada-002":
            config.dimensions = 1536
            
        return cls(
            provider=config.provider,
            model_name=config.model_name,
            dimensions=config.dimensions,
            api_key=config.api_key,
            api_base=config.api_base,
            batch_size=config.batch_size
        )


@dataclass
class AnthropicEmbeddingConfig(BaseEmbeddingConfig):
    """Configuration for Anthropic embedding provider"""
    provider: str = "anthropic"
    model_name: str = "claude-3-haiku-20240307"
    dimensions: int = 1536
    

@dataclass
class VectorStoreConfig:
    """Configuration for vector stores"""
    provider: str = "chroma"
    collection_name: str = "cliche_memories"
    persist_directory: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    dimensions: int = 384  # Will be overridden by embedding provider's dimensions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "provider": self.provider,
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory,
            "host": self.host,
            "port": self.port,
            "dimensions": self.dimensions
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorStoreConfig':
        """Create configuration from dictionary"""
        return cls(
            provider=data.get("provider", "chroma"),
            collection_name=data.get("collection_name", "cliche_memories"),
            persist_directory=data.get("persist_directory"),
            host=data.get("host"),
            port=data.get("port"),
            dimensions=data.get("dimensions", 384)
        )


@dataclass
class MemoryConfig:
    """Configuration for the CLIche memory system"""
    enabled: bool = True
    auto_memory: bool = True
    user_id: str = "default_user"
    data_dir: Optional[str] = None
    embedding: Union[BaseEmbeddingConfig, Dict[str, Any]] = field(
        default_factory=lambda: OllamaEmbeddingConfig()
    )
    vector_store: Union[VectorStoreConfig, Dict[str, Any]] = field(
        default_factory=lambda: VectorStoreConfig()
    )
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Convert dict to proper config objects if needed
        if isinstance(self.embedding, dict):
            provider = self.embedding.get("provider", "ollama")
            if provider == "ollama":
                self.embedding = OllamaEmbeddingConfig.from_dict(self.embedding)
            elif provider == "openai":
                self.embedding = OpenAIEmbeddingConfig.from_dict(self.embedding)
            elif provider == "anthropic":
                self.embedding = AnthropicEmbeddingConfig.from_dict(self.embedding)
            else:
                self.embedding = BaseEmbeddingConfig.from_dict(self.embedding)
                
        if isinstance(self.vector_store, dict):
            self.vector_store = VectorStoreConfig.from_dict(self.vector_store)
            
        # Set default data directory if not specified
        if not self.data_dir:
            config_dir = Path.home() / ".config" / "cliche"
            self.data_dir = str(config_dir / "memory")
            
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Ensure vector store dimensions match embedding dimensions
        if isinstance(self.embedding, BaseEmbeddingConfig):
            self.vector_store.dimensions = self.embedding.dimensions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "enabled": self.enabled,
            "auto_memory": self.auto_memory,
            "user_id": self.user_id,
            "data_dir": self.data_dir,
            "embedding": self.embedding.to_dict() if isinstance(self.embedding, BaseEmbeddingConfig) else self.embedding,
            "vector_store": self.vector_store.to_dict() if isinstance(self.vector_store, VectorStoreConfig) else self.vector_store,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryConfig':
        """Create configuration from dictionary"""
        return cls(
            enabled=data.get("enabled", True),
            auto_memory=data.get("auto_memory", True),
            user_id=data.get("user_id", "default_user"),
            data_dir=data.get("data_dir"),
            embedding=data.get("embedding", {}),
            vector_store=data.get("vector_store", {})
        )
        
    def save(self, config_path: Optional[str] = None) -> None:
        """Save configuration to file"""
        if not config_path:
            config_dir = Path.home() / ".config" / "cliche"
            config_path = str(config_dir / "memory_config.json")
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Save to file
        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'MemoryConfig':
        """Load configuration from file"""
        if not config_path:
            config_dir = Path.home() / ".config" / "cliche"
            config_path = str(config_dir / "memory_config.json")
            
        # Return default config if file doesn't exist
        if not os.path.exists(config_path):
            return cls()
            
        # Load from file
        with open(config_path, "r") as f:
            data = json.load(f)
            
        return cls.from_dict(data)
