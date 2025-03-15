"""
Memory management commands for CLIche.

This module contains the commands for managing the memory system.

Made with ❤️ by Pink Pixel
"""
import os
import click
import json
from ..core import get_cliche_instance
from pathlib import Path
import shutil

@click.group()
def memory():
    """Memory management commands."""
    pass

@memory.command()
def status():
    """Display memory system status."""
    assistant = get_cliche_instance()
    
    # Get memory status
    status_info = assistant.memory.get_status()
    
    # Display status information
    click.echo(click.style("Memory System Status", fg="blue", bold=True))
    click.echo("─" * 40)
    
    # Auto-memory status
    auto_memory = "✅ On" if status_info.get("auto_memory", False) else "❌ Off"
    click.echo(f"Auto-memory: {click.style(auto_memory, fg='green' if status_info.get('auto_memory', False) else 'red')}")
    
    # User ID
    user_id = status_info.get("user_id", "Not set")
    click.echo(f"User ID: {click.style(user_id, fg='blue')}")
    
    # Provider information
    provider = status_info.get("provider", "None")
    click.echo(f"Provider: {click.style(provider, fg='blue')}")
    
    # Memory count if available
    memory_count = status_info.get("memory_count", "Unknown")
    click.echo(f"Memory count: {click.style(str(memory_count), fg='blue')}")
    
    # Data directory
    data_dir = status_info.get("data_dir", "Unknown")
    click.echo(f"Data directory: {click.style(data_dir, fg='blue')}")
    
    # Retention settings
    memory_config = assistant.config.config.get("memory", {})
    retention_days = memory_config.get("retention_days", 0)
    max_memories = memory_config.get("max_memories", 0)
    
    # Format retention information
    retention_days_str = "indefinite (no time limit)" if retention_days == 0 else f"{retention_days} days"
    max_memories_str = "unlimited" if max_memories == 0 else str(max_memories)
    
    click.echo(f"Retention period: {click.style(retention_days_str, fg='blue')}")
    click.echo(f"Maximum memories: {click.style(max_memories_str, fg='blue')}")
    
    click.echo("─" * 40)
    click.echo("Commands:")
    click.echo(" - Toggle auto-memory: " + click.style("cliche memory automemory on/off", fg="cyan"))
    click.echo(" - Set retention policy: " + click.style("cliche memory retention --days <days> --max <count>", fg="cyan"))
    click.echo(" - Store memory: " + click.style("cliche remember 'your memory'", fg="cyan"))
    click.echo(" - Recall memory: " + click.style("cliche memory recall 'search query'", fg="cyan"))
    click.echo(" - Forget memory: " + click.style("cliche forget 'search query'", fg="cyan"))
    click.echo(" - Repair database: " + click.style("cliche memory repair", fg="cyan"))

@memory.command()
@click.argument('state', type=click.Choice(['on', 'off']), required=False)
def automemory(state):
    """Toggle auto-memory on/off."""
    assistant = get_cliche_instance()
    
    if state is None:
        # If no state is provided, show current status
        current_state = assistant.memory.get_status().get("auto_memory", False)
        state_str = "ON" if current_state else "OFF"
        click.echo(click.style(f"Auto-memory is currently {state_str}", fg="blue"))
        return
    
    # Set auto-memory state
    new_state = state.lower() == 'on'
    success = assistant.memory.set_auto_memory(new_state)
    
    if success:
        state_str = "ON" if new_state else "OFF"
        click.echo(click.style(f"✅ Auto-memory turned {state_str}", fg="green"))
    else:
        click.echo(click.style("❌ Failed to set auto-memory state", fg="red"))

@memory.command()
@click.argument('content', nargs=-1, required=False)
@click.option('--tags', '-t', help='Comma-separated tags for the memory')
@click.option('--category', '-c', help='Category for the memory')
def store(content, tags, category):
    """Store a new memory (alias for 'remember' command)"""
    # Get the remember command from commands
    from .remember import remember
    ctx = click.Context(remember, info_name='remember')
    
    # Convert content back to a tuple if provided
    content_tuple = content if content else tuple()
    
    # Call the remember command
    return remember.invoke(ctx, content_tuple, tags=tags, category=category)

@memory.command()
@click.argument('query', nargs=-1, required=False)
@click.option('--limit', '-l', default=5, help='Maximum number of results to return')
@click.option('--semantic/--keyword', default=True, help='Use semantic search or keyword search')
@click.option('--json', 'as_json', is_flag=True, help='Output results as JSON')
def recall(query, limit, semantic, as_json):
    """Search for memories."""
    assistant = get_cliche_instance()
    
    if not assistant.memory.enabled:
        click.echo(click.style("⚠️ Memory system is disabled. Use 'memory toggle on' to enable it.", fg="yellow"))
        return
    
    if not query:
        click.echo(click.style("Please provide a search query", fg="yellow"))
        return
    
    # Join the query terms
    query_str = " ".join(query)
    
    try:
        # Search for memories
        results = assistant.memory.search(query_str, limit=limit, semantic=semantic)
        
        if not results or len(results) == 0:
            click.echo(click.style(f"No memories found for query: '{query_str}'", fg="yellow"))
            return
        
        # Display results
        if as_json:
            click.echo(json.dumps(results, indent=2))
        else:
            click.echo(click.style(f"Found {len(results)} memories for '{query_str}':", fg="blue"))
            click.echo("─" * 40)
            
            for i, memory in enumerate(results):
                memory_id = memory.get("id", "unknown")
                memory_content = memory.get("content", "No content")
                
                # Get metadata fields
                metadata = memory.get("metadata", {})
                tags = metadata.get("tags", "")
                category = metadata.get("category", "None")
                timestamp = metadata.get("timestamp", "Unknown")
                
                # Format timestamp if it's a unix timestamp
                try:
                    import datetime
                    if timestamp.isdigit():
                        timestamp = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
                
                # Display memory
                click.echo(click.style(f"#{i+1} [ID: {memory_id}]", fg="cyan", bold=True))
                click.echo(memory_content)
                
                # Display metadata
                meta_items = []
                if category and category != "None":
                    meta_items.append(f"Category: {category}")
                if tags and len(tags) > 0:
                    meta_items.append(f"Tags: {tags}")
                if timestamp and timestamp != "Unknown":
                    meta_items.append(f"Time: {timestamp}")
                
                if meta_items:
                    click.echo(click.style("Metadata: " + " | ".join(meta_items), fg="blue"))
                
                if i < len(results) - 1:
                    click.echo("─" * 40)
    
    except Exception as e:
        click.echo(click.style(f"❌ Error searching memories: {str(e)}", fg="red"))

@memory.command()
@click.argument('term', nargs=-1)
def forget(term):
    """Remove a memory by ID or search terms.
    
    This is an alias for the 'forget' command. For more options like removing all memories,
    use 'cliche forget --all' directly.
    """
    # Convert term to a string
    term_str = " ".join(term)
    if not term_str:
        click.echo(click.style("Please provide a memory ID or search terms to forget", fg="yellow"))
        return
        
    # Call the direct forget command
    from .forget import forget as forget_cmd
    # Call with the appropriate arguments (term as content, no --id, no --all, no --confirm)
    forget_cmd.callback(content=term, id=None, all=False, confirm=False)

@memory.command()
@click.argument('user_id', required=False)
def user(user_id):
    """Set or show the user ID."""
    assistant = get_cliche_instance()
    
    if not user_id:
        # Display current user ID
        current_user_id = assistant.memory.user_id
        click.echo(f"Current user ID: {click.style(current_user_id, fg='blue')}")
        return
    
    # Set new user ID
    try:
        success = assistant.memory.set_user_id(user_id)
        if success:
            click.echo(click.style(f"✅ User ID set to: {user_id}", fg="green"))
        else:
            click.echo(click.style(f"❌ Failed to set user ID", fg="red"))
    except Exception as e:
        click.echo(click.style(f"❌ Error setting user ID: {str(e)}", fg="red"))

@memory.command()
@click.option('--days', type=int, help='Number of days to retain memories (0 = keep forever)')
@click.option('--max', type=int, help='Maximum number of memories to keep (0 = unlimited)')
@click.option('--reset', is_flag=True, help='Reset retention settings to keep memories indefinitely')
def retention(days, max, reset):
    """Set memory retention policy.
    
    Configure how long memories are kept and the maximum number to store.
    
    Examples:
      - Keep memories for 30 days: cliche memory retention --days 30
      - Keep only the latest 100 memories: cliche memory retention --max 100
      - Keep all memories indefinitely: cliche memory retention --reset
    """
    assistant = get_cliche_instance()
    
    # Get current retention settings from config
    memory_config = assistant.config.config.get("memory", {})
    current_days = memory_config.get("retention_days", 0)
    current_max = memory_config.get("max_memories", 0)
    
    # Handle reset flag first
    if reset:
        memory_config["retention_days"] = 0
        memory_config["max_memories"] = 0
        current_days = 0
        current_max = 0
        
        # Update memory object's retention settings directly
        assistant.memory.retention_days = 0
        assistant.memory.max_memories = 0
        
        # Save updated config
        try:
            assistant.config.config["memory"] = memory_config
            success = assistant.config.save_config(assistant.config.config)
            
            if success:
                click.echo(click.style("✅ Memory retention settings reset to keep all memories indefinitely", fg="green"))
                return
            else:
                click.echo(click.style("❌ Failed to reset memory retention settings", fg="red"))
                return
        except Exception as e:
            click.echo(click.style(f"❌ Error while saving config: {str(e)}", fg="red"))
            return
    
    # If no options specified, show current settings
    if days is None and max is None:
        days_str = "indefinitely (no time limit)" if current_days == 0 else f"{current_days} days"
        max_str = "all memories (no limit)" if current_max == 0 else f"maximum {current_max} memories"
        
        click.echo(click.style("Memory Retention Settings", fg="blue", bold=True))
        click.echo("─" * 40)
        click.echo(f"Retention period: {click.style(days_str, fg='cyan')}")
        click.echo(f"Maximum memories: {click.style(max_str, fg='cyan')}")
        
        # Show examples of how to set
        click.echo("\nExamples:")
        click.echo(" - Keep memories for 30 days: " + click.style("cliche memory retention --days 30", fg="green"))
        click.echo(" - Keep only latest 100 memories: " + click.style("cliche memory retention --max 100", fg="green"))
        click.echo(" - Reset to keep all memories indefinitely: " + click.style("cliche memory retention --reset", fg="green"))
        return 

    # Update retention settings
    updated = False
    if days is not None:
        memory_config["retention_days"] = days
        assistant.memory.retention_days = days
        updated = True
    
    if max is not None:
        memory_config["max_memories"] = max
        assistant.memory.max_memories = max
        updated = True
    
    if updated:
        # Save updated config
        assistant.config.config["memory"] = memory_config
        success = assistant.config.save_config(assistant.config.config)
        
        if success:
            # Format for display
            days_str = "indefinitely (no time limit)" if memory_config["retention_days"] == 0 else f"{memory_config['retention_days']} days"
            max_str = "all memories (no limit)" if memory_config["max_memories"] == 0 else f"maximum {memory_config['max_memories']} memories"
            
            click.echo(click.style("✅ Memory retention settings updated:", fg="green"))
            click.echo(f"Retention period: {click.style(days_str, fg='cyan')}")
            click.echo(f"Maximum memories: {click.style(max_str, fg='cyan')}")
        else:
            click.echo(click.style("❌ Failed to update memory retention settings", fg="red"))
    else:
        click.echo(click.style("No changes made to retention settings", fg="yellow"))

@memory.command()
@click.option('--confirm', '-y', is_flag=True, help='Skip confirmation')
def repair(confirm):
    """Repair the memory database.
    
    This command fixes database problems, especially 'database disk image is malformed' errors
    that may occur with the search functionality. It rebuilds the full-text search index.
    """
    assistant = get_cliche_instance()
    
    if not confirm:
        click.echo(click.style("⚠️ This will rebuild the memory search index.", fg="yellow"))
        click.echo("Your memories will be preserved, but this operation may take some time.")
        if not click.confirm("Do you want to continue?"):
            click.echo("Operation cancelled.")
            return
    
    click.echo("Repairing memory database...")
    
    try:
        success = assistant.memory.repair_database()
        if success:
            click.echo(click.style("✅ Memory database repaired successfully!", fg="green"))
        else:
            click.echo(click.style("❌ Failed to repair memory database.", fg="red"))
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red")) 