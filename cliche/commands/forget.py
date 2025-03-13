"""
Forget command for CLIche.

This command allows removing memories from the CLIche memory system.

Made with ❤️ by Pink Pixel
"""
import click
from ..core import get_cliche_instance

@click.command()
@click.argument('content', nargs=-1)
@click.option('--id', '-i', help='Specific memory ID to forget')
@click.option('--all', '-a', is_flag=True, help='Remove all memories')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def forget(content, id, all, confirm):
    """Remove a specific memory containing given terms or by ID
    
    Examples:
        cliche forget --id 123456 (removes memory with specific ID)
        cliche forget capital of France (searches and removes memories about 'capital of France')
        cliche forget --all (removes all memories after confirmation)
    """
    assistant = get_cliche_instance()
    
    if not assistant.memory.enabled:
        click.echo(click.style("⚠️ Memory system is disabled. Use 'memory toggle on' to enable it.", fg="yellow"))
        return
    
    # Case 1: Remove all memories
    if all:
        if not confirm:
            confirmation = click.confirm(click.style("⚠️ Are you sure you want to remove ALL memories?", fg="yellow"))
            if not confirmation:
                click.echo("Operation cancelled.")
                return
        
        try:
            assistant.memory.clear_memories()
            click.echo(click.style("✅ All memories have been removed.", fg="green"))
        except Exception as e:
            click.echo(click.style(f"❌ Error removing all memories: {str(e)}", fg="red"))
        return
    
    # Case 2: Remove by ID
    if id:
        try:
            success = assistant.memory.remove_memory(id)
            if success:
                click.echo(click.style(f"✅ Memory with ID {id} removed successfully.", fg="green"))
            else:
                click.echo(click.style(f"❌ No memory found with ID {id}.", fg="red"))
        except Exception as e:
            click.echo(click.style(f"❌ Error removing memory: {str(e)}", fg="red"))
        return
    
    # Case 3: Remove by content search
    content_str = " ".join(content)
    if not content_str:
        click.echo(click.style("❌ Please provide memory content to search for, a specific ID, or use --all.", fg="red"))
        return
    
    # Search for memories matching the content
    search_results = assistant.memory.search(content_str, limit=5)
    
    if not search_results or len(search_results) == 0:
        click.echo(click.style(f"No memories found containing '{content_str}'.", fg="yellow"))
        return
    
    # Display found memories and ask which to remove
    click.echo(click.style(f"Found {len(search_results)} memories containing '{content_str}':", fg="blue"))
    
    for i, memory in enumerate(search_results):
        memory_id = memory.get("id", "unknown")
        memory_content = memory.get("content", "No content")[:100] + ("..." if len(memory.get("content", "")) > 100 else "")
        click.echo(f"{i+1}. [ID: {memory_id}]: {memory_content}")
    
    # Allow selecting memories to remove
    if not confirm:
        choices = click.prompt(
            "Enter numbers of memories to remove (comma-separated), 'all' to remove all listed, or 'cancel'",
            type=str,
            default="cancel"
        )
        
        if choices.lower() == "cancel":
            click.echo("Operation cancelled.")
            return
            
        if choices.lower() == "all":
            indices = range(len(search_results))
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in choices.split(",")]
                # Validate indices
                valid_indices = [idx for idx in indices if 0 <= idx < len(search_results)]
                if not valid_indices:
                    click.echo(click.style("❌ No valid selection made.", fg="red"))
                    return
                indices = valid_indices
            except ValueError:
                click.echo(click.style("❌ Invalid selection format. Use comma-separated numbers.", fg="red"))
                return
    else:
        indices = range(len(search_results))
    
    # Remove selected memories
    removed_count = 0
    for idx in indices:
        memory_id = search_results[idx].get("id", None)
        if memory_id:
            try:
                if assistant.memory.remove_memory(memory_id):
                    removed_count += 1
            except Exception as e:
                click.echo(click.style(f"❌ Error removing memory {memory_id}: {str(e)}", fg="red"))
    
    if removed_count > 0:
        click.echo(click.style(f"✅ Successfully removed {removed_count} memories.", fg="green"))
    else:
        click.echo(click.style("❌ No memories were removed.", fg="red")) 