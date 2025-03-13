#!/usr/bin/env python
"""
Test script for CLIche memory system.

This script tests the memory system directly through the CLIche instance.

Made with ❤️ by Pink Pixel
"""
import sys
import os
import logging
import uuid
from pathlib import Path

# Add parent directory to path to import cliche
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cliche.core import get_cliche_instance

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("memory_test")

def test_memory_system():
    """Test memory system directly through the CLIche instance"""
    cliche = get_cliche_instance()
    
    logger.info("Getting memory status...")
    status = cliche.memory.get_status()
    logger.info(f"Memory status: {status}")
    
    logger.info("Enabling memory system...")
    enabled = cliche.memory.toggle(True)
    logger.info(f"Memory system enabled: {enabled}")
    
    # Generate a unique test ID to help with cleanup
    test_id = str(uuid.uuid4())[:8]
    logger.info(f"Using test ID: {test_id}")
    
    logger.info("Adding memories...")
    
    # Add a simple memory
    memory1_id = cliche.memory.add(
        f"This is test memory 1 with ID {test_id}",
        metadata={"test_id": test_id, "type": "test_memory"}
    )
    logger.info(f"Added memory 1, ID: {memory1_id}")
    
    # Add a memory with tags as a string
    memory2_id = cliche.memory.add(
        f"This is test memory 2 with ID {test_id} and tags",
        metadata={"test_id": test_id, "tags": "test,memory,cliche", "type": "test_memory"}
    )
    logger.info(f"Added memory 2, ID: {memory2_id}")
    
    logger.info("Searching for memories...")
    search_results = cliche.memory.search(f"test memory {test_id}", limit=5)
    logger.info(f"Found {len(search_results)} memories for test ID {test_id}")
    
    for i, memory in enumerate(search_results):
        logger.info(f"Memory {i+1}: {memory.get('content', 'No content')}")
        logger.info(f"  ID: {memory.get('id', 'unknown')}")
        logger.info(f"  Metadata: {memory.get('metadata', {})}")
    
    logger.info("Testing memory removal...")
    if memory2_id:
        success = cliche.memory.remove_memory(memory2_id)
        logger.info(f"Removed memory 2: {success}")
    
    # Clean up test memories
    logger.info("Cleaning up test memories...")
    cleanup_results = cliche.memory.search(f"test_id:{test_id}", limit=10)
    removed_count = 0
    
    for memory in cleanup_results:
        memory_id = memory.get("id", None)
        if memory_id:
            success = cliche.memory.remove_memory(memory_id)
            if success:
                removed_count += 1
    
    logger.info(f"Cleaned up {removed_count} test memories")
    logger.info("Memory system tests completed successfully!")

if __name__ == "__main__":
    print("Starting memory system tests...")
    test_memory_system()
    print("Memory system tests completed!") 