"""
Remember command for CLIche.

This is a stub implementation while the memory system is being rebuilt.

Made with ❤️ by Pink Pixel
"""
import click
from ..core import get_cliche_instance

@click.command()
@click.argument('content', nargs=-1)
def remember(content):
    """Store a new memory"""
    COMING_SOON = "⚠️ New memory system coming soon! This feature is currently being rebuilt."
    
    assistant = get_cliche_instance()
    
    if not assistant.memory.enabled:
        click.echo(click.style("⚠️ Memory system is disabled. Use 'memory toggle on' to enable it.", fg="yellow"))
        return
    
    content_str = " ".join(content)
    if not content_str:
        click.echo(click.style("❌ Please provide memory content to store.", fg="red"))
        return
    
    click.echo(click.style(COMING_SOON, fg="yellow"))
    
    # Call stub memory system for compatibility
    memory_id = assistant.memory.add(content_str)
    if memory_id:
        click.echo(click.style(f"Note: Your memory request has been recorded but not stored in the database.", fg="blue")) 