"""
Chat command for CLIche

Provides a command for chatting with the LLM in a more conversational way.

Made with ❤️ by Pink Pixel
"""
import click
import logging
import asyncio

from ..core import get_cliche_instance

logger = logging.getLogger(__name__)

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
    use_memory = assistant.memory.enabled and not no_memory
    
    # Check for explicit memory request
    is_memory_request, memory_content, memory_tags = assistant.memory.detect_memory_request(message_str)
    
    # Check for preference sharing
    is_preference, preference_content, preference_tags = assistant.memory.detect_preference(message_str)
    
    # Generate response
    try:
        # Show waiting message
        click.echo("💬 CLIche is chatting (and probably mocking you)...")
        click.echo()
        
        if use_memory:
            # Enhance message with memories
            enhanced_message = assistant.memory.enhance_with_memories(message_str)
            
            # Check if enhancement added any memories
            if enhanced_message != message_str:
                # Log the enhanced message
                logger.debug(f"Enhanced message: {enhanced_message}")
                
                # Generate response with enhanced message
                response = asyncio.run(assistant.ask_llm(enhanced_message))
                
                # Extract personal info from response
                assistant.memory.extract_personal_info(message_str, response)
            else:
                # Generate response with original message
                response = asyncio.run(assistant.ask_llm(message_str))
                
                # Extract personal info from response
                assistant.memory.extract_personal_info(message_str, response)
                
            # Auto-memory feature
            if assistant.memory.auto_memory:
                try:
                    # If this is an explicit memory request, store it with the appropriate tags
                    if is_memory_request and memory_content:
                        memory_id = assistant.memory.add(memory_content, memory_tags)
                        # No need to notify the user as the LLM response should acknowledge it
                    # If this is a preference, it's already handled by detect_preference
                    elif not is_preference:
                        # Create a memory of this interaction
                        assistant.memory.auto_add(message_str, response)
                except Exception as e:
                    logger.error(f"Failed to create memory: {str(e)}")
        else:
            response = asyncio.run(assistant.ask_llm(message_str))
        
        # If this was a memory request, acknowledge it
        if is_memory_request and memory_content:
            click.echo(f"💬 {response}\n\nI've remembered that {memory_content}")
        # If this was a preference, acknowledge it
        elif is_preference and preference_content:
            click.echo(f"💬 {response}\n\nI've noted your preference: {preference_content}")
        else:
            click.echo(f"💬 {response}")
    except Exception as e:
        logger.error(f"Failed to generate response: {str(e)}")
        click.echo(f"Error: {str(e)}")
