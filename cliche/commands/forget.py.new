"""
Forget command for CLIche.

This is a stub implementation while the memory system is being rebuilt.

Made with ❤️ by Pink Pixel
"""
import click
from ..core import get_cliche_instance

@click.command()
@click.argument('term', nargs=-1)
def forget(term):
    """Remove a specific memory containing the given terms"""
    COMING_SOON = "⚠️ New memory system coming soon! This feature is currently being rebuilt."
    
    if not term:
        click.echo(click.style("Please provide a search term to find memories to remove", fg="yellow"))
        return
    
    # Get stub response
    term_str = " ".join(term)
    
    # Display coming soon message
    click.echo(click.style(COMING_SOON, fg="yellow"))
    
    # Just for log compatibility
    cliche = get_cliche_instance()
    if hasattr(cliche, 'memory') and cliche.memory:
        cliche.memory.remove_memory(term_str) 