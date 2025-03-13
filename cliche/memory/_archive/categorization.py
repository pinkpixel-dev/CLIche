"""
Memory categorization module for CLIche

Handles the categorization of memories by topic and type.

Made with ❤️ by Pink Pixel
"""
import re
import logging
from typing import Dict, List, Any, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Types of memories"""
    PREFERENCE = "preference"
    FACT = "fact"
    PLAN = "plan"
    RELATIONSHIP = "relationship"
    PERSONAL_INFO = "personal_info"
    GOAL = "goal"
    OPINION = "opinion"
    OTHER = "other"

class MemoryTopic(Enum):
    """Topics for memory categorization"""
    FOOD = "food"
    COLOR = "color"
    MUSIC = "music"
    MOVIE = "movie"
    BOOK = "book"
    TRAVEL = "travel"
    PROGRAMMING = "programming"
    ANIMAL = "animal"
    SPORT = "sport"
    FAMILY = "family"
    JOB = "job"
    HOBBY = "hobby"
    GENERAL = "general"

class MemoryCategorizer:
    """Categorizes memories by topic and type"""
    
    def __init__(self, config=None):
        """
        Initialize the memory categorizer
        
        Args:
            config: Optional configuration for the categorizer
        """
        # config is ignored in this implementation, but we accept it for consistency
        # with other memory components
        
        # Define topic keywords for categorization
        self.topic_keywords = {
            MemoryTopic.FOOD.value: [
                "food", "meal", "dish", "cuisine", "recipe", "eat", "eating", "cook", "cooking", 
                "like to eat", "favorite food", "favourite food", "prefer to eat", "enjoy eating", 
                "taste", "flavor", "flavour", "delicious", "yummy", "tasty", "snack", "breakfast", 
                "lunch", "dinner", "appetizer", "dessert", "pickles", "pizza", "burger", "pasta"
            ],
            MemoryTopic.COLOR.value: [
                "color", "colour", "red", "blue", "green", "yellow", "orange", "purple", 
                "pink", "black", "white", "brown", "gray", "grey", "teal", "cyan", "magenta"
            ],
            MemoryTopic.MUSIC.value: [
                "music", "song", "artist", "band", "album", "genre", "playlist", "listen", 
                "listening", "singer", "concert", "symphony", "orchestra", "instrument", "piano", 
                "guitar", "drums", "violin", "bass", "saxophone", "trumpet", "flute"
            ],
            MemoryTopic.MOVIE.value: [
                "movie", "film", "watch", "watching", "cinema", "theater", "actor", "actress", 
                "director", "scene", "plot", "character", "series", "show", "tv", "television", 
                "documentary", "comedy", "drama", "action", "thriller", "horror", "sci-fi", 
                "science fiction", "fantasy", "animation", "cartoon"
            ],
            MemoryTopic.BOOK.value: [
                "book", "read", "reading", "author", "novel", "story", "literature", "chapter", 
                "page", "character", "plot", "fiction", "non-fiction", "biography", "autobiography", 
                "memoir", "poetry", "poem", "magazine", "article", "journal", "publication"
            ],
            MemoryTopic.TRAVEL.value: [
                "travel", "trip", "vacation", "holiday", "visit", "destination", "tourism", 
                "tourist", "beach", "mountain", "city", "country", "flight", "hotel", "resort", 
                "cruise", "journey", "adventure", "exploration", "sightseeing", "tour", "guide", 
                "passport", "visa", "luggage", "backpack", "map", "compass", "gps"
            ],
            MemoryTopic.PROGRAMMING.value: [
                "programming", "code", "coding", "developer", "software", "app", "application", 
                "website", "web", "language", "python", "javascript", "java", "go", "rust", 
                "c++", "typescript", "html", "css", "php", "ruby", "swift", "kotlin", "scala", 
                "perl", "haskell", "lisp", "clojure", "erlang", "elixir", "dart", "flutter", 
                "react", "angular", "vue", "node", "django", "flask", "spring", "rails", "laravel"
            ],
            MemoryTopic.ANIMAL.value: [
                "animal", "pet", "zoo", "wildlife", "cat", "dog", "bird", "fish", "reptile", 
                "mammal", "amphibian", "insect", "arachnid", "crustacean", "mollusk", "feline", 
                "canine", "avian", "aquatic", "terrestrial", "predator", "prey", "herbivore", 
                "carnivore", "omnivore", "endangered", "extinct", "species", "genus", "family", 
                "order", "class", "phylum", "kingdom"
            ],
            MemoryTopic.SPORT.value: [
                "sport", "exercise", "fitness", "workout", "gym", "run", "running", "swim", 
                "swimming", "bike", "biking", "cycling", "hike", "hiking", "climb", "climbing", 
                "football", "soccer", "basketball", "baseball", "tennis", "golf", "hockey", 
                "rugby", "cricket", "volleyball", "badminton", "table tennis", "ping pong", 
                "boxing", "martial arts", "wrestling", "gymnastics", "athletics", "track", "field"
            ],
            MemoryTopic.FAMILY.value: [
                "family", "husband", "wife", "spouse", "child", "children", "kid", "kids", 
                "parent", "parents", "mother", "father", "brother", "sister", "sibling", 
                "grandparent", "grandmother", "grandfather", "grandchild", "grandson", 
                "granddaughter", "uncle", "aunt", "nephew", "niece", "cousin", "relative", 
                "in-law", "mother-in-law", "father-in-law", "brother-in-law", "sister-in-law"
            ],
            MemoryTopic.JOB.value: [
                "job", "work", "career", "profession", "company", "office", "workplace", 
                "business", "industry", "sector", "market", "economy", "finance", "accounting", 
                "marketing", "sales", "management", "administration", "executive", "director", 
                "manager", "supervisor", "employee", "employer", "colleague", "coworker", 
                "client", "customer", "project", "task", "deadline", "meeting", "conference", 
                "presentation", "report", "resume", "cv", "interview", "application", "position", 
                "role", "responsibility", "duty", "assignment", "promotion", "demotion", "raise", 
                "bonus", "salary", "wage", "income", "benefit", "pension", "retirement"
            ],
            MemoryTopic.HOBBY.value: [
                "hobby", "hobbies", "interest", "interests", "pastime", "activity", "activities", 
                "collect", "collecting", "collection", "craft", "crafting", "art", "drawing", 
                "painting", "sculpting", "photography", "gardening", "cooking", "baking", 
                "knitting", "sewing", "woodworking", "metalworking", "fishing", "hunting", 
                "camping", "hiking", "biking", "cycling", "running", "swimming", "gaming", 
                "video games", "board games", "card games", "puzzle", "crossword", "sudoku", 
                "chess", "checkers", "backgammon", "poker", "bridge", "reading", "writing", 
                "blogging", "vlogging", "streaming", "podcasting", "dancing", "singing", 
                "playing music", "instrument", "theater", "acting", "drama", "comedy", "improv"
            ]
        }
        
        # Define type patterns for categorization
        self.type_patterns = {
            MemoryType.PREFERENCE.value: [
                r"(prefer|like|love|enjoy|favorite|favourite)",
                r"(hate|dislike|don't like|do not like|can't stand|cannot stand)",
            ],
            MemoryType.FACT.value: [
                r"(is|are|was|were|has|have|had)",
                r"(know|knew|known)",
            ],
            MemoryType.PLAN.value: [
                r"(plan|schedule|appointment|meeting|tomorrow|next week|next month|next year)",
                r"(going to|will|shall|intend to|aim to|hope to)",
            ],
            MemoryType.RELATIONSHIP.value: [
                r"(friend|family|parent|child|spouse|partner|colleague)",
                r"(mother|father|brother|sister|son|daughter|husband|wife)",
            ],
            MemoryType.PERSONAL_INFO.value: [
                r"(name is|live in|from|age|birthday|born)",
                r"(address|phone|email|contact)",
            ],
            MemoryType.GOAL.value: [
                r"(goal|aim|objective|target|aspire|want to|would like to)",
                r"(dream|ambition|aspiration|desire)",
            ],
            MemoryType.OPINION.value: [
                r"(think|believe|opinion|feel|view)",
                r"(consider|judge|evaluate|assess)",
            ],
        }
        
        # Define topic relationships for contextual retrieval
        self.topic_relationships = {
            MemoryTopic.TRAVEL.value: [
                MemoryTopic.FOOD.value,  # Food preferences while traveling
                MemoryTopic.HOBBY.value,  # Activities during travel
            ],
            MemoryTopic.FOOD.value: [
                MemoryTopic.RESTAURANT.value if hasattr(MemoryTopic, "RESTAURANT") else "restaurant",
                MemoryTopic.TRAVEL.value,  # Food from different places
            ],
            MemoryTopic.PROGRAMMING.value: [
                MemoryTopic.JOB.value,  # Programming for work
                MemoryTopic.HOBBY.value,  # Programming as a hobby
            ],
            MemoryTopic.ANIMAL.value: [
                MemoryTopic.HOBBY.value,  # Pets as a hobby
                MemoryTopic.FAMILY.value,  # Pets as family members
            ],
            MemoryTopic.SPORT.value: [
                MemoryTopic.HOBBY.value,  # Sports as a hobby
                MemoryTopic.HEALTH.value if hasattr(MemoryTopic, "HEALTH") else "health",
            ],
        }
        
        # Define contextual queries to topics mapping
        self.contextual_queries = {
            "vacation": [MemoryTopic.TRAVEL.value, MemoryTopic.FOOD.value],
            "weekend": [MemoryTopic.HOBBY.value, MemoryTopic.TRAVEL.value, MemoryTopic.FOOD.value, MemoryTopic.SPORT.value],
            "project": [MemoryTopic.PROGRAMMING.value, MemoryTopic.HOBBY.value, MemoryTopic.JOB.value],
            "relax": [MemoryTopic.HOBBY.value, MemoryTopic.MUSIC.value, MemoryTopic.MOVIE.value, MemoryTopic.BOOK.value, MemoryTopic.TRAVEL.value],
            "gift": [MemoryTopic.HOBBY.value, MemoryTopic.BOOK.value, MemoryTopic.MUSIC.value, MemoryTopic.MOVIE.value],
            "fun": [MemoryTopic.HOBBY.value, MemoryTopic.TRAVEL.value, MemoryTopic.SPORT.value],
            "learn": [MemoryTopic.PROGRAMMING.value, MemoryTopic.BOOK.value, MemoryTopic.HOBBY.value],
            "create": [MemoryTopic.PROGRAMMING.value, MemoryTopic.HOBBY.value, MemoryTopic.FOOD.value],
            "visit": [MemoryTopic.TRAVEL.value, MemoryTopic.FAMILY.value],
            "recommend": [MemoryTopic.FOOD.value, MemoryTopic.BOOK.value, MemoryTopic.MOVIE.value, MemoryTopic.MUSIC.value, MemoryTopic.TRAVEL.value],
        }
    
    def categorize(self, content: str) -> str:
        """
        Categorize a memory by topic and return the primary topic
        
        Args:
            content: Memory content to categorize
            
        Returns:
            Primary topic as a string
        """
        result = self.categorize_memory(content)
        return result.get("topic", MemoryTopic.GENERAL.value)
    
    def categorize_memory(self, content: str) -> Dict[str, Any]:
        """
        Categorize a memory by topic and type
        
        Args:
            content: Memory content to categorize
            
        Returns:
            Dictionary with topic and type information
        """
        content_lower = content.lower()
        
        # Determine memory type
        memory_type = self._determine_memory_type(content_lower)
        
        # Determine memory topic
        memory_topic = self._determine_memory_topic(content_lower)
        
        # Determine subtopics if applicable
        subtopics = self._determine_subtopics(content_lower, memory_topic)
        
        return {
            "type": memory_type,
            "topic": memory_topic,
            "subtopics": subtopics
        }
    
    def _determine_memory_type(self, content: str) -> str:
        """
        Determine the type of a memory
        
        Args:
            content: Memory content to analyze
            
        Returns:
            Memory type
        """
        for memory_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return memory_type
        
        # Default to fact if no specific type is matched
        return MemoryType.FACT.value
    
    def _determine_memory_topic(self, content: str) -> str:
        """
        Determine the topic of a memory
        
        Args:
            content: Memory content to analyze
            
        Returns:
            Memory topic
        """
        # Check each topic's keywords
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    return topic
        
        # Default to general if no specific topic is matched
        return MemoryTopic.GENERAL.value
    
    def _determine_subtopics(self, content: str, primary_topic: str) -> List[str]:
        """
        Determine subtopics for a memory
        
        Args:
            content: Memory content to analyze
            primary_topic: Primary topic of the memory
            
        Returns:
            List of subtopics
        """
        subtopics = set()
        
        # Check for related topics
        if primary_topic in self.topic_relationships:
            for related_topic in self.topic_relationships[primary_topic]:
                # Only add as a subtopic if there's evidence in the content
                if related_topic in self.topic_keywords:
                    for keyword in self.topic_keywords[related_topic]:
                        if keyword in content:
                            subtopics.add(related_topic)
                            break
        
        # Check for contextual queries
        for context, topics in self.contextual_queries.items():
            if context in content and primary_topic in topics:
                for topic in topics:
                    if topic != primary_topic:
                        subtopics.add(topic)
        
        return list(subtopics)
    
    def get_related_topics(self, topic: str) -> List[str]:
        """
        Get topics related to a given topic
        
        Args:
            topic: Topic to get related topics for
            
        Returns:
            List of related topics
        """
        related_topics = set()
        
        # Add directly related topics
        if topic in self.topic_relationships:
            related_topics.update(self.topic_relationships[topic])
        
        # Add topics from contextual queries
        for context, topics in self.contextual_queries.items():
            if topic in topics:
                related_topics.update(topics)
        
        # Remove the original topic
        if topic in related_topics:
            related_topics.remove(topic)
        
        return list(related_topics)
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query to determine relevant topics and types
        
        Args:
            query: Query to analyze
            
        Returns:
            Dictionary with analysis results
        """
        query_lower = query.lower()
        
        # Check for preference questions
        preference_questions = {
            MemoryTopic.FOOD.value: ["what food", "what foods", "which food", "which foods", "favorite food", "favourite food", "like to eat", "prefer to eat", "enjoy eating", "what do i like to eat", "what kind of food", "what kinds of food"],
            MemoryTopic.COLOR.value: ["what color", "which color", "favorite color", "favourite color"],
            MemoryTopic.MUSIC.value: ["what music", "which music", "favorite music", "favourite music"],
            MemoryTopic.MOVIE.value: ["what movie", "which movie", "favorite movie", "favourite movie"],
            MemoryTopic.BOOK.value: ["what book", "which book", "favorite book", "favourite book"],
            MemoryTopic.TRAVEL.value: ["where to go", "where to visit", "where to travel", "vacation spot", "holiday destination"],
            MemoryTopic.PROGRAMMING.value: ["what language", "which language", "coding language", "programming language"],
        }
        
        # Check if query is asking about preferences
        is_preference_question = False
        preference_topics = []
        
        for topic, questions in preference_questions.items():
            if any(question in query_lower for question in questions):
                is_preference_question = True
                preference_topics.append(topic)
        
        # Determine topics in the query
        query_topics = []
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                query_topics.append(topic)
        
        # Check for contextual relationships
        contextual_topics = []
        for context, topics in self.contextual_queries.items():
            if context in query_lower:
                contextual_topics.extend(topics)
        
        # Combine all topics and remove duplicates
        all_topics = list(set(preference_topics + query_topics + contextual_topics))
        
        return {
            "is_preference_question": is_preference_question,
            "preference_topics": preference_topics,
            "query_topics": query_topics,
            "contextual_topics": contextual_topics,
            "all_topics": all_topics
        }
