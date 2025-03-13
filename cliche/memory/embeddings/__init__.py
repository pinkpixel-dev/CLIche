"""
Embedding providers for CLIche memory system.

This module provides embedding providers for the memory system.

Made with ❤️ by Pink Pixel
"""
from .base import BaseEmbeddingProvider

__all__ = [
    "BaseEmbeddingProvider",
]

# Register providers when they're imported
try:
    from .ollama import OllamaEmbeddingProvider
    __all__.append("OllamaEmbeddingProvider")
except ImportError:
    pass

try:
    from .openai import OpenAIEmbeddingProvider
    __all__.append("OpenAIEmbeddingProvider")
except ImportError:
    pass

try:
    from .anthropic import AnthropicEmbeddingProvider
    __all__.append("AnthropicEmbeddingProvider")
except ImportError:
    pass

try:
    from .google import GoogleEmbeddingProvider
    __all__.append("GoogleEmbeddingProvider")
except ImportError:
    pass

try:
    from .deepseek import DeepSeekEmbeddingProvider
    __all__.append("DeepSeekEmbeddingProvider")
except ImportError:
    pass

try:
    from .openrouter import OpenRouterEmbeddingProvider
    __all__.append("OpenRouterEmbeddingProvider")
except ImportError:
    pass
