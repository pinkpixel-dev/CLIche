"""
Embedding providers for CLIche memory system.

This module provides embedding providers for the memory system.

Made with ❤️ by Pink Pixel
"""
from .base import BaseEmbeddingProvider
from .factory import EmbeddingProviderFactory

__all__ = [
    "BaseEmbeddingProvider",
    "EmbeddingProviderFactory",
]

# Register providers when they're imported
try:
    from .ollama import OllamaEmbeddingProvider
    EmbeddingProviderFactory.register_provider("ollama", OllamaEmbeddingProvider)
    __all__.append("OllamaEmbeddingProvider")
except ImportError:
    pass

try:
    from .openai import OpenAIEmbeddingProvider
    EmbeddingProviderFactory.register_provider("openai", OpenAIEmbeddingProvider)
    __all__.append("OpenAIEmbeddingProvider")
except ImportError:
    pass

try:
    from .anthropic import AnthropicEmbeddingProvider
    EmbeddingProviderFactory.register_provider("anthropic", AnthropicEmbeddingProvider)
    __all__.append("AnthropicEmbeddingProvider")
except ImportError:
    pass

try:
    from .google import GoogleEmbeddingProvider
    EmbeddingProviderFactory.register_provider("google", GoogleEmbeddingProvider)
    __all__.append("GoogleEmbeddingProvider")
except ImportError:
    pass

try:
    from .deepseek import DeepSeekEmbeddingProvider
    EmbeddingProviderFactory.register_provider("deepseek", DeepSeekEmbeddingProvider)
    __all__.append("DeepSeekEmbeddingProvider")
except ImportError:
    pass

try:
    from .openrouter import OpenRouterEmbeddingProvider
    EmbeddingProviderFactory.register_provider("openrouter", OpenRouterEmbeddingProvider)
    __all__.append("OpenRouterEmbeddingProvider")
except ImportError:
    pass
