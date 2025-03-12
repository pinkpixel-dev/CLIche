"""
GPU information utilities
"""
import subprocess
import logging
from typing import Tuple, Dict, Any, List, Optional

# Set up logging
logger = logging.getLogger(__name__)

try:
    import py3nvml as nvml
    HAS_NVIDIA = True
except ImportError:
    HAS_NVIDIA = False

def get_gpu_info() -> Tuple[str, str]:
    """Get GPU information and utilization."""
    try:
        # Try nvidia-smi first
        result = subprocess.run(['nvidia-smi', '--query-gpu=gpu_name,utilization.gpu', '--format=csv,noheader,nounits'],
                            capture_output=True, text=True, check=True, timeout=2)
        if result.stdout.strip():
            gpu_name, utilization = result.stdout.strip().split(',', 1)  # Use maxsplit=1 to handle commas in GPU names
            return gpu_name.strip(), f"{utilization.strip()}%"
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug(f"nvidia-smi command failed: {str(e)}")
        # If nvidia-smi fails, try py3nvml
        if HAS_NVIDIA:
            try:
                nvml.nvmlInit()
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                name = nvml.nvmlDeviceGetName(handle)
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                nvml.nvmlShutdown()
                return name, f"{util.gpu}%"
            except Exception as e:
                logger.debug(f"py3nvml failed: {str(e)}")

        # Try lspci as a last resort
        try:
            result = subprocess.run('lspci | grep -i "vga\\|3d\\|display"', 
                                shell=True, capture_output=True, text=True, timeout=2)
            if result.stdout:
                return result.stdout.strip().split(':')[-1].strip(), "N/A"
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.debug(f"lspci command failed: {str(e)}")

    return "No GPU detected", "N/A"

def get_detailed_gpu_info() -> List[Dict[str, Any]]:
    """
    Get detailed information about all available GPUs.
    
    Returns:
        List of dictionaries containing detailed GPU information
    """
    gpus = []
    
    # Try nvidia-smi first (most detailed information)
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.used,memory.free', 
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, check=True, timeout=2
        )
        
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                parts = [part.strip() for part in line.split(',')]
                
                # Handle case where GPU name contains commas
                if len(parts) > 8:
                    # Reconstruct the name from extra parts
                    name_parts = parts[1:-6]
                    name = ','.join(name_parts)
                    # Reassemble the parts with the fixed name
                    parts = [parts[0], name] + parts[-6:]
                
                if len(parts) >= 8:
                    gpu = {
                        "index": parts[0],
                        "name": parts[1],
                        "temperature": parts[2],
                        "gpu_utilization": parts[3],
                        "memory_utilization": parts[4],
                        "memory_total": parts[5],
                        "memory_used": parts[6],
                        "memory_free": parts[7]
                    }
                    gpus.append(gpu)
        
        return gpus
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug(f"nvidia-smi detailed command failed: {str(e)}")
    
    # If nvidia-smi fails, try py3nvml
    if HAS_NVIDIA:
        try:
            nvml.nvmlInit()
            device_count = nvml.nvmlDeviceGetCount()
            
            for i in range(device_count):
                try:
                    handle = nvml.nvmlDeviceGetHandleByIndex(i)
                    name = nvml.nvmlDeviceGetName(handle)
                    
                    # Get memory info
                    mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                    
                    # Get utilization rates
                    util = nvml.nvmlDeviceGetUtilizationRates(handle)
                    
                    # Get temperature (may not be available on all devices)
                    temp = None
                    try:
                        temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
                    except Exception:
                        pass
                    
                    gpu = {
                        "index": str(i),
                        "name": name,
                        "temperature": str(temp) if temp is not None else "N/A",
                        "gpu_utilization": str(util.gpu),
                        "memory_utilization": str(util.memory),
                        "memory_total": str(mem_info.total // (1024 * 1024)),
                        "memory_used": str(mem_info.used // (1024 * 1024)),
                        "memory_free": str(mem_info.free // (1024 * 1024))
                    }
                    
                    gpus.append(gpu)
                except Exception as e:
                    logger.debug(f"Error getting info for GPU {i}: {str(e)}")
            
            nvml.nvmlShutdown()
            
            if gpus:
                return gpus
        except Exception as e:
            logger.debug(f"py3nvml detailed info failed: {str(e)}")
    
    # Last resort: try to get basic info from lspci
    try:
        result = subprocess.run('lspci | grep -i "vga\\|3d\\|display"', 
                            shell=True, capture_output=True, text=True, timeout=2)
        if result.stdout:
            for i, line in enumerate(result.stdout.strip().split('\n')):
                gpu_name = line.split(':')[-1].strip()
                gpu = {
                    "index": str(i),
                    "name": gpu_name,
                    "temperature": "N/A",
                    "gpu_utilization": "N/A",
                    "memory_utilization": "N/A",
                    "memory_total": "N/A",
                    "memory_used": "N/A",
                    "memory_free": "N/A"
                }
                gpus.append(gpu)
            
            return gpus
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug(f"lspci detailed command failed: {str(e)}")
    
    # If all methods fail, return a placeholder
    return [{
        "index": "0",
        "name": "No GPU detected",
        "temperature": "N/A",
        "gpu_utilization": "N/A",
        "memory_utilization": "N/A",
        "memory_total": "N/A",
        "memory_used": "N/A",
        "memory_free": "N/A"
    }]
