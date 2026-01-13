"""
Utility Functions for Nyx System
Handles configuration loading, JSON operations, and async helpers.
"""
import os
import json
import asyncio
from typing import Any, Dict
from pathlib import Path
from .logger import logger

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    logger.warning("PyYAML not found. YAML config loading will fail.")


# Global Data Directory
# For production/published package, we MUST use the user's home directory.
# Writing to site-packages or specific desktop paths causes permission errors and failure on other machines.
NYX_DATA_DIR = Path.home() / ".nyx"


def load_config(path: str = None) -> Dict[str, Any]:
    """
    Load configuration with fallback strategies.
    Order: Specified Path -> NYX_DATA_DIR/config.yaml
    """
    if path:
        path_obj = Path(path)
    else:
        path_obj = NYX_DATA_DIR / "config.yaml"
    
    if not path_obj.exists():
        # Last ditch: Check if path provided was relative and missing
        if path and not Path(path).is_absolute():
             fallback = NYX_DATA_DIR / path
             if fallback.exists():
                 path_obj = fallback
        
        if not path_obj.exists():
             return {}

    try:
        content = path_obj.read_text(encoding='utf-8')
        
        if HAS_YAML:
            config = yaml.safe_load(content)
        else:
            # Fallback to JSON if YAML not available
            config = json.loads(content)
            
        return _expand_env_vars(config)
        
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


def _expand_env_vars(item: Any) -> Any:
    """Recursively expand environment variables in config values."""
    if isinstance(item, dict):
        return {k: _expand_env_vars(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [_expand_env_vars(i) for i in item]
    elif isinstance(item, str) and item.startswith("${") and item.endswith("}"):
        env_key = item[2:-1]
        return os.getenv(env_key, item)
    return item


async def run_async_command(cmd: str) -> str:
    """Execute shell command asynchronously and return output."""
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    if proc.returncode != 0:
        raise Exception(f"Command failed: {cmd}\nError: {stderr.decode()}")
    
    return stdout.decode().strip()


def save_json(path: Path, data: Any) -> None:
    """Save data to JSON file with pretty printing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(path: Path) -> Any:
    """Load data from JSON file."""
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
