"""
Ollama embedding provider for CLIche memory system.

This module provides an embedding provider using Ollama.

Made with ❤️ by Pink Pixel
"""
from typing import List, Optional, Dict, Any, Union
import logging
import subprocess
import numpy as np
import json
import os
import time
import requests
from pathlib import Path

from ..config import OllamaEmbeddingConfig
from .base import BaseEmbeddingProvider

# Import Ollama conditionally to handle cases where it's not installed
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """
    Embedding provider using Ollama.
    
    This provider generates embeddings using a local Ollama server.
    """
    
    def __init__(self, config: OllamaEmbeddingConfig):
        """
        Initialize the Ollama embedding provider.
        
        Args:
            config: Configuration for the embedding provider
        """
        super().__init__(config)
        self.config = config
        self.host = config.host
        
        # Check if Ollama is installed
        if not OLLAMA_AVAILABLE:
            self.logger.warning("Ollama Python library is not installed. Using HTTP fallback.")
            # We can still use Ollama via HTTP API, so don't return
        
        # Check if Ollama is running
        if not self.is_available():
            self.logger.warning("Ollama server is not running or not reachable.")
            return
        
        # Check if the model is available, download if needed
        self.download_model()
        
        # Set is_ready flag
        self.is_ready = True
    
    def embed(self, text: Union[str, List[str]], truncate: bool = True) -> np.ndarray:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to generate embeddings for. Can be a single string or a list of strings.
            truncate: Whether to truncate text that exceeds model context limits
            
        Returns:
            Numpy array of embeddings, shape (n_texts, dimensions)
        """
        # Check if ready
        if not self.is_ready:
            if not self.is_available():
                raise RuntimeError("Ollama server is not running or not reachable")
            if not self.download_model():
                raise RuntimeError(f"Failed to download model: {self.config.model_name}")
            self.is_ready = True
        
        # Prepare text for embedding
        texts = self._prepare_text(text)
        
        # Generate embeddings in batches
        return self._batch_embed(texts)
    
    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Embed a batch of texts.
        
        Args:
            texts: Batch of texts to embed
            
        Returns:
            Numpy array of embeddings, shape (n_texts, dimensions)
        """
        embeddings = []
        
        for text in texts:
            # Generate embedding
            try:
                if OLLAMA_AVAILABLE:
                    # Use Ollama Python library
                    response = ollama.embeddings(
                        model=self.config.model_name,
                        prompt=text
                    )
                    embedding = response["embedding"]
                else:
                    # Use HTTP API
                    response = requests.post(
                        f"{self.host}/api/embeddings",
                        json={
                            "model": self.config.model_name,
                            "prompt": text
                        }
                    )
                    response.raise_for_status()
                    embedding = response.json()["embedding"]
                
                embeddings.append(embedding)
            except Exception as e:
                self.logger.error(f"Failed to generate embedding: {e}")
                # Use a zero embedding as fallback
                embeddings.append(np.zeros(self.get_dimensions()).tolist())
        
        # Convert to numpy array
        return np.array(embeddings)
    
    def get_dimensions(self) -> int:
        """
        Get the dimensions of the embeddings.
        
        Returns:
            Number of dimensions
        """
        return self.config.dimensions
    
    def is_available(self) -> bool:
        """
        Check if Ollama is available.
        
        Returns:
            True if available, False otherwise
        """
        try:
            # Try to ping the Ollama server
            if OLLAMA_AVAILABLE:
                # Use Ollama Python library
                ollama.list()
            else:
                # Use HTTP API
                response = requests.get(f"{self.host}/api/tags")
                response.raise_for_status()
            
            return True
        except Exception as e:
            self.logger.debug(f"Ollama server not available: {e}")
            return False
    
    def download_model(self, model_name: Optional[str] = None) -> bool:
        """
        Download the Ollama model if needed.
        
        Args:
            model_name: Name of the model to download. If None, use the model from config.
            
        Returns:
            True if successful, False otherwise
        """
        if model_name is None:
            model_name = self.config.model_name
        
        try:
            # Check if model is already available
            if OLLAMA_AVAILABLE:
                models = ollama.list()
                for model in models.get("models", []):
                    if model.get("name") == model_name:
                        self.logger.info(f"Model already available: {model_name}")
                        return True
            else:
                # Use HTTP API
                response = requests.get(f"{self.host}/api/tags")
                response.raise_for_status()
                models = response.json()
                for model in models.get("models", []):
                    if model.get("name") == model_name:
                        self.logger.info(f"Model already available: {model_name}")
                        return True
            
            # Download the model
            self.logger.info(f"Downloading model: {model_name}")
            
            if OLLAMA_AVAILABLE:
                # Use Ollama Python library
                ollama.pull(model_name)
            else:
                # Use HTTP API
                response = requests.post(
                    f"{self.host}/api/pull",
                    json={"name": model_name}
                )
                response.raise_for_status()
            
            self.logger.info(f"Downloaded model: {model_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to download model {model_name}: {e}")
            return False
    
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        This method is called when the embedding provider is no longer needed.
        """
        # Nothing to clean up for Ollama
        pass
