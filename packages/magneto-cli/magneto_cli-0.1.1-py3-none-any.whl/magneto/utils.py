"""
Utility functions module
"""
import re
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse


def collect_torrent_files(
    input_path: Path, 
    recursive: bool = False,
    case_sensitive: bool = False
) -> List[Path]:
    """
    Collect torrent files
    
    Args:
        input_path: Input path (file or directory)
        recursive: Whether to recursively search subdirectories
        case_sensitive: Whether to be case-sensitive
        
    Returns:
        List of torrent file paths
    """
    torrent_files = []
    
    if input_path.is_file():
        # Single file
        suffix = input_path.suffix.lower() if not case_sensitive else input_path.suffix
        if suffix == '.torrent':
            torrent_files.append(input_path)
    elif input_path.is_dir():
        # Directory
        if recursive:
            # Recursive search
            pattern = '**/*.torrent' if not case_sensitive else '**/*.TORRENT'
            torrent_files.extend(list(input_path.glob(pattern)))
            if case_sensitive:
                torrent_files.extend(list(input_path.glob('**/*.torrent')))
        else:
            # Current directory only
            torrent_files.extend(list(input_path.glob('*.torrent')))
            torrent_files.extend(list(input_path.glob('*.TORRENT')))
    
    # Remove duplicates and sort
    torrent_files = sorted(set(torrent_files))
    return torrent_files


def get_output_path(
    input_path: Path,
    output_path: Optional[Path] = None,
    default_name: str = "magnet_links.txt"
) -> Path:
    """
    Determine output file path
    
    Args:
        input_path: Input path
        output_path: User-specified output path
        default_name: Default output file name
        
    Returns:
        Output file path
    """
    if output_path:
        # If specified path is a directory, add default filename
        if output_path.is_dir() or (not output_path.suffix and not output_path.exists()):
            return output_path / default_name
        return output_path
    
    # Auto-determine output path
    if input_path.is_dir():
        return input_path / default_name
    else:
        return input_path.parent / default_name


def format_file_size(size: int) -> str:
    """
    Format file size
    
    Args:
        size: File size in bytes
        
    Returns:
        Formatted file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def is_url(input_string: str) -> bool:
    """
    Check if input string is a valid URL
    
    Args:
        input_string: Input string to check
        
    Returns:
        True if input is a valid URL, False otherwise
    """
    if not input_string or not isinstance(input_string, str):
        return False
    
    # Remove leading/trailing whitespace
    input_string = input_string.strip()
    
    # Basic URL pattern check
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if url_pattern.match(input_string):
        return True
    
    # Also try urlparse for more robust checking
    try:
        result = urlparse(input_string)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False
