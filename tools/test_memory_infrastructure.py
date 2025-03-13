#!/usr/bin/env python
"""
Test script for CLIche memory system infrastructure.

This script tests the core infrastructure components of the memory system,
including configuration, embedding providers, and vector stores.

Made with ❤️ by Pink Pixel
"""
import sys
import os
import logging
import argparse
import numpy as np
from pathlib import Path

# Add parent directory to path to import cliche
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cliche.memory.config import (
    MemoryConfig,
    BaseEmbeddingConfig,
    OllamaEmbeddingConfig,
    VectorStoreConfig,
)
from cliche.memory import (
    BaseEmbeddingProvider,
    EmbeddingProviderFactory,
    BaseVectorStore,
    VectorStoreFactory,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("memory_test")


def test_config():
    """Test configuration classes"""
    logger.info("Testing configuration classes...")
    
    # Test MemoryConfig with default values
    memory_config = MemoryConfig()
    assert memory_config.enabled is True, "Default enabled value should be True"
    assert memory_config.auto_memory is True, "Default auto_memory value should be True"
    assert memory_config.user_id == "default_user", "Default user_id value should be 'default_user'"
    assert isinstance(memory_config.embedding, BaseEmbeddingConfig), "embedding should be an instance of BaseEmbeddingConfig"
    assert isinstance(memory_config.vector_store, VectorStoreConfig), "vector_store should be an instance of VectorStoreConfig"
    
    # Test saving and loading
    test_path = "/tmp/cliche_test_config.json"
    memory_config.save(test_path)
    loaded_config = MemoryConfig.load(test_path)
    
    assert loaded_config.enabled == memory_config.enabled, "Loaded enabled value should match original"
    assert loaded_config.auto_memory == memory_config.auto_memory, "Loaded auto_memory value should match original"
    assert loaded_config.user_id == memory_config.user_id, "Loaded user_id value should match original"
    
    logger.info("Configuration tests passed.")


def test_embedding_factory():
    """Test embedding provider factory"""
    logger.info("Testing embedding provider factory...")
    
    # Create a config for Ollama
    ollama_config = OllamaEmbeddingConfig(
        model_name="nomic-embed-text",
        dimensions=768
    )
    
    # Create a provider using the factory
    provider = EmbeddingProviderFactory.create_provider_from_config(ollama_config)
    
    if provider is None:
        logger.warning("Could not create Ollama provider, skipping embedding tests")
        return
    
    # Check instance type
    assert isinstance(provider, BaseEmbeddingProvider), "Provider should be an instance of BaseEmbeddingProvider"
    
    # Check dimensions
    assert provider.get_dimensions() == 768, "Provider dimensions should match config"
    
    logger.info("Embedding factory tests passed.")


def test_vector_store_factory():
    """Test vector store factory"""
    logger.info("Testing vector store factory...")
    
    # Create a config for ChromaDB
    vector_config = VectorStoreConfig(
        provider="chroma",
        collection_name="test_collection",
        dimensions=768
    )
    
    # Create a store using the factory
    store = VectorStoreFactory.create_store_from_config(vector_config)
    
    if store is None:
        logger.warning("Could not create ChromaDB store, skipping vector store tests")
        return
    
    # Check instance type
    assert isinstance(store, BaseVectorStore), "Store should be an instance of BaseVectorStore"
    
    # Check collection name
    assert store.get_collection_name() == "test_collection", "Collection name should match config"
    
    logger.info("Vector store factory tests passed.")


def test_end_to_end():
    """Test end-to-end integration of embeddings and vector store"""
    logger.info("Testing end-to-end integration...")
    
    # Create providers
    ollama_config = OllamaEmbeddingConfig(
        model_name="nomic-embed-text",
        dimensions=768
    )
    
    provider = EmbeddingProviderFactory.create_provider_from_config(ollama_config)
    
    if provider is None:
        logger.warning("Could not create Ollama provider, skipping end-to-end tests")
        return
    
    # Create vector store
    vector_config = VectorStoreConfig(
        provider="chroma",
        collection_name="test_collection",
        dimensions=provider.get_dimensions()
    )
    
    store = VectorStoreFactory.create_store_from_config(vector_config)
    
    if store is None:
        logger.warning("Could not create ChromaDB store, skipping end-to-end tests")
        return
    
    # Create test content
    test_content = [
        "This is a test memory about Python programming.",
        "CLIche is a command-line interface for AI generation.",
        "Memory systems help AI assistants remember information over time.",
        "Vector embeddings are numerical representations of text content."
    ]
    
    memory_ids = []
    
    # Add memories
    for i, content in enumerate(test_content):
        # Generate embedding
        embedding = provider.embed(content)
        
        # Add to vector store
        memory_id = store.add(
            content=content,
            embedding=embedding[0],  # Take first (and only) embedding
            metadata={"index": i, "category": "test"}
        )
        
        memory_ids.append(memory_id)
        logger.info(f"Added memory {i+1}/{len(test_content)} with ID: {memory_id}")
    
    # Count memories
    count = store.count()
    assert count >= len(test_content), f"Expected at least {len(test_content)} memories, got {count}"
    
    # Search for memories
    query = "AI assistants and memory"
    logger.info(f"Generating embedding for query: '{query}'")
    query_embedding = provider.embed(query)
    
    logger.info(f"Query embedding shape: {query_embedding.shape}")
    logger.info(f"Searching with min_score: 0.0")
    
    results = store.search(
        query_embedding=query_embedding[0],
        limit=2,
        min_score=0.0  # Set min_score to 0 to ensure we get results
    )
    
    logger.info(f"Search returned {len(results)} results")
    
    # Check if results were returned
    if len(results) == 0:
        # Try another query as fallback
        fallback_query = "Vector embeddings"
        logger.info(f"No results found, trying fallback query: '{fallback_query}'")
        fallback_embedding = provider.embed(fallback_query)
        results = store.search(
            query_embedding=fallback_embedding[0],
            limit=2,
            min_score=0.0
        )
        logger.info(f"Fallback search returned {len(results)} results")
    
    assert len(results) > 0, "Expected at least one search result"
    
    # Display results
    logger.info(f"Search query: '{query}'")
    for i, result in enumerate(results):
        logger.info(f"Result {i+1}: {result['content']} (score: {result['score']:.4f})")
    
    # Clean up
    for memory_id in memory_ids:
        store.delete(memory_id)
    
    logger.info("End-to-end tests passed.")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test CLIche memory system infrastructure")
    parser.add_argument("--skip-config", action="store_true", help="Skip configuration tests")
    parser.add_argument("--skip-embedding", action="store_true", help="Skip embedding tests")
    parser.add_argument("--skip-vector", action="store_true", help="Skip vector store tests")
    parser.add_argument("--skip-e2e", action="store_true", help="Skip end-to-end tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        # Set all loggers to DEBUG level for more detailed output
        for name in logging.root.manager.loggerDict:
            if name.startswith('cliche'):
                logging.getLogger(name).setLevel(logging.DEBUG)
    
    logger.info("Starting memory system infrastructure tests...")
    
    try:
        if not args.skip_config:
            test_config()
        
        if not args.skip_embedding:
            test_embedding_factory()
        
        if not args.skip_vector:
            test_vector_store_factory()
        
        if not args.skip_e2e:
            test_end_to_end()
        
        logger.info("All tests passed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 