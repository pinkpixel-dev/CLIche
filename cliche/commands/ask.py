"""
Ask command for CLIche

Provides a command for asking questions to the LLM.

Made with ❤️ by Pink Pixel
"""
import click
import logging
import asyncio

from ..core import get_cliche_instance

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
    use_memory = assistant.memory.enabled and not no_memory
    
    # Generate response
    try:
        click.echo("🤔 CLIche is pondering (and judging)...")
        click.echo()
        
        if use_memory:
            # Enhance query with memories
            enhanced_query = assistant.memory.enhance_with_memories(query_str)
            response = asyncio.run(assistant.ask_llm(enhanced_query))
            
            # Store the interaction as a memory if auto_memory is enabled
            if assistant.memory.auto_memory:
                try:
                    # Create a memory of this interaction
                    memory_content = f"User asked: {query_str}\nYou responded: {response}"
                    memory_id = assistant.memory.add(memory_content, {"type": "conversation"})
                    # We don't need to notify the user about this
                except Exception as e:
                    # Silently handle any errors with memory storage
                    pass
        else:
            response = asyncio.run(assistant.ask_llm(query_str))
        
        click.echo(f"💡 {response}")
    except Exception as e:
        logger.error(f"Failed to generate response: {str(e)}")
        click.echo(f"Error: {str(e)}")