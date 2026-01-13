import os
import hashlib
from typing import Optional

def download_file(url: str, filepath: str, sha256: Optional[str] = None) -> None:
    """
    Download a file from a URL to a specific filepath, with optional SHA256 verification.
    Uses torch.hub.download_url_to_file if available for progress bar, else standard request.

    Args:
        url: Source URL.
        filepath: Destination path on disk.
        sha256: Expected SHA256 hash string.
    """
    try:
        import torch
        # torch.hub.download_url_to_file handles progress bars nicely
        torch.hub.download_url_to_file(url, filepath, hash_prefix=sha256, progress=True)
    except ImportError:
        # Fallback if torch is not installed (though 'video' depends on it)
        import urllib.request
        from tqdm import tqdm

        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if os.path.exists(filepath):
            if sha256:
                # Check hash
                with open(filepath, "rb") as f:
                    digest = hashlib.sha256(f.read()).hexdigest()
                if digest == sha256:
                    return
            else:
                return

        with tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=os.path.basename(filepath)) as t:
            def reporthook(blocknum, blocksize, totalsize):
                t.total = totalsize
                t.update(blocknum * blocksize - t.n)

            urllib.request.urlretrieve(url, filepath, reporthook=reporthook)

def get_cache_dir(subdir: str = "models") -> str:
    """Get the local cache directory for veridex."""
    home = os.path.expanduser("~")
    cache_dir = os.path.join(home, ".cache", "veridex", subdir)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir
