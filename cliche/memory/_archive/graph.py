"""
Graph Memory for CLIche

Provides a graph-based memory system for tracking relationships between entities.

Made with ❤️ by Pink Pixel
"""
import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .types import Entity, EntityType, MemoryItem, Relationship, RelationshipType

logger = logging.getLogger(__name__)


class MemoryGraph:
    """Graph-based memory system for tracking relationships between entities."""
    
    def __init__(self, config=None):
        """
        Initialize the memory graph
        
        Args:
            config: Configuration for the memory graph (dictionary or None)
        """
        # Ensure config is a dictionary
        if config is None:
            config = {}
        elif not isinstance(config, dict):
            try:
                # Try to convert config to a dict if it has a get method
                if hasattr(config, "get") and callable(config.get):
                    # It's a config-like object, use it directly for accessing
                    pass
                else:
                    # Try to convert to dict
                    config = dict(config)
            except (TypeError, ValueError):
                logger.warning("Invalid config type for MemoryGraph, using defaults")
                config = {}
                
        # Define a safe getter function
        def safe_get(obj, key, default=None):
            try:
                if isinstance(obj, dict):
                    return obj.get(key, default)
                elif hasattr(obj, "get") and callable(obj.get):
                    return obj.get(key, default)
                else:
                    return default
            except:
                return default
        
        # Extract configuration
        self.data_dir = os.path.expanduser(safe_get(config, "data_dir", "~/.config/cliche/memory/graph"))
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize the database
        self.db_path = os.path.join(self.data_dir, "graph.db")
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.lock = threading.Lock()
        
        # Initialize the database schema
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema"""
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                # Create entities table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS entities (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        properties TEXT,
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL
                    )
                ''')
                
                # Create relationships table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS relationships (
                        id TEXT PRIMARY KEY,
                        source_id TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        type TEXT NOT NULL,
                        properties TEXT,
                        bidirectional INTEGER NOT NULL,
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL,
                        FOREIGN KEY (source_id) REFERENCES entities (id) ON DELETE CASCADE,
                        FOREIGN KEY (target_id) REFERENCES entities (id) ON DELETE CASCADE
                    )
                ''')
                
                # Create memory_entities table (to link memories to entities)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memory_entities (
                        memory_id TEXT NOT NULL,
                        entity_id TEXT NOT NULL,
                        created_at INTEGER NOT NULL,
                        PRIMARY KEY (memory_id, entity_id),
                        FOREIGN KEY (entity_id) REFERENCES entities (id) ON DELETE CASCADE
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_name ON entities (name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_type ON entities (type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships (source_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships (target_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships (type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_entities_memory ON memory_entities (memory_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_entities_entity ON memory_entities (entity_id)')
                
                self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to initialize graph database: {str(e)}")
            raise
    
    def add_entity(self, entity: Union[Entity, Dict[str, Any]]) -> str:
        """
        Add an entity to the graph
        
        Args:
            entity: Entity to add
            
        Returns:
            ID of the added entity
        """
        try:
            # Convert dict to Entity if needed
            if isinstance(entity, dict):
                entity = Entity.from_dict(entity)
            
            # Generate ID if not provided
            if not entity.id:
                entity.id = str(uuid.uuid4())
            
            # Update timestamps
            current_time = int(time.time())
            entity.updated_at = current_time
            if not entity.created_at:
                entity.created_at = current_time
            
            # Convert properties to JSON
            properties_json = json.dumps(entity.properties)
            
            with self.lock:
                cursor = self.connection.cursor()
                
                # Check if entity exists (by name and type)
                cursor.execute(
                    '''
                    SELECT id FROM entities 
                    WHERE name = ? AND type = ?
                    ''',
                    (entity.name, entity.type.value)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing entity
                    entity_id = existing[0]
                    cursor.execute(
                        '''
                        UPDATE entities
                        SET properties = ?, updated_at = ?
                        WHERE id = ?
                        ''',
                        (properties_json, entity.updated_at, entity_id)
                    )
                else:
                    # Insert new entity
                    entity_id = entity.id
                    cursor.execute(
                        '''
                        INSERT INTO entities
                        (id, name, type, properties, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''',
                        (
                            entity_id,
                            entity.name,
                            entity.type.value,
                            properties_json,
                            entity.created_at,
                            entity.updated_at
                        )
                    )
                
                self.connection.commit()
            
            return entity_id
        except Exception as e:
            logger.error(f"Failed to add entity: {str(e)}")
            raise
    
    def add_relationship(self, relationship: Union[Relationship, Dict[str, Any]]) -> str:
        """
        Add a relationship to the graph
        
        Args:
            relationship: Relationship to add
            
        Returns:
            ID of the added relationship
        """
        try:
            # Convert dict to Relationship if needed
            if isinstance(relationship, dict):
                relationship = Relationship.from_dict(relationship)
            
            # Generate ID if not provided
            if not relationship.id:
                relationship.id = str(uuid.uuid4())
            
            # Update timestamps
            current_time = int(time.time())
            relationship.updated_at = current_time
            if not relationship.created_at:
                relationship.created_at = current_time
            
            # Convert properties to JSON
            properties_json = json.dumps(relationship.properties)
            
            with self.lock:
                cursor = self.connection.cursor()
                
                # Check if entities exist
                for entity_id in [relationship.source_id, relationship.target_id]:
                    cursor.execute('SELECT id FROM entities WHERE id = ?', (entity_id,))
                    if not cursor.fetchone():
                        raise ValueError(f"Entity {entity_id} does not exist")
                
                # Check if relationship exists
                cursor.execute(
                    '''
                    SELECT id FROM relationships 
                    WHERE source_id = ? AND target_id = ? AND type = ?
                    ''',
                    (relationship.source_id, relationship.target_id, relationship.type.value)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing relationship
                    relationship_id = existing[0]
                    cursor.execute(
                        '''
                        UPDATE relationships
                        SET properties = ?, bidirectional = ?, updated_at = ?
                        WHERE id = ?
                        ''',
                        (
                            properties_json,
                            1 if relationship.bidirectional else 0,
                            relationship.updated_at,
                            relationship_id
                        )
                    )
                else:
                    # Insert new relationship
                    relationship_id = relationship.id
                    cursor.execute(
                        '''
                        INSERT INTO relationships
                        (id, source_id, target_id, type, properties, bidirectional, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''',
                        (
                            relationship_id,
                            relationship.source_id,
                            relationship.target_id,
                            relationship.type.value,
                            properties_json,
                            1 if relationship.bidirectional else 0,
                            relationship.created_at,
                            relationship.updated_at
                        )
                    )
                
                self.connection.commit()
            
            return relationship_id
        except Exception as e:
            logger.error(f"Failed to add relationship: {str(e)}")
            raise
    
    def link_memory_to_entity(self, memory_id: str, entity_id: str) -> bool:
        """
        Link a memory to an entity
        
        Args:
            memory_id: ID of the memory
            entity_id: ID of the entity
            
        Returns:
            True if the link was created, False otherwise
        """
        try:
            # Check if entity exists
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute('SELECT id FROM entities WHERE id = ?', (entity_id,))
                if not cursor.fetchone():
                    logger.warning(f"Entity {entity_id} does not exist")
                    return False
                
                # Create the link if it doesn't exist
                cursor.execute(
                    '''
                    SELECT memory_id FROM memory_entities
                    WHERE memory_id = ? AND entity_id = ?
                    ''',
                    (memory_id, entity_id)
                )
                
                if not cursor.fetchone():
                    cursor.execute(
                        '''
                        INSERT INTO memory_entities
                        (memory_id, entity_id, created_at)
                        VALUES (?, ?, ?)
                        ''',
                        (memory_id, entity_id, int(time.time()))
                    )
                    
                    self.connection.commit()
                
                return True
        except Exception as e:
            logger.error(f"Failed to link memory to entity: {str(e)}")
            return False
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Entity if found, None otherwise
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute(
                    '''
                    SELECT id, name, type, properties, created_at, updated_at
                    FROM entities
                    WHERE id = ?
                    ''',
                    (entity_id,)
                )
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                entity_id, name, entity_type, properties_json, created_at, updated_at = row
                
                # Parse properties
                properties = json.loads(properties_json) if properties_json else {}
                
                # Create entity
                try:
                    type_enum = EntityType(entity_type)
                except ValueError:
                    type_enum = EntityType.OTHER
                
                return Entity(
                    id=entity_id,
                    name=name,
                    type=type_enum,
                    properties=properties,
                    created_at=created_at,
                    updated_at=updated_at
                )
        except Exception as e:
            logger.error(f"Failed to get entity: {str(e)}")
            return None
    
    def get_entities_by_name(self, name: str, entity_type: Optional[EntityType] = None) -> List[Entity]:
        """
        Get entities by name and optional type
        
        Args:
            name: Name of the entity
            entity_type: Type of the entity (optional)
            
        Returns:
            List of matching entities
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                if entity_type:
                    cursor.execute(
                        '''
                        SELECT id, name, type, properties, created_at, updated_at
                        FROM entities
                        WHERE name = ? AND type = ?
                        ''',
                        (name, entity_type.value)
                    )
                else:
                    cursor.execute(
                        '''
                        SELECT id, name, type, properties, created_at, updated_at
                        FROM entities
                        WHERE name = ?
                        ''',
                        (name,)
                    )
                
                rows = cursor.fetchall()
                
                entities = []
                for row in rows:
                    entity_id, name, entity_type, properties_json, created_at, updated_at = row
                    
                    # Parse properties
                    properties = json.loads(properties_json) if properties_json else {}
                    
                    # Create entity
                    try:
                        type_enum = EntityType(entity_type)
                    except ValueError:
                        type_enum = EntityType.OTHER
                    
                    entities.append(Entity(
                        id=entity_id,
                        name=name,
                        type=type_enum,
                        properties=properties,
                        created_at=created_at,
                        updated_at=updated_at
                    ))
                
                return entities
        except Exception as e:
            logger.error(f"Failed to get entities by name: {str(e)}")
            return []
    
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """
        Get a relationship by ID
        
        Args:
            relationship_id: ID of the relationship
            
        Returns:
            Relationship if found, None otherwise
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute(
                    '''
                    SELECT id, source_id, target_id, type, properties, bidirectional, created_at, updated_at
                    FROM relationships
                    WHERE id = ?
                    ''',
                    (relationship_id,)
                )
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                rel_id, source_id, target_id, rel_type, properties_json, bidirectional, created_at, updated_at = row
                
                # Parse properties
                properties = json.loads(properties_json) if properties_json else {}
                
                # Create relationship
                try:
                    type_enum = RelationshipType(rel_type)
                except ValueError:
                    type_enum = RelationshipType.OTHER
                
                return Relationship(
                    id=rel_id,
                    source_id=source_id,
                    target_id=target_id,
                    type=type_enum,
                    properties=properties,
                    bidirectional=bool(bidirectional),
                    created_at=created_at,
                    updated_at=updated_at
                )
        except Exception as e:
            logger.error(f"Failed to get relationship: {str(e)}")
            return None
    
    def get_relationships(
        self,
        entity_id: str,
        relationship_type: Optional[RelationshipType] = None,
        direction: str = "both"
    ) -> List[Relationship]:
        """
        Get relationships for an entity
        
        Args:
            entity_id: ID of the entity
            relationship_type: Type of relationship (optional)
            direction: Direction of the relationship ('outgoing', 'incoming', or 'both')
            
        Returns:
            List of relationships
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                queries = []
                params = []
                
                # Outgoing relationships (entity is source)
                if direction in ["outgoing", "both"]:
                    if relationship_type:
                        queries.append(
                            '''
                            SELECT id, source_id, target_id, type, properties, bidirectional, created_at, updated_at
                            FROM relationships
                            WHERE source_id = ? AND type = ?
                            '''
                        )
                        params.append((entity_id, relationship_type.value))
                    else:
                        queries.append(
                            '''
                            SELECT id, source_id, target_id, type, properties, bidirectional, created_at, updated_at
                            FROM relationships
                            WHERE source_id = ?
                            '''
                        )
                        params.append((entity_id,))
                
                # Incoming relationships (entity is target)
                if direction in ["incoming", "both"]:
                    if relationship_type:
                        queries.append(
                            '''
                            SELECT id, source_id, target_id, type, properties, bidirectional, created_at, updated_at
                            FROM relationships
                            WHERE target_id = ? AND type = ?
                            '''
                        )
                        params.append((entity_id, relationship_type.value))
                    else:
                        queries.append(
                            '''
                            SELECT id, source_id, target_id, type, properties, bidirectional, created_at, updated_at
                            FROM relationships
                            WHERE target_id = ?
                            '''
                        )
                        params.append((entity_id,))
                
                relationships = []
                relationship_ids = set()  # To avoid duplicates
                
                for query, param in zip(queries, params):
                    cursor.execute(query, param)
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        rel_id, source_id, target_id, rel_type, properties_json, bidirectional, created_at, updated_at = row
                        
                        # Skip if already added
                        if rel_id in relationship_ids:
                            continue
                        
                        relationship_ids.add(rel_id)
                        
                        # Parse properties
                        properties = json.loads(properties_json) if properties_json else {}
                        
                        # Create relationship
                        try:
                            type_enum = RelationshipType(rel_type)
                        except ValueError:
                            type_enum = RelationshipType.OTHER
                        
                        relationships.append(Relationship(
                            id=rel_id,
                            source_id=source_id,
                            target_id=target_id,
                            type=type_enum,
                            properties=properties,
                            bidirectional=bool(bidirectional),
                            created_at=created_at,
                            updated_at=updated_at
                        ))
                
                return relationships
        except Exception as e:
            logger.error(f"Failed to get relationships: {str(e)}")
            return []
    
    def get_connected_entities(
        self,
        entity_id: str,
        relationship_type: Optional[RelationshipType] = None,
        entity_type: Optional[EntityType] = None,
        direction: str = "both"
    ) -> List[Entity]:
        """
        Get entities connected to the given entity
        
        Args:
            entity_id: ID of the entity
            relationship_type: Type of relationship (optional)
            entity_type: Type of entity to return (optional)
            direction: Direction of the relationship ('outgoing', 'incoming', or 'both')
            
        Returns:
            List of connected entities
        """
        try:
            # Get relationships
            relationships = self.get_relationships(entity_id, relationship_type, direction)
            
            # Extract connected entity IDs
            connected_ids = []
            for rel in relationships:
                if rel.source_id == entity_id:
                    connected_ids.append(rel.target_id)
                else:
                    connected_ids.append(rel.source_id)
            
            # No connected entities
            if not connected_ids:
                return []
            
            # Get entities
            with self.lock:
                cursor = self.connection.cursor()
                
                placeholders = ", ".join(["?"] * len(connected_ids))
                
                if entity_type:
                    query = f'''
                        SELECT id, name, type, properties, created_at, updated_at
                        FROM entities
                        WHERE id IN ({placeholders}) AND type = ?
                    '''
                    params = connected_ids + [entity_type.value]
                else:
                    query = f'''
                        SELECT id, name, type, properties, created_at, updated_at
                        FROM entities
                        WHERE id IN ({placeholders})
                    '''
                    params = connected_ids
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                entities = []
                for row in rows:
                    entity_id, name, entity_type, properties_json, created_at, updated_at = row
                    
                    # Parse properties
                    properties = json.loads(properties_json) if properties_json else {}
                    
                    # Create entity
                    try:
                        type_enum = EntityType(entity_type)
                    except ValueError:
                        type_enum = EntityType.OTHER
                    
                    entities.append(Entity(
                        id=entity_id,
                        name=name,
                        type=type_enum,
                        properties=properties,
                        created_at=created_at,
                        updated_at=updated_at
                    ))
                
                return entities
        except Exception as e:
            logger.error(f"Failed to get connected entities: {str(e)}")
            return []
    
    def get_entities_for_memory(self, memory_id: str) -> List[Entity]:
        """
        Get entities linked to a memory
        
        Args:
            memory_id: ID of the memory
            
        Returns:
            List of entities linked to the memory
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute(
                    '''
                    SELECT e.id, e.name, e.type, e.properties, e.created_at, e.updated_at
                    FROM entities e
                    JOIN memory_entities me ON e.id = me.entity_id
                    WHERE me.memory_id = ?
                    ''',
                    (memory_id,)
                )
                
                rows = cursor.fetchall()
                
                entities = []
                for row in rows:
                    entity_id, name, entity_type, properties_json, created_at, updated_at = row
                    
                    # Parse properties
                    properties = json.loads(properties_json) if properties_json else {}
                    
                    # Create entity
                    try:
                        type_enum = EntityType(entity_type)
                    except ValueError:
                        type_enum = EntityType.OTHER
                    
                    entities.append(Entity(
                        id=entity_id,
                        name=name,
                        type=type_enum,
                        properties=properties,
                        created_at=created_at,
                        updated_at=updated_at
                    ))
                
                return entities
        except Exception as e:
            logger.error(f"Failed to get entities for memory: {str(e)}")
            return []
    
    def clear(self) -> bool:
        """
        Clear all data from the graph
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                cursor = self.connection.cursor()
                
                cursor.execute('DELETE FROM memory_entities')
                cursor.execute('DELETE FROM relationships')
                cursor.execute('DELETE FROM entities')
                
                self.connection.commit()
                
                return True
        except Exception as e:
            logger.error(f"Failed to clear graph: {str(e)}")
            return False
    
    def __del__(self):
        """Clean up resources on deletion"""
        try:
            if hasattr(self, 'connection'):
                self.connection.close()
        except Exception:
            pass 