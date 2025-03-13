"""
Base embedding provider for CLIche memory system.

This module defines the abstract base class for embedding providers.

Made with ❤️ by Pink Pixel
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
import logging
import numpy as np

from ..config import BaseEmbeddingConfig


class BaseEmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    
    All embedding providers must implement this interface.
    """
    
    def __init__(self, config: BaseEmbeddingConfig):
        """
        Initialize the embedding provider.
        
        Args:
            config: Configuration for the embedding provider
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_ready = False
        
    @abstractmethod
    def embed(self, text: Union[str, List[str]], truncate: bool = True) -> np.ndarray:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to generate embeddings for. Can be a single string or a list of strings.
            truncate: Whether to truncate text that exceeds model context limits
            
        Returns:
            Numpy array of embeddings, shape (n_texts, dimensions)
        """
        pass
    
    @abstractmethod
    def get_dimensions(self) -> int:
        """
        Get the dimensions of the embeddings.
        
        Returns:
            Number of dimensions
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the embedding provider is available.
        
        Returns:
            True if available, False otherwise
        """
        pass
    
    def download_model(self, model_name: Optional[str] = None) -> bool:
        """
        Download a model if needed.
        
        Args:
            model_name: Name of the model to download. If None, use the default model.
            
        Returns:
            True if download successful or not needed, False otherwise
        """
        # Default implementation does nothing (assumes model is already available)
        return True
    
    def _prepare_text(self, text: Union[str, List[str]], max_length: int = 8192) -> List[str]:
        """
        Prepare text for embedding.
        
        Args:
            text: Text to prepare. Can be a single string or a list of strings.
            max_length: Maximum length for each text
            
        Returns:
            List of prepared texts
        """
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text
            
        # Truncate texts if needed
        if max_length:
            texts = [t[:max_length] for t in texts]
            
        return texts
    
    def _batch_embed(self, texts: List[str], batch_size: Optional[int] = None) -> np.ndarray:
        """
        Embed texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size to use. If None, use config batch_size.
            
        Returns:
            Numpy array of embeddings, shape (n_texts, dimensions)
        """
        if batch_size is None:
            batch_size = self.config.batch_size
            
        # If batch size is 0 or negative, embed all at once
        if batch_size <= 0:
            batch_size = len(texts)
            
        # Embed in batches
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self._embed_batch(batch)
            embeddings.append(batch_embeddings)
            
        # Concatenate all batches
        return np.vstack(embeddings) if embeddings else np.array([])
    
    @abstractmethod
    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Embed a batch of texts.
        
        Args:
            texts: Batch of texts to embed
            
        Returns:
            Numpy array of embeddings, shape (n_texts, dimensions)
        """
        pass
    
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        This method is called when the embedding provider is no longer needed.
        """
        # Default implementation does nothing
        pass
