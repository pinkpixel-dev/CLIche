"""
Memory Utilities for CLIche

Provides utility functions for working with the memory system.

Made with ❤️ by Pink Pixel
"""
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .types import Entity, EntityType, MemoryCategory, MemoryItem, Relationship, RelationshipType

logger = logging.getLogger(__name__)


def format_memory_for_display(memory: MemoryItem, include_metadata: bool = False) -> str:
    """
    Format a memory for display
    
    Args:
        memory: The memory to format
        include_metadata: Whether to include metadata
        
    Returns:
        Formatted memory string
    """
    try:
        # Format the creation time
        created_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(memory.created_at))
        
        # Basic format
        result = f"[{memory.category.value}] {memory.content} (Created: {created_time})"
        
        # Add metadata if requested
        if include_metadata and memory.metadata:
            meta_str = json.dumps(memory.metadata, indent=2)
            result += f"\nMetadata: {meta_str}"
        
        return result
    except Exception as e:
        logger.error(f"Error formatting memory: {str(e)}")
        return str(memory.content)


def format_entity_for_display(entity: Entity, include_properties: bool = False) -> str:
    """
    Format an entity for display
    
    Args:
        entity: The entity to format
        include_properties: Whether to include properties
        
    Returns:
        Formatted entity string
    """
    try:
        # Basic format
        result = f"[{entity.type.value}] {entity.name}"
        
        # Add properties if requested
        if include_properties and entity.properties:
            # Filter out system properties
            display_props = {k: v for k, v in entity.properties.items() if not k.startswith("_")}
            if display_props:
                props_str = json.dumps(display_props, indent=2)
                result += f"\nProperties: {props_str}"
        
        return result
    except Exception as e:
        logger.error(f"Error formatting entity: {str(e)}")
        return str(entity.name)


def format_relationship_for_display(
    relationship: Relationship,
    source_name: Optional[str] = None,
    target_name: Optional[str] = None,
    include_properties: bool = False
) -> str:
    """
    Format a relationship for display
    
    Args:
        relationship: The relationship to format
        source_name: Name of the source entity (if available)
        target_name: Name of the target entity (if available)
        include_properties: Whether to include properties
        
    Returns:
        Formatted relationship string
    """
    try:
        # Source and target
        source = source_name or relationship.source_id
        target = target_name or relationship.target_id
        
        # Relationship type
        rel_type = relationship.type.value
        
        # Format based on directionality
        if relationship.bidirectional:
            result = f"{source} <-[{rel_type}]-> {target}"
        else:
            result = f"{source} -[{rel_type}]-> {target}"
        
        # Add properties if requested
        if include_properties and relationship.properties:
            # Filter out system properties
            display_props = {k: v for k, v in relationship.properties.items() if not k.startswith("_")}
            if display_props:
                props_str = json.dumps(display_props, indent=2)
                result += f"\nProperties: {props_str}"
        
        return result
    except Exception as e:
        logger.error(f"Error formatting relationship: {str(e)}")
        return f"{relationship.source_id} -> {relationship.target_id}"


def format_memories_as_context(
    memories: List[MemoryItem],
    include_categories: bool = True,
    max_length: Optional[int] = None
) -> str:
    """
    Format a list of memories as context for an LLM
    
    Args:
        memories: List of memories
        include_categories: Whether to include categories
        max_length: Maximum length of the context
        
    Returns:
        Formatted memories string
    """
    if not memories:
        return ""
    
    try:
        formatted_memories = []
        
        for memory in memories:
            if include_categories:
                mem_str = f"[{memory.category.value}] {memory.content}"
            else:
                mem_str = memory.content
            
            formatted_memories.append(mem_str)
        
        result = "\n\n".join(formatted_memories)
        
        # Truncate if needed
        if max_length and len(result) > max_length:
            result = result[:max_length-3] + "..."
        
        return result
    except Exception as e:
        logger.error(f"Error formatting memories as context: {str(e)}")
        return "\n\n".join([m.content for m in memories])


def extract_keywords(text: str, min_length: int = 3, max_count: int = 20) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Input text
        min_length: Minimum keyword length
        max_count: Maximum number of keywords
        
    Returns:
        List of keywords
    """
    try:
        # Remove special characters and convert to lowercase
        cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words
        words = cleaned_text.split()
        
        # Count word frequency
        word_count = {}
        for word in words:
            if len(word) >= min_length:
                word_count[word] = word_count.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        
        # Return top keywords
        return [word for word, count in sorted_words[:max_count]]
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return []


def generate_memory_stats(
    memory_count: int,
    category_counts: Dict[str, int],
    entity_count: int,
    relationship_count: int
) -> str:
    """
    Generate memory system statistics
    
    Args:
        memory_count: Total number of memories
        category_counts: Count of memories by category
        entity_count: Total number of entities
        relationship_count: Total number of relationships
        
    Returns:
        Formatted statistics string
    """
    try:
        stats = [
            "Memory System Statistics",
            "========================",
            f"Total Memories: {memory_count}",
            "",
            "Memory Categories:",
        ]
        
        # Add category counts
        for category, count in category_counts.items():
            stats.append(f"  - {category}: {count}")
        
        # Add entity and relationship counts
        stats.append("")
        stats.append(f"Total Entities: {entity_count}")
        stats.append(f"Total Relationships: {relationship_count}")
        
        return "\n".join(stats)
    except Exception as e:
        logger.error(f"Error generating memory stats: {str(e)}")
        return f"Memory Count: {memory_count}"


def create_memory_backup(data_dir: str, backup_dir: Optional[str] = None) -> Optional[str]:
    """
    Create a backup of memory database files
    
    Args:
        data_dir: Directory containing the memory data
        backup_dir: Directory to store the backup (defaults to data_dir/backups)
        
    Returns:
        Path to the backup directory if successful, None otherwise
    """
    try:
        import shutil
        from datetime import datetime
        
        # Set default backup directory
        if not backup_dir:
            backup_dir = os.path.join(data_dir, "backups")
        
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create timestamped backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"memory_backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        # Find database files
        db_files = []
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.endswith(".db") or file.endswith(".sqlite") or file.endswith(".sqlite3"):
                    db_files.append(os.path.join(root, file))
        
        if not db_files:
            logger.warning(f"No database files found in {data_dir}")
            return None
        
        # Copy database files to backup directory
        for db_file in db_files:
            rel_path = os.path.relpath(db_file, data_dir)
            backup_file = os.path.join(backup_path, rel_path)
            
            # Create directory structure
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            
            # Copy file
            shutil.copy2(db_file, backup_file)
            logger.info(f"Backed up {db_file} to {backup_file}")
        
        return backup_path
    except Exception as e:
        logger.error(f"Error creating memory backup: {str(e)}")
        return None 