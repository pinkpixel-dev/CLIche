"""
Memory commands for CLIche

Provides commands for storing and retrieving memories.

Made with ❤️ by Pink Pixel
"""
import click
import asyncio
from typing import Optional

from ..core import get_cliche_instance

@click.group()
def memory():
    """Memory management commands"""
    pass

@memory.command()
@click.argument('content', nargs=-1)
def store(content):
    """Store a new memory"""
    assistant = get_cliche_instance()
    
    if not assistant.memory.enabled:
        click.echo("Memory system is disabled. Use 'memory toggle on' to enable it.")
        return
    
    content_str = " ".join(content)
    if not content_str:
        click.echo("Please provide memory content to store.")
        return
    
    memory_id = assistant.memory.add(content_str)
    
    if memory_id:
        click.echo(f"Memory stored successfully (ID: {memory_id}).")
    else:
        click.echo("Failed to store memory.")

@memory.command()
@click.argument('query', nargs=-1)
@click.option('--limit', '-l', default=5, help='Maximum number of results to return')
def recall(query, limit):
    """Recall memories matching a query"""
    assistant = get_cliche_instance()
    
    if not assistant.memory.enabled:
        click.echo("Memory system is disabled. Use 'memory toggle on' to enable it.")
        return
    
    query_str = " ".join(query)
    if not query_str:
        click.echo("Please provide a query to search for.")
        return
    
    memories = assistant.memory.search(query_str, limit)
    
    if not memories:
        click.echo("No memories found matching your query.")
        return
    
    click.echo(f"Found {len(memories)} memories matching your query:\n")
    
    for i, memory in enumerate(memories, 1):
        click.echo(f"{i}. {memory['memory']}")
        if i < len(memories):
            click.echo("")

@memory.command()
@click.argument('state', type=click.Choice(['on', 'off']), required=False)
def toggle(state):
    """Toggle the memory system on or off"""
    assistant = get_cliche_instance()
    
    if state is None:
        # Just report current status
        status = "enabled" if assistant.memory.enabled else "disabled"
        click.echo(f"Memory system is currently {status}.")
        return
    
    enabled = state == "on"
    result = assistant.memory.toggle(enabled)
    
    if result:
        status = "enabled" if enabled else "disabled"
        click.echo(f"Memory system has been {status}.")
    else:
        click.echo("Failed to toggle memory system.")

@memory.command()
@click.argument('user_id', required=False)
def user(user_id):
    """Set the user ID for memories"""
    assistant = get_cliche_instance()
    
    if not assistant.memory.enabled:
        click.echo("Memory system is disabled. Use 'memory toggle on' to enable it.")
        return
    
    if user_id is None:
        # Just report current user ID
        click.echo(f"Current user ID: {assistant.memory.user_id}")
        return
    
    result = assistant.memory.set_user_id(user_id)
    
    if result:
        click.echo(f"User ID has been set to '{user_id}'.")
    else:
        click.echo("Failed to set user ID.")

@memory.command()
@click.option('--auto', type=click.Choice(['on', 'off']), help="Enable or disable auto memory")
def status(auto):
    """Get memory system status"""
    assistant = get_cliche_instance()
    
    try:
        # Get status
        status = assistant.memory.get_status()
        
        # Toggle auto_memory if requested
        if auto is not None:
            # Update memory config
            memory_config = assistant.config.config.get("memory", {})
            memory_config["auto_memory"] = auto == "on"
            assistant.config.config["memory"] = memory_config
            
            # Save config
            assistant.config.save_config(assistant.config.config)
            
            # Update instance state
            assistant.memory.auto_memory = memory_config["auto_memory"]
            
            # Update status
            status["auto_memory"] = assistant.memory.auto_memory
            
            auto_status = "enabled" if assistant.memory.auto_memory else "disabled"
            click.echo(f"Auto memory is now {auto_status}")
        
        # Display status
        click.echo("\nMemory System Status:")
        click.echo(f"  Enabled: {status['enabled']}")
        click.echo(f"  Provider: {status['provider']}")
        click.echo(f"  User ID: {status['user_id']}")
        click.echo(f"  Auto Memory: {status['auto_memory']}")
        click.echo(f"  Data Directory: {status['data_dir']}")
        click.echo(f"  Collection Name: {status['collection_name']}")
        click.echo(f"  Profile Enabled: {status['profile_enabled']}")
        
        # Display profile if it exists
        if status['profile']:
            click.echo("\nUser Profile:")
            for key, value in status['profile'].items():
                click.echo(f"  {key.capitalize()}: {value}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

@memory.group()
def profile():
    """Manage user profile"""
    pass

@profile.command()
@click.argument('field', required=True)
@click.argument('value', required=True)
def set(field, value):
    """Set a user profile field"""
    assistant = get_cliche_instance()
    
    if not assistant.memory.enabled:
        click.echo("Memory system is disabled. Use 'memory toggle on' to enable it.")
        return
    
    try:
        # Set profile field
        success = assistant.memory.set_profile_field(field, value)
        
        if success:
            click.echo(f"Profile field '{field}' set to '{value}'")
            
            # Store as a memory as well for backward compatibility
            memory_content = f"My {field} is {value}."
            assistant.memory.add(memory_content, {"type": "profile", "field": field})
            
            return
        else:
            click.echo(f"Failed to set profile field '{field}'")
            return
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return

@profile.command()
@click.argument('enabled', type=click.Choice(['on', 'off']), required=True)
def toggle(enabled):
    """Toggle user profile on/off"""
    assistant = get_cliche_instance()
    
    try:
        # Toggle profile
        success = assistant.memory.toggle_profile(enabled == "on")
        
        if success:
            status = "enabled" if assistant.memory.profile_enabled else "disabled"
            click.echo(f"User profile is now {status}")
            return
        else:
            click.echo("Failed to toggle user profile")
            return
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return

@profile.command()
def clear():
    """Clear the user profile"""
    assistant = get_cliche_instance()
    
    try:
        # Clear profile
        success = assistant.memory.clear_profile()
        
        if success:
            click.echo("User profile cleared")
            return
        else:
            click.echo("Failed to clear user profile")
            return
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return
