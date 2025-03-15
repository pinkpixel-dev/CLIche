"""
Ask command for CLIche

Provides a command for asking questions to the LLM.

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
from .chat import find_related_memories, CATEGORY_PATTERNS, extract_keywords

logger = logging.getLogger(__name__)

@click.command()
@click.argument('query', nargs=-1, required=True)
@click.option('--no-memory', is_flag=True, help='Disable memory for this query')
def ask(query, no_memory):
    """Ask a question to the LLM"""
    # Join query parts into a single string
    query_str = ' '.join(query)
    
    # Get CLIche instance
    assistant = get_cliche_instance()
    
    # Determine whether to use memory
    memory_ready = assistant.memory and assistant.memory.enabled
    use_memory = memory_ready and not no_memory
    
    # Generate response
    try:
        click.echo("🤔 CLIche is pondering (and judging)...")
        click.echo()
        
        if use_memory:
            # Capture standard error to prevent FTS errors from showing up
            old_stderr = sys.stderr
            sys.stderr = io.StringIO()
            
            try:
                # Find related memories using the enhanced memory retrieval system
                memory_context = find_related_memories(assistant, query_str)
            finally:
                # Restore stderr and log any captured errors
                captured_errors = sys.stderr.getvalue()
                sys.stderr = old_stderr
                
                if captured_errors:
                    logger.debug(f"Suppressed errors during memory search: {captured_errors}")
            
            if memory_context:
                # Enhance the prompt with memories and instructions
                enhanced_query = (
                    f"{memory_context}\n"
                    f"Use the above memories to personalize your response if relevant. "
                    f"Don't directly mention that you're using memories unless directly asked. "
                    f"Respond naturally as if you've known the user for a while. "
                    f"Now please respond to this question: {query_str}"
                )
                response = asyncio.run(assistant.ask_llm(enhanced_query))
            else:
                # No relevant memories found, proceed with original query
                response = asyncio.run(assistant.ask_llm(query_str))
            
            # Store the interaction as a memory if auto_memory is enabled
            if assistant.memory.auto_memory:
                try:
                    # Store the query as a memory
                    assistant.memory.add(query_str, {
                        "type": "question",
                        "response": response
                    })
                except Exception as e:
                    # Silently handle any errors with memory storage
                    logger.error(f"Failed to add memory: {str(e)}")
        else:
            # If memory isn't ready, just use the LLM without memory
            response = asyncio.run(assistant.ask_llm(query_str))
        
        click.echo(f"💡 {response}")
    except Exception as e:
        logger.error(f"Failed to generate response: {str(e)}")
        click.echo(f"Error: {str(e)}")