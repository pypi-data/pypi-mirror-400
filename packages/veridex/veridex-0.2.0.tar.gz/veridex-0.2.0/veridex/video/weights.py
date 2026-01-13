"""Centralized configuration for model weights."""
from typing import Optional
import os

# Default weight URLs
# These are placeholders - update with real URLs when weights are available
DEFAULT_WEIGHTS = {
    "physnet": {
        "url": "https://github.com/ADITYAMAHAKALI/veridex/releases/download/v0.1.0/physnet.pth",
        "filename": "physnet.pth",
        "sha256": None,  # Add checksum when real weights are available
    },
    "i3d": {
        "url": "https://github.com/ADITYAMAHAKALI/veridex/releases/download/v0.1.0/i3d_rgb.pth",
        "filename": "i3d_rgb.pth",
        "sha256": None,
    },
    "syncnet": {
        "url": "http://www.robots.ox.ac.uk/~vgg/software/lipsync/data/syncnet_v2.model",
        "filename": "syncnet_v2.pth",
        "sha256": None,
    }
}

# Allow override via environment variables
# Example: export VERIDEX_PHYSNET_URL="https://my-server.com/physnet.pth"
def get_weight_config(model_name: str) -> dict:
    """
    Get weight configuration for a model.
    
    Checks environment variables first, then falls back to defaults.
    
    Args:
        model_name: One of 'physnet', 'i3d', 'syncnet'
        
    Returns:
        Dict with 'url', 'filename', 'sha256'
        
    Example:
        >>> config = get_weight_config('physnet')
        >>> print(config['url'])
    """
    if model_name not in DEFAULT_WEIGHTS:
        raise ValueError(f"Unknown model: {model_name}. Use one of {list(DEFAULT_WEIGHTS.keys())}")
    
    config = DEFAULT_WEIGHTS[model_name].copy()
    
    # Check for environment variable override
    env_var = f"VERIDEX_{model_name.upper()}_URL"
    if env_var in os.environ:
        config['url'] = os.environ[env_var]
    
    return config

def set_weight_url(model_name: str, url: str, sha256: Optional[str] = None):
    """
    Programmatically override weight URL.
    
    Args:
        model_name: One of 'physnet', 'i3d', 'syncnet'
        url: New URL to use
        sha256: Optional SHA256 checksum
        
    Example:
        >>> from veridex.video.weights import set_weight_url
        >>> set_weight_url('physnet', 'https://my-server.com/physnet.pth')
    """
    if model_name not in DEFAULT_WEIGHTS:
        raise ValueError(f"Unknown model: {model_name}")
    
    DEFAULT_WEIGHTS[model_name]['url'] = url
    if sha256 is not None:
        DEFAULT_WEIGHTS[model_name]['sha256'] = sha256
