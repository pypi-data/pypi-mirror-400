"""
Magneto - Tool for batch converting torrent files to magnet links
"""
__version__ = "0.1.1"
__author__ = "Yuze Xie"

from pathlib import Path
from typing import Tuple, Dict, Union

from .core import TorrentConverter
from .parser import ArgumentParser
from .ui import UI
from .utils import is_url

__all__ = ["TorrentConverter", "ArgumentParser", "UI", "torrent_to_magnet"]


def torrent_to_magnet(
    input_source: Union[str, Path],
    include_trackers: bool = False
) -> Tuple[str, str, Dict]:
    """
    Convert a torrent file or URL to a magnet link.
    
    This is a convenient entry point function that can be used directly in code
    without going through the CLI.
    
    Args:
        input_source: Path to torrent file (str or Path) or URL of torrent file
        include_trackers: Whether to include tracker information in the magnet link
            (default: False)
    
    Returns:
        A tuple containing three elements:
        - magnet_link (str): Generated magnet link
        - info_hash (str): Torrent info hash (hexadecimal string, uppercase)
        - metadata (Dict): Dictionary containing the following keys:
            - name: Torrent name
            - trackers: List of trackers (included even if include_trackers=False)
            - info_hash: Info hash
            - file_size: File size in bytes
            - source_url: Source URL if input is a URL
    
    Raises:
        IOError: File read failed or URL download failed
        ValueError: Torrent file format error
        ImportError: Missing required dependency (bencode.py)
    
    Example:
        >>> from magneto import torrent_to_magnet
        >>> 
        >>> # Convert from file path
        >>> magnet, hash, meta = torrent_to_magnet("path/to/file.torrent")
        >>> print(magnet)
        magnet:?xt=urn:btih:ABC123...
        >>> 
        >>> # Convert from URL
        >>> magnet, hash, meta = torrent_to_magnet("https://example.com/file.torrent")
        >>> 
        >>> # Include trackers
        >>> magnet, hash, meta = torrent_to_magnet("file.torrent", include_trackers=True)
    """
    converter = TorrentConverter()
    
    # Check if input is a URL
    input_str = str(input_source)
    if is_url(input_str):
        return converter.convert_from_url(input_str, include_trackers=include_trackers)
    else:
        # Handle file path
        torrent_path = Path(input_source)
        if not torrent_path.exists():
            raise IOError(f"File does not exist: {torrent_path}")
        return converter.convert(torrent_path, include_trackers=include_trackers)
