"""
Shared types and classes for CLIche Memory System

Defines common types used across the memory system.

Made with ❤️ by Pink Pixel
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Set


class MemoryCategory(Enum):
    """Categories for memory classification"""
    PREFERENCE = "preference"
    FACT = "fact"
    PLAN = "plan"
    RELATIONSHIP = "relationship"
    PERSONAL_INFO = "personal_info"
    GOAL = "goal"
    OPINION = "opinion"
    OTHER = "other"


class EntityType(Enum):
    """Types of entities in the memory graph"""
    PERSON = "person"
    PLACE = "place"
    THING = "thing"
    CONCEPT = "concept"
    EVENT = "event"
    DATETIME = "datetime"
    ORGANIZATION = "organization"
    OTHER = "other"


class RelationshipType(Enum):
    """Types of relationships in the memory graph"""
    HAS = "has"
    IS = "is"
    KNOWS = "knows"
    LIKES = "likes"
    DISLIKES = "dislikes"
    WANTS = "wants"
    OWNS = "owns"
    LOCATED_AT = "located_at"
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    BEFORE = "before"
    AFTER = "after"
    DURING = "during"
    CAUSES = "causes"
    OTHER = "other"


@dataclass
class MemoryItem:
    """A memory item with content and metadata"""
    id: str
    content: str
    category: MemoryCategory
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    updated_at: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create from dictionary"""
        # Convert category value to enum
        category = data.get("category", "other")
        try:
            category_enum = MemoryCategory(category)
        except ValueError:
            category_enum = MemoryCategory.OTHER
        
        return cls(
            id=data.get("id", ""),
            content=data.get("content", ""),
            category=category_enum,
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
            created_at=data.get("created_at", int(datetime.now().timestamp())),
            updated_at=data.get("updated_at", int(datetime.now().timestamp()))
        )


@dataclass
class Entity:
    """An entity in the memory graph"""
    id: str
    name: str
    type: EntityType
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    updated_at: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create from dictionary"""
        # Convert type value to enum
        entity_type = data.get("type", "other")
        try:
            type_enum = EntityType(entity_type)
        except ValueError:
            type_enum = EntityType.OTHER
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=type_enum,
            properties=data.get("properties", {}),
            created_at=data.get("created_at", int(datetime.now().timestamp())),
            updated_at=data.get("updated_at", int(datetime.now().timestamp()))
        )


@dataclass
class Relationship:
    """A relationship in the memory graph"""
    id: str
    source_id: str
    target_id: str
    type: RelationshipType
    properties: Dict[str, Any] = field(default_factory=dict)
    bidirectional: bool = False
    created_at: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    updated_at: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            "properties": self.properties,
            "bidirectional": self.bidirectional,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create from dictionary"""
        # Convert type value to enum
        rel_type = data.get("type", "other")
        try:
            type_enum = RelationshipType(rel_type)
        except ValueError:
            type_enum = RelationshipType.OTHER
        
        return cls(
            id=data.get("id", ""),
            source_id=data.get("source_id", ""),
            target_id=data.get("target_id", ""),
            type=type_enum,
            properties=data.get("properties", {}),
            bidirectional=data.get("bidirectional", False),
            created_at=data.get("created_at", int(datetime.now().timestamp())),
            updated_at=data.get("updated_at", int(datetime.now().timestamp()))
        ) 