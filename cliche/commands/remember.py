"""
Remember command for CLIche.

This command allows storing memories in the CLIche memory system.

Made with ❤️ by Pink Pixel
"""
import click
import time
from ..core import get_cliche_instance

@click.command()
@click.argument('content', nargs=-1)
@click.option('--tags', '-t', help='Comma-separated tags for the memory')
@click.option('--category', '-c', help='Category for the memory')
def remember(content, tags, category):
    """Store a new memory
    
    Examples:
        cliche remember The capital of France is Paris
        cliche remember -t geography,europe,capitals The capital of France is Paris
        cliche remember -c fact Python was created by Guido van Rossum
    """
    assistant = get_cliche_instance()
    
    if not assistant.memory.enabled:
        click.echo(click.style("⚠️ Memory system is disabled. Use 'memory toggle on' to enable it.", fg="yellow"))
        return
    
    content_str = " ".join(content)
    if not content_str:
        click.echo(click.style("❌ Please provide memory content to store.", fg="red"))
        return
    
    # Prepare metadata
    metadata = {
        "timestamp": str(int(time.time())),
        "user_id": assistant.memory.user_id,
        "type": "user_memory"
    }
    
    # Add tags if provided (store as comma-separated string)
    if tags:
        metadata["tags"] = tags  # Store as original string instead of list
    
    # Add category if provided
    if category:
        metadata["category"] = category
    
    # Add the memory
    memory_id = assistant.memory.add(content_str, metadata)
    
    if memory_id:
        click.echo(click.style("✅ Memory stored successfully!", fg="green"))
        click.echo(f"ID: {memory_id}")
        
        # Show metadata summary
        meta_summary = []
        if category:
            meta_summary.append(f"Category: {category}")
        if tags:
            meta_summary.append(f"Tags: {tags}")
        
        if meta_summary:
            click.echo(click.style("Metadata: " + ", ".join(meta_summary), fg="blue"))
    else:
        click.echo(click.style("❌ Failed to store memory. Memory system may not be ready.", fg="red")) 