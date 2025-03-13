#!/usr/bin/env python3
"""
Test script for the CLIche Memory Manager.

This script tests the functionality of the MemoryManager class, which provides
a high-level interface for working with memories in the CLIche memory system.

Made with ❤️ by Pink Pixel
"""
import sys
import os
import logging
import argparse
import uuid
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the cliche package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the memory manager
from cliche.memory import MemoryManager, MemoryConfig, BaseEmbeddingConfig, VectorStoreConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('memory_manager_test')


def test_memory_manager_init():
    """Test initializing the memory manager"""
    logger.info("Testing memory manager initialization...")
    
    # Create a memory manager with default configuration
    manager = MemoryManager()
    
    # Check if the manager is ready
    assert manager.is_ready(), "Memory manager should be ready"
    
    logger.info("Memory manager initialization test passed.")
    return manager


def test_add_memory(manager: MemoryManager):
    """Test adding memories to the memory manager"""
    logger.info("Testing adding memories...")
    
    # Add some test memories
    memory_ids = []
    
    # Memory 1
    content = "Memory systems help AI assistants remember information over time."
    metadata = {"type": "fact", "topic": "memory", "source": "test"}
    memory_id = manager.add_memory(content, metadata)
    assert memory_id is not None, "Failed to add memory 1"
    memory_ids.append(memory_id)
    logger.info(f"Added memory 1 with ID: {memory_id}")
    
    # Memory 2
    content = "Vector embeddings are used to represent text in a high-dimensional space."
    metadata = {"type": "fact", "topic": "embeddings", "source": "test"}
    memory_id = manager.add_memory(content, metadata)
    assert memory_id is not None, "Failed to add memory 2"
    memory_ids.append(memory_id)
    logger.info(f"Added memory 2 with ID: {memory_id}")
    
    # Memory 3
    content = "ChromaDB is a vector database for storing and retrieving embeddings."
    metadata = {"type": "fact", "topic": "vector_store", "source": "test"}
    memory_id = manager.add_memory(content, metadata)
    assert memory_id is not None, "Failed to add memory 3"
    memory_ids.append(memory_id)
    logger.info(f"Added memory 3 with ID: {memory_id}")
    
    # Memory 4
    content = "CLIche is a command-line interface for AI assistants."
    metadata = {"type": "fact", "topic": "cliche", "source": "test"}
    memory_id = manager.add_memory(content, metadata)
    assert memory_id is not None, "Failed to add memory 4"
    memory_ids.append(memory_id)
    logger.info(f"Added memory 4 with ID: {memory_id}")
    
    logger.info("Adding memories test passed.")
    return memory_ids


def test_get_memory(manager: MemoryManager, memory_ids: List[str]):
    """Test retrieving memories from the memory manager"""
    logger.info("Testing retrieving memories...")
    
    # Get each memory by ID
    for i, memory_id in enumerate(memory_ids):
        memory = manager.get_memory(memory_id)
        assert memory is not None, f"Failed to get memory {i+1}"
        assert memory["id"] == memory_id, f"Memory ID mismatch for memory {i+1}"
        logger.info(f"Retrieved memory {i+1}: {memory['content']}")
    
    logger.info("Retrieving memories test passed.")


def test_search_memories(manager: MemoryManager):
    """Test searching for memories"""
    logger.info("Testing searching for memories...")
    
    # Search for memories related to AI assistants
    query = "AI assistants and memory"
    results = manager.search_memories(query, limit=2)
    
    # Check if results were returned
    assert len(results) > 0, "Expected at least one search result"
    
    # Display results
    logger.info(f"Search query: '{query}'")
    for i, result in enumerate(results):
        logger.info(f"Result {i+1}: {result['content']} (score: {result['score']:.4f})")
    
    # Try another search
    query = "vector embeddings"
    results = manager.search_memories(query, limit=2)
    
    # Check if results were returned
    assert len(results) > 0, "Expected at least one search result"
    
    # Display results
    logger.info(f"Search query: '{query}'")
    for i, result in enumerate(results):
        logger.info(f"Result {i+1}: {result['content']} (score: {result['score']:.4f})")
    
    logger.info("Searching memories test passed.")


def test_filter_metadata(manager: MemoryManager):
    """Test filtering memories by metadata"""
    logger.info("Testing filtering memories by metadata...")
    
    # Filter by topic
    filter_metadata = {"topic": "memory"}
    results = manager.list_memories(filter_metadata)
    
    # Check if results were returned
    assert len(results) > 0, "Expected at least one memory with topic 'memory'"
    
    # Display results
    logger.info(f"Filter by topic 'memory':")
    for i, result in enumerate(results):
        logger.info(f"Result {i+1}: {result['content']}")
    
    # Count memories by topic
    count = manager.count_memories(filter_metadata)
    logger.info(f"Count of memories with topic 'memory': {count}")
    
    logger.info("Filtering memories test passed.")


def test_update_memory(manager: MemoryManager, memory_ids: List[str]):
    """Test updating memories"""
    logger.info("Testing updating memories...")
    
    # Update the first memory
    memory_id = memory_ids[0]
    original = manager.get_memory(memory_id)
    
    # Update content
    new_content = original["content"] + " This is updated content."
    success = manager.update_memory(memory_id, content=new_content)
    assert success, "Failed to update memory content"
    
    # Get the updated memory
    updated = manager.get_memory(memory_id)
    assert updated["content"] == new_content, "Memory content was not updated"
    
    logger.info(f"Updated memory content: {updated['content']}")
    
    # Update metadata
    new_metadata = {**original["metadata"], "updated": True}
    success = manager.update_memory(memory_id, metadata=new_metadata)
    assert success, "Failed to update memory metadata"
    
    # Get the updated memory
    updated = manager.get_memory(memory_id)
    assert updated["metadata"].get("updated") is True, "Memory metadata was not updated"
    
    logger.info(f"Updated memory metadata: {updated['metadata']}")
    
    logger.info("Updating memories test passed.")


def test_delete_memories(manager: MemoryManager, memory_ids: List[str]):
    """Test deleting memories"""
    logger.info("Testing deleting memories...")
    
    # Delete each memory
    for i, memory_id in enumerate(memory_ids):
        success = manager.delete_memory(memory_id)
        assert success, f"Failed to delete memory {i+1}"
        logger.info(f"Deleted memory {i+1} with ID: {memory_id}")
    
    # Verify that the memories were deleted
    for i, memory_id in enumerate(memory_ids):
        memory = manager.get_memory(memory_id)
        assert memory is None, f"Memory {i+1} was not deleted"
    
    logger.info("Deleting memories test passed.")


def test_config_save_load():
    """Test saving and loading configuration"""
    logger.info("Testing saving and loading configuration...")
    
    # Create a custom configuration
    embedding_config = BaseEmbeddingConfig(
        provider="ollama",
        model_name="nomic-embed-text",
        dimensions=768
    )
    
    vector_store_config = VectorStoreConfig(
        provider="chroma",
        collection_name="test_collection_custom",
        dimensions=768
    )
    
    config = MemoryConfig(
        embedding=embedding_config,
        vector_store=vector_store_config
    )
    
    # Create a memory manager with the custom configuration
    manager = MemoryManager(config)
    
    # Save the configuration to a temporary file
    temp_file = f"/tmp/cliche_memory_config_{uuid.uuid4()}.json"
    success = manager.save_config(temp_file)
    assert success, "Failed to save configuration"
    logger.info(f"Saved configuration to {temp_file}")
    
    # Load the configuration from the file
    loaded_config = MemoryManager.load_config(temp_file)
    assert loaded_config is not None, "Failed to load configuration"
    
    # Create a new memory manager with the loaded configuration
    new_manager = MemoryManager(loaded_config)
    assert new_manager.is_ready(), "Memory manager with loaded configuration should be ready"
    
    # Clean up
    os.remove(temp_file)
    
    logger.info("Saving and loading configuration test passed.")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test the CLIche Memory Manager')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--skip-test', '-s', type=str, help='Skip a specific test (comma-separated)')
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    
    # Parse tests to skip
    skip_tests = []
    if args.skip_test:
        skip_tests = [test.strip() for test in args.skip_test.split(',')]
    
    logger.info("Starting memory manager tests...")
    
    try:
        # Run tests
        if 'init' not in skip_tests:
            manager = test_memory_manager_init()
        else:
            logger.info("Skipping memory manager initialization test")
            manager = MemoryManager()
        
        if 'add' not in skip_tests:
            memory_ids = test_add_memory(manager)
        else:
            logger.info("Skipping adding memories test")
            # Add a few test memories anyway for other tests
            memory_ids = []
            for i in range(4):
                memory_id = manager.add_memory(f"Test memory {i+1}", {"test": True})
                memory_ids.append(memory_id)
        
        if 'get' not in skip_tests:
            test_get_memory(manager, memory_ids)
        else:
            logger.info("Skipping retrieving memories test")
        
        if 'search' not in skip_tests:
            test_search_memories(manager)
        else:
            logger.info("Skipping searching memories test")
        
        if 'filter' not in skip_tests:
            test_filter_metadata(manager)
        else:
            logger.info("Skipping filtering memories test")
        
        if 'update' not in skip_tests:
            test_update_memory(manager, memory_ids)
        else:
            logger.info("Skipping updating memories test")
        
        if 'delete' not in skip_tests:
            test_delete_memories(manager, memory_ids)
        else:
            logger.info("Skipping deleting memories test")
            # Clean up anyway
            for memory_id in memory_ids:
                manager.delete_memory(memory_id)
        
        if 'config' not in skip_tests:
            test_config_save_load()
        else:
            logger.info("Skipping configuration test")
        
        logger.info("All tests passed successfully!")
        
    except AssertionError as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 