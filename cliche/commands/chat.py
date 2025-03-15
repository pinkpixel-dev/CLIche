"""
Chat command for CLIche

Provides a command for chatting with the LLM in a more conversational way.

Made with ❤️ by Pink Pixel
"""
import click
import logging
import asyncio
import re
import sys
import io
from collections import Counter

from ..core import get_cliche_instance

logger = logging.getLogger(__name__)

# Base categories with some common patterns
CATEGORY_PATTERNS = {
    "food": [
        r"cook", r"eat", r"food", r"meal", r"dinner", r"breakfast", r"lunch",
        r"recipe", r"restaurant", r"hungry", r"cuisine", r"dish", r"pizza", r"burger",
        r"kitchen", r"bake", r"chef", r"grocery", r"ingredient", r"taste", r"flavor",
        r"diet", r"nutrition"
    ],
    "programming": [
        r"program", r"code", r"develop", r"build", r"software", r"app", r"application",
        r"javascript", r"python", r"java", r"ruby", r"go", r"rust", r"typescript",
        r"html", r"css", r"database", r"algorithm", r"function", r"class", r"object",
        r"library", r"framework", r"api", r"backend", r"frontend", r"fullstack",
        r"compiler", r"interpreter", r"debug", r"syntax", r"coding", r"script", r"git"
    ],
    "travel": [
        r"travel", r"trip", r"vacation", r"flight", r"hotel", r"book", r"destination",
        r"visit", r"country", r"city", r"airport", r"tour", r"sightseeing", r"abroad",
        r"foreign", r"overseas", r"journey", r"adventure", r"explore", r"tourism",
        r"suitcase", r"backpack", r"passport", r"visa", r"resort", r"beach", r"mountain"
    ],
    "entertainment": [
        r"movie", r"film", r"show", r"tv", r"series", r"watch", r"stream", r"netflix",
        r"hulu", r"amazon", r"disney", r"actor", r"actress", r"director", r"scene",
        r"episode", r"season", r"theater", r"cinema", r"music", r"song", r"artist",
        r"band", r"concert", r"album", r"playlist", r"streaming", r"game", r"gaming",
        r"play", r"video game", r"playstation", r"xbox", r"nintendo", r"console"
    ],
    "health": [
        r"health", r"fitness", r"workout", r"exercise", r"gym", r"diet", r"nutrition",
        r"weight", r"muscle", r"strength", r"cardio", r"run", r"jog", r"walk", r"yoga",
        r"meditation", r"mindfulness", r"doctor", r"medical", r"medicine", r"symptom",
        r"illness", r"disease", r"treatment", r"therapy", r"mental", r"physical", r"sleep"
    ],
    "shopping": [
        r"shop", r"buy", r"purchase", r"store", r"mall", r"online", r"amazon", r"ebay",
        r"price", r"cost", r"discount", r"deal", r"sale", r"product", r"item", r"brand",
        r"warranty", r"return", r"shipping", r"delivery", r"cart", r"checkout", r"payment"
    ],
    "career": [
        r"job", r"career", r"work", r"profession", r"employment", r"boss", r"manager",
        r"colleague", r"coworker", r"interview", r"resume", r"cv", r"application",
        r"salary", r"wage", r"promotion", r"office", r"remote", r"hybrid", r"company",
        r"business", r"startup", r"corporation", r"enterprise", r"industry", r"sector"
    ],
    "education": [
        r"education", r"school", r"college", r"university", r"degree", r"course",
        r"class", r"study", r"learn", r"teach", r"student", r"professor", r"teacher",
        r"instructor", r"lecture", r"assignment", r"homework", r"exam", r"test",
        r"grade", r"academic", r"research", r"thesis", r"dissertation", r"knowledge"
    ],
    "technology": [
        r"technology", r"tech", r"computer", r"laptop", r"desktop", r"phone", r"mobile",
        r"tablet", r"device", r"hardware", r"software", r"gadget", r"robot", r"ai",
        r"artificial intelligence", r"machine learning", r"data", r"cloud", r"server",
        r"network", r"internet", r"web", r"wireless", r"bluetooth", r"usb", r"app"
    ],
    "relationships": [
        r"relationship", r"partner", r"spouse", r"husband", r"wife", r"boyfriend",
        r"girlfriend", r"date", r"dating", r"romance", r"romantic", r"love", r"marriage",
        r"engaged", r"engagement", r"wedding", r"divorce", r"breakup", r"family",
        r"parent", r"child", r"kid", r"mother", r"father", r"mom", r"dad", r"son", 
        r"daughter", r"brother", r"sister", r"sibling", r"relative", r"friend"
    ]
}

def extract_keywords(text):
    """Extract potential keywords from text by removing common words and keeping nouns/verbs"""
    # This is a simple implementation - in a more advanced system, you might use NLP libraries
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Split into words
    words = text.split()
    
    # Remove common words/stopwords (simplified list)
    stopwords = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 'which', 
        'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than', 'such', 'both', 
        'through', 'about', 'for', 'is', 'of', 'while', 'during', 'to', 'from', 'in', 
        'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 
        'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 
        'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 
        'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'don', 'should', 
        'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 
        'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 
        'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn', 'my', 'me', 'i', 'we', 'our',
        'you', 'your'
    }
    
    keywords = [word for word in words if word not in stopwords and len(word) > 2]
    
    return keywords

def enrich_query_with_context(message: str) -> dict:
    """
    Enrich the query with contextual information to improve memory retrieval.
    
    This analyzes the query intent and adds related terms for broader memory matching.
    
    Args:
        message: The user's message
        
    Returns:
        Dictionary with query information including:
        - intent: The detected intent of the message
        - search_terms: A list of search terms to use
        - relevance_categories: Categories that might be relevant
        - keywords: Extracted keywords from the message
    """
    message_lower = message.lower()
    
    # Extract keywords from the message
    keywords = extract_keywords(message_lower)
    
    # Initialize with the original message
    result = {
        "original_message": message,
        "intent": "general",
        "search_terms": [message],
        "relevance_categories": [],
        "keywords": keywords
    }
    
    # Detect preference intent
    preference_patterns = [
        r"like", r"love", r"hate", r"prefer", r"favorite", r"recommend",
        r"suggest", r"what should i"
    ]
    
    is_preference = any(re.search(pattern, message_lower) for pattern in preference_patterns)
    if is_preference:
        result["intent"] = "preference"
    
    # Check for each category
    matched_categories = []
    for category, patterns in CATEGORY_PATTERNS.items():
        if any(re.search(pattern, message_lower) for pattern in patterns):
            matched_categories.append(category)
            result["search_terms"].extend(patterns[:5])  # Add some patterns as search terms
    
    if matched_categories:
        # If we have matched categories, add them
        result["relevance_categories"] = matched_categories
        
        # If it's a preference question related to specific categories
        if is_preference:
            for category in matched_categories:
                result["search_terms"].append(f"favorite {category}")
                result["search_terms"].append(f"like {category}")
                result["search_terms"].append(f"prefer {category}")
    
    # Add keywords as search terms if we have them
    if keywords:
        result["search_terms"].extend(keywords)
    
    return result

def get_enhanced_memories(assistant, message: str, limit: int = 5):
    """
    Get memories that are contextually relevant to the message.
    
    This goes beyond simple keyword matching to find memories that relate
    to the user's intent, even if they don't contain exact keyword matches.
    
    Args:
        assistant: The CLIche instance
        message: The user's message
        limit: Maximum number of memories to return
        
    Returns:
        List of memory dictionaries
    """
    # Get context information
    context_info = enrich_query_with_context(message)
    
    # Initial list to store all potentially relevant memories
    all_memories = []
    found_memory_ids = set()
    
    # Capture standard error to prevent FTS errors from showing up
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    # Try the original query first
    try:
        # Clean up query to avoid FTS syntax errors
        cleaned_query = re.sub(r'[\'",?!.;:]', ' ', message)
        direct_matches = assistant.memory.search(cleaned_query, limit=limit)
        
        # Add direct matches to the result list
        for memory in direct_matches:
            memory_id = memory.get('id')
            if memory_id and memory_id not in found_memory_ids:
                found_memory_ids.add(memory_id)
                all_memories.append(memory)
    except Exception as e:
        # Log the error but don't show it to the user
        logger.debug(f"Primary memory search failed: {str(e)}")
    
    # If we didn't find enough direct matches, try the enriched terms
    if len(all_memories) < limit:
        remaining_limit = limit - len(all_memories)
        
        # Try each search term in the context
        for term in context_info["search_terms"]:
            if len(all_memories) >= limit:
                break
                
            try:
                # Clean up the term
                cleaned_term = re.sub(r'[\'",?!.;:]', ' ', term)
                if not cleaned_term.strip():
                    continue
                    
                # Search for this term
                term_matches = assistant.memory.search(cleaned_term, limit=remaining_limit)
                
                # Add new matches to our result list
                for memory in term_matches:
                    memory_id = memory.get('id')
                    if memory_id and memory_id not in found_memory_ids:
                        found_memory_ids.add(memory_id)
                        all_memories.append(memory)
                        
                # Update the remaining limit
                remaining_limit = limit - len(all_memories)
            except Exception as e:
                logger.debug(f"Term search failed for '{term}': {str(e)}")
    
    # If we still don't have enough results, try to get the most recent preferences
    if len(all_memories) < limit and "preference" in context_info["intent"]:
        try:
            # Get the most recent preferences
            preference_matches = assistant.memory.search("prefer like favorite love", limit=remaining_limit)
            
            for memory in preference_matches:
                memory_id = memory.get('id')
                if memory_id and memory_id not in found_memory_ids:
                    found_memory_ids.add(memory_id)
                    all_memories.append(memory)
        except Exception as e:
            logger.debug(f"Preference search failed: {str(e)}")
    
    # Restore stderr
    captured_errors = sys.stderr.getvalue()
    sys.stderr = old_stderr
    
    # Log any captured errors for debugging
    if captured_errors:
        logger.debug(f"Suppressed errors during memory search: {captured_errors}")
    
    # Sort memories by relevance (relevance score would be ideal, but timestamp is a simple proxy)
    all_memories.sort(key=lambda m: m.get('timestamp', 0), reverse=True)
    
    # Return up to the limit
    return all_memories[:limit]

def find_related_memories(assistant, message: str, limit: int = 3):
    """
    Find memories related to the message using a combined approach.
    
    This function:
    1. Uses the enhanced contextual search
    2. Analyzes the message for intent
    3. Applies memory search strategies based on the intent
    4. Formats memories for inclusion in prompts
    
    Args:
        assistant: The CLIche instance
        message: The user's message
        limit: Maximum number of memories to retrieve
        
    Returns:
        Formatted string with memories, or empty string if none found
    """
    # Skip if memory is not available
    if not assistant.memory or not assistant.memory.enabled:
        return ""
    
    # Redirect stderr to capture any FTS errors
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    try:
        # Get context-enhanced memories
        memories = get_enhanced_memories(assistant, message, limit=limit)
        
        if not memories:
            return ""
            
        # Format memories for the prompt
        memory_context = "I found these relevant memories about the user:\n\n"
        for i, memory in enumerate(memories):
            memory_context += f"Memory {i+1}: {memory.get('content', '')}\n\n"
            
        return memory_context
    except Exception as e:
        logger.debug(f"Memory retrieval failed: {str(e)}")
        return ""  # Return empty string on failure
    finally:
        # Restore stderr and log any captured errors
        captured_errors = sys.stderr.getvalue()
        sys.stderr = old_stderr
        
        if captured_errors and "FTS search failed" in captured_errors:
            # Log these errors for debugging but don't show to the user
            logger.debug(f"Suppressed FTS errors: {captured_errors}")

@click.command()
@click.argument('message', nargs=-1, required=True)
@click.option('--no-memory', is_flag=True, help='Disable memory for this conversation')
def chat(message, no_memory):
    """Chat with CLIche in a conversational way"""
    # Join message parts into a single string
    message_str = ' '.join(message)
    
    # Get CLIche instance
    assistant = get_cliche_instance()
    
    # Determine whether to use memory
    memory_ready = assistant.memory and assistant.memory.enabled
    use_memory = memory_ready and not no_memory
    
    # Generate response
    try:
        # Show waiting message
        click.echo("💬 CLIche is chatting (and probably mocking you)...")
        click.echo()
        
        if use_memory:
            # Find related memories
            memory_context = find_related_memories(assistant, message_str)
            
            if memory_context:
                # Enhance the prompt with memories and instructions
                enhanced_message = (
                    f"{memory_context}\n"
                    f"Use the above memories to personalize your response if relevant. "
                    f"Don't directly mention that you're using memories unless directly asked. "
                    f"Respond naturally as if you've known the user for a while. "
                    f"Now please respond to this message: {message_str}"
                )
                response = asyncio.run(assistant.ask_llm(enhanced_message))
            else:
                # No relevant memories found, proceed with original message
                response = asyncio.run(assistant.ask_llm(message_str))
            
            # Store the interaction as a memory if auto_memory is enabled
            if assistant.memory.auto_memory:
                try:
                    # Store the message as a memory
                    assistant.memory.add(message_str, {
                        "type": "chat",
                        "response": response
                    })
                except Exception as e:
                    # Silently handle any errors with memory storage
                    logger.error(f"Failed to add memory: {str(e)}")
        else:
            # If memory isn't ready, just use the LLM without memory
            response = asyncio.run(assistant.ask_llm(message_str))
        
        # Display response
        click.echo(f"💬 {response}")
    except Exception as e:
        logger.error(f"Failed to generate response: {str(e)}")
        click.echo(f"Error: {str(e)}")
