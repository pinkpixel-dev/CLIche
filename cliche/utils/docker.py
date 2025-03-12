"""
Docker-related utility functions
"""
import json
import subprocess
import logging
from typing import Dict, List, Optional

# Set up logging
logger = logging.getLogger(__name__)

def get_docker_containers() -> Dict:
    """Get list of running docker containers with their details."""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{json .}}'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode != 0:
            logger.debug(f"Docker command failed with return code {result.returncode}")
            return {}
            
        containers = {}
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    container = json.loads(line)
                    containers[container['ID']] = {
                        'name': container['Names'],
                        'image': container['Image'],
                        'status': container['Status'],
                        'ports': container['Ports']
                    }
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse Docker container JSON: {e}")
                    continue
                    
        return containers
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug(f"Docker command failed: {str(e)}")
        return {}

def get_docker_images() -> List[Dict]:
    """Get list of available docker images."""
    try:
        result = subprocess.run(
            ['docker', 'images', '--format', '{{json .}}'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode != 0:
            logger.debug(f"Docker images command failed with return code {result.returncode}")
            return []
            
        images = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    image = json.loads(line)
                    images.append({
                        'repository': image.get('Repository', 'N/A'),
                        'tag': image.get('Tag', 'N/A'),
                        'id': image.get('ID', 'N/A'),
                        'created': image.get('CreatedSince', 'N/A'),
                        'size': image.get('Size', 'N/A')
                    })
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse Docker image JSON: {e}")
                    continue
                    
        return images
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug(f"Docker images command failed: {str(e)}")
        return []

def is_docker_running() -> bool:
    """Check if Docker daemon is running."""
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False
