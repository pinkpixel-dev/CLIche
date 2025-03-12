"""
System-related commands
"""
import click
import psutil
import platform
from datetime import datetime
from ..utils.gpu import get_gpu_info, get_detailed_gpu_info
from ..utils.docker import get_docker_containers, is_docker_running, get_docker_images

@click.command()
@click.option('--detailed', '-d', is_flag=True, help='Show detailed information')
def system(detailed):
    """Display system information"""
    cpu_count = psutil.cpu_count()
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    gpu_name, gpu_usage = get_gpu_info()
    
    click.echo("\n🖥️  System Information:")
    click.echo(f"OS: {platform.system()} {platform.release()}")
    click.echo(f"CPU Cores: {cpu_count}")
    click.echo(f"CPU Usage: {cpu_usage}%")
    click.echo(f"Memory: {memory.used/1024/1024/1024:.1f}GB used of {memory.total/1024/1024/1024:.1f}GB ({memory.percent}%)")
    click.echo(f"Disk: {disk.used/1024/1024/1024:.1f}GB used of {disk.total/1024/1024/1024:.1f}GB ({disk.percent}%)")
    
    if gpu_name != "No GPU detected":
        click.echo(f"GPU: {gpu_name}")
        click.echo(f"GPU Usage: {gpu_usage}")
    
    # Show detailed information if requested
    if detailed:
        # Show detailed CPU information
        click.echo("\n📊 CPU Details:")
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            click.echo(f"CPU Frequency: {cpu_freq.current:.1f} MHz")
        
        # Show per-core CPU usage
        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
        for i, usage in enumerate(per_cpu):
            click.echo(f"Core {i}: {usage}%")
        
        # Show detailed GPU information
        gpus = get_detailed_gpu_info()
        if gpus and gpus[0]["name"] != "No GPU detected":
            click.echo("\n🎮 GPU Details:")
            for gpu in gpus:
                click.echo(f"GPU {gpu['index']}: {gpu['name']}")
                if gpu['temperature'] != "N/A":
                    click.echo(f"  Temperature: {gpu['temperature']}°C")
                if gpu['gpu_utilization'] != "N/A":
                    click.echo(f"  GPU Utilization: {gpu['gpu_utilization']}%")
                if gpu['memory_utilization'] != "N/A":
                    click.echo(f"  Memory Utilization: {gpu['memory_utilization']}%")
                if gpu['memory_total'] != "N/A":
                    click.echo(f"  Memory: {gpu['memory_used']}MB used of {gpu['memory_total']}MB")
        
        # Show network information
        net_io = psutil.net_io_counters()
        click.echo("\n🌐 Network:")
        click.echo(f"Bytes Sent: {net_io.bytes_sent/1024/1024:.1f}MB")
        click.echo(f"Bytes Received: {net_io.bytes_recv/1024/1024:.1f}MB")
        
        # Show disk I/O information
        try:
            disk_io = psutil.disk_io_counters()
            click.echo("\n💾 Disk I/O:")
            click.echo(f"Read: {disk_io.read_bytes/1024/1024:.1f}MB")
            click.echo(f"Write: {disk_io.write_bytes/1024/1024:.1f}MB")
        except Exception:
            pass
    
    # Docker containers
    if is_docker_running():
        docker_containers = get_docker_containers()
        if docker_containers:
            click.echo("\n🐳 Docker Containers:")
            for container in docker_containers.values():
                click.echo(f"- {container['name']} ({container['status']})")
                
            if detailed:
                # Show Docker images if detailed view is requested
                docker_images = get_docker_images()
                if docker_images:
                    click.echo("\n📦 Docker Images:")
                    for image in docker_images[:5]:  # Limit to 5 images to avoid cluttering the output
                        click.echo(f"- {image['repository']}:{image['tag']} ({image['size']})")
                    
                    if len(docker_images) > 5:
                        click.echo(f"  ... and {len(docker_images) - 5} more")
    
    click.echo(f"\nCurrent Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
