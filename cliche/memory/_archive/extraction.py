"""
Memory extraction module for CLIche

Handles the extraction of facts, preferences, and other information from user conversations.

Made with ❤️ by Pink Pixel
"""
import json
import logging
import re
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime

from .types import Entity, EntityType, Relationship, RelationshipType

logger = logging.getLogger(__name__)

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

class MemoryExtractor:
    """Extracts memories from conversations using LLM."""
    
    def __init__(self, llm_provider=None):
        """
        Initialize the memory extractor
        
        Args:
            llm_provider: LLM provider to use for extraction (can be None for basic functionality)
        """
        self.llm = llm_provider
        logger.info(f"Initialized MemoryExtractor with LLM provider: {llm_provider.__class__.__name__ if llm_provider else 'None'}")
        
    def extract_facts(self, conversation: str) -> List[Dict[str, Any]]:
        """
        Extract facts from a conversation
        
        Args:
            conversation: The conversation text to analyze
            
        Returns:
            List of extracted facts with metadata
        """
        # If no LLM provider is available, use a simple rule-based approach
        if not self.llm:
            logger.warning("No LLM provider available, using basic fact extraction")
            return self._basic_extract_facts(conversation)
            
        try:
            return self._extract_facts_from_text(conversation)
        except Exception as e:
            logger.error(f"Error extracting facts with LLM: {str(e)}")
            # Fall back to basic extraction on error
            return self._basic_extract_facts(conversation)
            
    def _basic_extract_facts(self, text: str) -> List[Dict[str, Any]]:
        """Simple rule-based fact extraction when LLM is not available"""
        facts = []
        
        # Extract simple "I am X" or "My X is Y" statements
        i_am_pattern = re.compile(r"I am ([^.,!?]+)")
        my_is_pattern = re.compile(r"My ([^.,!?]+) is ([^.,!?]+)")
        
        # Find "I am X" statements
        for match in i_am_pattern.finditer(text):
            statement = match.group(1).strip()
            if len(statement) > 2:  # Avoid very short statements
                facts.append({
                    "content": f"I am {statement}",
                    "metadata": {
                        "category": MemoryCategory.PERSONAL_INFO.value,
                        "confidence": 0.7,
                        "extracted_by": "rule_based"
                    }
                })
                
        # Find "My X is Y" statements
        for match in my_is_pattern.finditer(text):
            attribute = match.group(1).strip()
            value = match.group(2).strip()
            if len(attribute) > 2 and len(value) > 2:
                facts.append({
                    "content": f"My {attribute} is {value}",
                    "metadata": {
                        "category": MemoryCategory.PERSONAL_INFO.value,
                        "confidence": 0.7,
                        "extracted_by": "rule_based"
                    }
                })
                
        return facts
    
    def _extract_facts_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract facts from text when JSON parsing fails
        
        Args:
            text: Text to extract facts from
            
        Returns:
            List of extracted facts with metadata
        """
        facts = []
        
        # Try to find bullet points or numbered lists
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Check for bullet points or numbers
            if re.match(r'^[\-\*•]|^\d+\.', line):
                # Remove the bullet or number
                fact = re.sub(r'^[\-\*•]|^\d+\.', '', line).strip()
                if fact:
                    facts.append(self._process_fact(fact))
        
        # If no bullet points found, try to split by sentences
        if not facts:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:  # Avoid very short sentences
                    facts.append(self._process_fact(sentence))
        
        return facts
    
    def _process_fact(self, fact: str) -> Dict[str, Any]:
        """
        Process an extracted fact with metadata
        
        Args:
            fact: The fact to process
            
        Returns:
            Processed fact with metadata
        """
        category = self.categorize_memory(fact)
        
        return {
            "content": fact,
            "category": category.value,
            "metadata": {
                "extracted_at": datetime.now().isoformat(),
                "confidence": self._calculate_confidence(fact),
                "type": "extracted_fact",
                "category": category.value
            }
        }
    
    def categorize_memory(self, fact: str) -> MemoryCategory:
        """
        Categorize a memory based on its content
        
        Args:
            fact: The fact to categorize
            
        Returns:
            Category of the memory
        """
        # Simple rule-based categorization
        fact_lower = fact.lower()
        
        # Preference patterns
        if any(pattern in fact_lower for pattern in ["prefer", "like", "love", "enjoy", "favorite", "favourite"]):
            return MemoryCategory.PREFERENCE
        
        # Personal info patterns
        if any(pattern in fact_lower for pattern in ["name is", "live in", "from", "age", "birthday", "born"]):
            return MemoryCategory.PERSONAL_INFO
        
        # Plan patterns
        if any(pattern in fact_lower for pattern in ["plan", "schedule", "appointment", "meeting", "tomorrow", "next week"]):
            return MemoryCategory.PLAN
        
        # Relationship patterns
        if any(pattern in fact_lower for pattern in ["friend", "family", "parent", "child", "spouse", "partner", "colleague"]):
            return MemoryCategory.RELATIONSHIP
        
        # Goal patterns
        if any(pattern in fact_lower for pattern in ["goal", "aim", "objective", "target", "aspire", "want to", "would like to"]):
            return MemoryCategory.GOAL
        
        # Opinion patterns
        if any(pattern in fact_lower for pattern in ["think", "believe", "opinion", "feel", "view"]):
            return MemoryCategory.OPINION
        
        # Default to fact if no specific category is matched
        return MemoryCategory.FACT
    
    def _calculate_confidence(self, fact: str) -> float:
        """
        Calculate confidence score for an extracted fact
        
        Args:
            fact: The fact to calculate confidence for
            
        Returns:
            Confidence score between 0 and 1
        """
        # Simple heuristic based on length and specificity
        # In a real implementation, this would use more sophisticated methods
        
        # Longer facts tend to be more specific and reliable
        length_score = min(1.0, len(fact) / 100)
        
        # Facts with specific details tend to be more reliable
        specificity_indicators = [
            "on", "at", "in", "because", "since", "when", "where", "who", "what", "how",
            "always", "never", "sometimes", "often", "rarely", "usually", "frequently",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"
        ]
        
        specificity_score = 0.0
        for indicator in specificity_indicators:
            if indicator in fact.lower():
                specificity_score += 0.1
        
        specificity_score = min(1.0, specificity_score)
        
        # Combine scores with weights
        return 0.4 + (0.3 * length_score) + (0.3 * specificity_score)
    
    def _get_fact_extraction_prompt(self) -> str:
        """
        Get the prompt for fact extraction
        
        Returns:
            Prompt for fact extraction
        """
        return """You are a Personal Information Organizer, specialized in accurately storing facts, user memories, and preferences. Your primary role is to extract relevant pieces of information from conversations and organize them into distinct, manageable facts.

Types of Information to Remember:

1. Store Personal Preferences: Keep track of likes, dislikes, and specific preferences in various categories.
2. Maintain Important Personal Details: Remember significant personal information like names, relationships, and important dates.
3. Track Plans and Intentions: Note upcoming events, trips, goals, and any plans the user has shared.
4. Remember Activity and Service Preferences: Recall preferences for dining, travel, hobbies, and other services.
5. Monitor Health and Wellness Preferences: Keep a record of dietary restrictions, fitness routines, and other wellness-related information.
6. Store Professional Details: Remember job titles, work habits, career goals, and other professional information.
7. Miscellaneous Information Management: Keep track of favorite books, movies, brands, and other miscellaneous details.

Return the facts and preferences in a JSON format with a "facts" key containing an array of strings.

If you do not find anything relevant in the conversation, return an empty list.

Example output format:
{
  "facts": [
    "User likes pizza",
    "User is a software engineer",
    "User plans to visit Paris next summer"
  ]
}
"""

    def detect_memory_request(self, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Detect if a query is explicitly asking to remember something
        
        Args:
            query: Query string to analyze
            
        Returns:
            Tuple of (is_memory_request, memory_content, metadata)
        """
        # Check for memory-related keywords
        memory_keywords = [
            "remember", "recall", "memory", "memorize", 
            "don't forget", "note", "store", "keep in mind",
            "make a note", "save", "log", "record"
        ]
        
        # Memory patterns - more specific than just keywords
        memory_patterns = [
            r"remember\s+that\s+(.+)",
            r"please\s+remember\s+(.+)",
            r"don't\s+forget\s+that\s+(.+)",
            r"note\s+that\s+(.+)",
            r"keep\s+in\s+mind\s+that\s+(.+)",
            r"store\s+this\s*:\s*(.+)",
            r"memorize\s+this\s*:\s*(.+)",
            r"save\s+this\s*:\s*(.+)",
            r"add\s+to\s+memory\s*:\s*(.+)",
            r"remember\s+for\s+later\s*:\s*(.+)",
        ]
        
        # Check for pattern matches first (more precise)
        for pattern in memory_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                metadata = {
                    "source": "direct_request", 
                    "type": "memory",
                    "extraction_method": "pattern_match",
                    "pattern": pattern
                }
                return True, content, metadata
        
        # Fall back to keyword detection (less precise)
        is_memory_request = any(keyword.lower() in query.lower() for keyword in memory_keywords)
        
        if is_memory_request:
            # Extract content by removing memory trigger words
            content = query
            for keyword in memory_keywords:
                # Replace common phrases with the keyword
                content = re.sub(r'(?i)remember ' + re.escape(keyword), '', content)
                content = re.sub(r'(?i)' + re.escape(keyword), '', content, count=1)
            
            # Clean up the content
            content = content.strip()
            content = re.sub(r'^[:\s,;-]+', '', content)  # Remove leading punctuation
            content = re.sub(r'[:\s,;-]+$', '', content)  # Remove trailing punctuation
            
            metadata = {
                "source": "direct_request", 
                "type": "memory",
                "extraction_method": "keyword_match"
            }
            
            # Categorize the content
            category = self.categorize_memory(content)
            metadata["category"] = category.value
            
            return True, content, metadata
        
        # If no memory request detected
        return False, "", {}

    def detect_preference(self, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Enhanced preference detection with better question vs statement handling
        
        Args:
            query: User's query
            
        Returns:
            Tuple of (is_preference, preference_content, tags)
        """
        # Skip if query is empty
        if not query:
            return False, "", {}
            
        # Check for common preference patterns
        preference_patterns = [
            "my favorite", "i like", "i love", "i prefer", 
            "i enjoy", "i'm fond of", "i am fond of", "i think",
            "i believe", "i find", "i consider"
        ]
        
        # Skip if the query is a question about preferences rather than a statement
        question_indicators = ["what", "which", "tell me", "do i", "can you tell", "can you remind", "?"]
        for indicator in question_indicators:
            if indicator.lower() in query.lower():
                return False, "", {}
        
        # Special case for programming language preferences
        programming_patterns = ["code in", "program in", "develop in", "write in", "use"]
        for pattern in programming_patterns:
            if pattern.lower() in query.lower():
                language = self._extract_programming_language(query, pattern)
                if language:
                    preference_content = f"I like to code in {language}"
                    tags = {
                        "type": "preference",
                        "category": "programming"
                    }
                    return True, preference_content, tags
        
        is_preference = False
        preference_content = ""
        tags = {"type": "preference"}
        
        # Check if query contains any preference patterns
        for pattern in preference_patterns:
            if pattern.lower() in query.lower():
                is_preference = True
                
                # Extract the preference type and value
                parts = query.lower().split(pattern.lower(), 1)
                if len(parts) > 1:
                    # Format the preference content without adding "My" in front
                    preference_content = f"I {pattern} {parts[1].strip()}"
                    
                    # Try to identify the preference type
                    if "color" in parts[1].lower() or self._is_color(parts[1].strip()):
                        tags["category"] = "color"
                    elif any(word in parts[1].lower() for word in ["food", "dish", "meal", "cuisine"]) or self._is_food_item(parts[1].strip()):
                        tags["category"] = "food"
                    elif any(word in parts[1].lower() for word in ["movie", "film", "show", "series"]):
                        tags["category"] = "entertainment"
                    elif any(word in parts[1].lower() for word in ["music", "song", "band", "artist"]):
                        tags["category"] = "music"
                    elif any(word in parts[1].lower() for word in ["book", "author", "novel"]):
                        tags["category"] = "book"
                    elif any(word in parts[1].lower() for word in ["hobby", "activity", "pastime"]):
                        tags["category"] = "hobby"
                    elif any(word in parts[1].lower() for word in ["beach", "mountain", "travel", "vacation", "holiday", "destination", "city", "country"]):
                        tags["category"] = "travel"
                    elif any(word in parts[1].lower() for word in ["programming", "code", "coding", "language", "python", "javascript", "java", "go", "rust", "c++"]):
                        tags["category"] = "programming"
                    elif any(word in parts[1].lower() for word in ["animal", "pet", "cat", "dog", "bird"]):
                        tags["category"] = "animal"
                    else:
                        tags["category"] = "general"
                
                break
        
        return is_preference, preference_content, tags
    
    def _is_color(self, text: str) -> bool:
        """Check if the given text is a color"""
        colors = [
            "red", "blue", "green", "yellow", "orange", "purple", 
            "pink", "black", "white", "brown", "gray", "grey", 
            "teal", "cyan", "magenta", "violet", "indigo", "gold", 
            "silver", "bronze", "turquoise", "lavender", "crimson"
        ]
        
        for color in colors:
            if color in text.lower():
                return True
        
        return False
    
    def _is_food_item(self, text: str) -> bool:
        """Check if the given text is a food item"""
        food_items = [
            "pizza", "burger", "sandwich", "salad", "soup", "pasta", "rice", "curry", "sushi", "tacos",
            "apple", "banana", "orange", "grape", "watermelon", "mango", "strawberry", "blueberry", "raspberry",
            "chicken", "beef", "pork", "fish", "shrimp", "lobster", "crab", "egg", "bacon", "sausage",
            "cake", "ice cream", "cookie", "brownie", "muffin", "croissant", "donut", "bagel", "toast",
        ]
        
        for item in food_items:
            if item in text.lower():
                return True
        
        return False
    
    def _extract_programming_language(self, text: str, pattern: str) -> Optional[str]:
        """Extract a programming language from a phrase"""
        languages = [
            "python", "java", "javascript", "c++", "c#", "swift", "ruby", "php", "go", "rust", "kotlin", "scala",
            "typescript", "perl", "haskell", "matlab", "r", "sql", "assembly", "vb.net", "delphi", "pascal",
            "fortran", "cobol", "lisp", "scheme", "prolog", "erlang", "elixir", "clojure", "groovy", "grails",
            "julia", "crystal", "nim", "d", "vala", "f#", "visual basic", "powershell", "batch", "shell",
        ]
        
        # Split the text by the pattern
        parts = text.lower().split(pattern.lower(), 1)
        if len(parts) > 1:
            # Get the text after the pattern
            after_pattern = parts[1].strip()
            # Check if any language is mentioned
            for language in languages:
                if language in after_pattern.split():
                    return language
        
        return None

    def extract_entities(self, text: str) -> Tuple[List[Entity], Dict[str, Any]]:
        """
        Extract entities from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (entities, metadata)
        """
        if not self.llm:
            logger.warning("No LLM provider available, using basic entity extraction")
            return self._basic_extract_entities(text), {"method": "basic"}
        
        try:
            return self._extract_entities_with_llm(text)
        except Exception as e:
            logger.error(f"Error extracting entities with LLM: {str(e)}")
            return self._basic_extract_entities(text), {"method": "basic", "error": str(e)}
    
    def _basic_extract_entities(self, text: str) -> List[Entity]:
        """Basic entity extraction when LLM is not available"""
        entities = []
        
        # Look for dates (simple regex)
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',         # YYYY-MM-DD
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(st|nd|rd|th)?,?\s+\d{4}\b',  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                date_str = match.group(0)
                entities.append(Entity(text=date_str, type="DATE", start=match.start(), end=match.end()))
        
        # Look for people (simple approach - capitalized names)
        people_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'  # First Last name pattern
        for match in re.finditer(people_pattern, text):
            name = match.group(0)
            entities.append(Entity(text=name, type="PERSON", start=match.start(), end=match.end()))
            
        return entities

    def _extract_entities_with_llm(self, text: str) -> Tuple[List[Entity], Dict[str, Any]]:
        """
        Extract entities using LLM
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (entities, metadata)
        """
        # Get LLM provider
        llm = self.llm
        if not llm:
            logger.warning("No LLM provider configured, skipping entity extraction")
            return [], {"method": "none", "error": "No LLM provider"}
        
        # Prepare prompt
        prompt = self._get_entity_extraction_prompt(text)
        
        # Call LLM
        response = llm.get_completion(prompt)
        
        if not response:
            logger.warning("Failed to get response from LLM")
            return [], {"method": "llm", "error": "No response from LLM"}
        
        # Parse the response
        try:
            entities, relationships = self._parse_entity_extraction_response(response)
            return entities, {"method": "llm", "entity_count": len(entities), "relationship_count": len(relationships) if relationships else 0}
        except Exception as e:
            logger.error(f"Error parsing entity extraction response: {str(e)}")
            return [], {"method": "llm", "error": f"Failed to parse response: {str(e)}"}

    def _get_entity_extraction_prompt(self, text: str) -> str:
        """
        Generate a prompt for entity extraction
        
        Args:
            text: Input text
            
        Returns:
            Prompt for entity extraction
        """
        return f"""
You are an entity extraction system that identifies entities and relationships in text.
Analyze the following text and extract:

1. Entities with their types (PERSON, PLACE, ORGANIZATION, THING, CONCEPT, EVENT, DATETIME, OTHER)
2. Relationships between entities with their types (HAS, IS, KNOWS, LIKES, DISLIKES, WANTS, OWNS, LOCATED_AT, RELATED_TO, PART_OF, BEFORE, AFTER, DURING, CAUSES, OTHER)

Format your response as JSON with the following structure:
{{
  "entities": [
    {{
      "name": "entity name",
      "type": "PERSON|PLACE|ORGANIZATION|THING|CONCEPT|EVENT|DATETIME|OTHER",
      "properties": {{
        "property1": "value1",
        "property2": "value2"
      }}
    }}
  ],
  "relationships": [
    {{
      "source": "source entity name",
      "target": "target entity name",
      "type": "HAS|IS|KNOWS|LIKES|DISLIKES|WANTS|OWNS|LOCATED_AT|RELATED_TO|PART_OF|BEFORE|AFTER|DURING|CAUSES|OTHER",
      "bidirectional": true|false,
      "properties": {{
        "property1": "value1",
        "property2": "value2"
      }}
    }}
  ]
}}

Only include entities and relationships that are explicitly mentioned or strongly implied. Do not make assumptions beyond what is clearly stated or implied.

Text to analyze:
{text}
"""

    def _parse_entity_extraction_response(self, response: str) -> Optional[Tuple[List[Entity], List[Relationship]]]:
        """
        Parse the response from the LLM for entity extraction
        
        Args:
            response: LLM response
            
        Returns:
            Tuple of (entities, relationships) if successful, None otherwise
        """
        try:
            # Extract JSON from the response
            json_content = self._extract_json_from_text(response)
            
            if not json_content:
                logger.warning("No JSON content found in LLM response")
                return None
            
            # Parse JSON
            data = json.loads(json_content)
            
            # Extract entities
            entities = []
            entity_map = {}  # Map of entity name to Entity object
            
            for entity_data in data.get("entities", []):
                try:
                    name = entity_data.get("name")
                    if not name:
                        continue
                    
                    # Parse entity type
                    type_str = entity_data.get("type", "OTHER").upper()
                    try:
                        entity_type = EntityType[type_str]
                    except (KeyError, ValueError):
                        entity_type = EntityType.OTHER
                    
                    # Create entity
                    entity = Entity(
                        id=None,  # Will be assigned when added to the graph
                        name=name,
                        type=entity_type,
                        properties=entity_data.get("properties", {}),
                        created_at=None,  # Will be assigned when added to the graph
                        updated_at=None   # Will be assigned when added to the graph
                    )
                    
                    entities.append(entity)
                    entity_map[name.lower()] = entity
                    
                except Exception as e:
                    logger.error(f"Error parsing entity: {str(e)}")
                    continue
            
            # Extract relationships
            relationships = []
            
            for rel_data in data.get("relationships", []):
                try:
                    source_name = rel_data.get("source")
                    target_name = rel_data.get("target")
                    
                    if not source_name or not target_name:
                        continue
                    
                    # Ensure the source and target entities exist
                    source_entity = entity_map.get(source_name.lower())
                    target_entity = entity_map.get(target_name.lower())
                    
                    if not source_entity or not target_entity:
                        # Create missing entities as OTHER type
                        if not source_entity:
                            source_entity = Entity(
                                id=None,
                                name=source_name,
                                type=EntityType.OTHER,
                                properties={},
                                created_at=None,
                                updated_at=None
                            )
                            entities.append(source_entity)
                            entity_map[source_name.lower()] = source_entity
                        
                        if not target_entity:
                            target_entity = Entity(
                                id=None,
                                name=target_name,
                                type=EntityType.OTHER,
                                properties={},
                                created_at=None,
                                updated_at=None
                            )
                            entities.append(target_entity)
                            entity_map[target_name.lower()] = target_entity
                    
                    # Parse relationship type
                    type_str = rel_data.get("type", "OTHER").upper()
                    try:
                        rel_type = RelationshipType[type_str]
                    except (KeyError, ValueError):
                        rel_type = RelationshipType.OTHER
                    
                    # Create relationship
                    relationship = Relationship(
                        id=None,  # Will be assigned when added to the graph
                        source_id=None,  # Will be filled in when entities are added to the graph
                        target_id=None,  # Will be filled in when entities are added to the graph
                        type=rel_type,
                        properties=rel_data.get("properties", {}),
                        bidirectional=rel_data.get("bidirectional", False),
                        created_at=None,  # Will be assigned when added to the graph
                        updated_at=None   # Will be assigned when added to the graph
                    )
                    
                    # Store source and target entity references for later
                    relationship.properties["_source_name"] = source_name.lower()
                    relationship.properties["_target_name"] = target_name.lower()
                    
                    relationships.append(relationship)
                    
                except Exception as e:
                    logger.error(f"Error parsing relationship: {str(e)}")
                    continue
            
            return entities, relationships
        except Exception as e:
            logger.error(f"Error parsing entity extraction response: {str(e)}")
            return None

    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """
        Extract JSON content from text
        
        Args:
            text: Input text
            
        Returns:
            JSON string if found, None otherwise
        """
        try:
            # Look for JSON between braces
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return match.group(0)
            return None
        except Exception as e:
            logger.error(f"Error extracting JSON from text: {str(e)}")
            return None
