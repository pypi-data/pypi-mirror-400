"""
Core conversion module - Handles torrent file to magnet link conversion
"""
import hashlib
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import bencode
except ImportError:
    bencode = None


class TorrentConverter:
    """Torrent file converter"""
    
    def __init__(self):
        if bencode is None:
            raise ImportError(
                "bencode module is not installed. Please run: pip install bencode.py"
            )
    
    def download_torrent_file(self, url: str, timeout: int = 30) -> bytes:
        """
        Download torrent file from URL
        
        Args:
            url: URL of the torrent file
            timeout: Request timeout in seconds (default: 30)
            
        Returns:
            Binary content of the torrent file
            
        Raises:
            IOError: Download failed
        """
        try:
            # Create request with User-Agent header
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Download the file
            with urllib.request.urlopen(req, timeout=timeout) as response:
                torrent_data = response.read()
                
            if not torrent_data:
                raise IOError(f"Downloaded file is empty: {url}")
                
            return torrent_data
            
        except urllib.error.URLError as e:
            raise IOError(f"Unable to download from URL {url}: {e}")
        except Exception as e:
            raise IOError(f"Error downloading torrent file from {url}: {e}")
    
    def read_torrent_file(self, torrent_path: Path) -> bytes:
        """
        Read torrent file content
        
        Args:
            torrent_path: Path to the torrent file
            
        Returns:
            Binary content of the torrent file
            
        Raises:
            IOError: File read failed
        """
        try:
            with open(torrent_path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Unable to read file {torrent_path}: {e}")
    
    def parse_torrent(self, torrent_data: bytes) -> Dict:
        """
        Parse torrent file data
        
        Args:
            torrent_data: Binary data of the torrent file
            
        Returns:
            Parsed torrent dictionary data
            
        Raises:
            ValueError: Torrent file format error
        """
        try:
            return bencode.bdecode(torrent_data)
        except Exception as e:
            raise ValueError(f"Unable to parse torrent file: {e}")
    
    def get_info_hash(self, torrent_data: Dict) -> str:
        """
        Extract info hash from torrent data
        
        Args:
            torrent_data: Parsed torrent data dictionary
            
        Returns:
            Info hash as hexadecimal string (uppercase)
            
        Raises:
            ValueError: Torrent data missing info field
        """
        if 'info' not in torrent_data:
            raise ValueError("Torrent file is missing info field")
        
        # Re-encode info section
        info_encoded = bencode.bencode(torrent_data['info'])
        # Calculate SHA1 hash
        info_hash = hashlib.sha1(info_encoded).digest()
        # Convert to hexadecimal string (uppercase)
        return info_hash.hex().upper()
    
    def get_torrent_name(self, torrent_data: Dict) -> Optional[str]:
        """
        Extract file name from torrent data
        
        Args:
            torrent_data: Parsed torrent data dictionary
            
        Returns:
            File name, or None if not present
        """
        # Priority: get from info.name
        if 'info' in torrent_data and 'name' in torrent_data['info']:
            name = torrent_data['info']['name']
            if isinstance(name, bytes):
                return name.decode('utf-8', errors='ignore')
            return str(name)
        
        # Fallback: get from root level name
        if 'name' in torrent_data:
            name = torrent_data['name']
            if isinstance(name, bytes):
                return name.decode('utf-8', errors='ignore')
            return str(name)
        
        return None
    
    def generate_magnet_link(
        self, 
        info_hash: str, 
        name: Optional[str] = None,
        trackers: Optional[list] = None
    ) -> str:
        """
        Generate magnet link
        
        Args:
            info_hash: Info hash string
            name: File name (optional)
            trackers: Tracker list (optional)
            
        Returns:
            Complete magnet link
        """
        magnet = f"magnet:?xt=urn:btih:{info_hash}"
        
        # Add file name
        if name:
            encoded_name = urllib.parse.quote(name, safe='')
            magnet += f"&dn={encoded_name}"
        
        # Add trackers
        if trackers:
            for tracker in trackers:
                if isinstance(tracker, bytes):
                    tracker = tracker.decode('utf-8', errors='ignore')
                encoded_tracker = urllib.parse.quote(tracker, safe='')
                magnet += f"&tr={encoded_tracker}"
        
        return magnet
    
    def get_trackers(self, torrent_data: Dict) -> list:
        """
        Extract tracker list from torrent data
        
        Args:
            torrent_data: Parsed torrent data dictionary
            
        Returns:
            List of tracker URLs
        """
        trackers = []
        
        # Get from announce
        if 'announce' in torrent_data:
            announce = torrent_data['announce']
            if isinstance(announce, bytes):
                announce = announce.decode('utf-8', errors='ignore')
            trackers.append(announce)
        
        # Get from announce-list
        if 'announce-list' in torrent_data:
            for announce_group in torrent_data['announce-list']:
                if isinstance(announce_group, list):
                    for announce in announce_group:
                        if isinstance(announce, bytes):
                            announce = announce.decode('utf-8', errors='ignore')
                        if announce not in trackers:
                            trackers.append(announce)
                elif isinstance(announce_group, bytes):
                    announce = announce_group.decode('utf-8', errors='ignore')
                    if announce not in trackers:
                        trackers.append(announce)
        
        return trackers
    
    def convert(self, torrent_path: Path, include_trackers: bool = False) -> Tuple[str, str, Dict]:
        """
        Convert a single torrent file to magnet link
        
        Args:
            torrent_path: Path to the torrent file
            include_trackers: Whether to include trackers in the magnet link
            
        Returns:
            Tuple of (magnet_link, info_hash, metadata)
            metadata contains: name, trackers, etc.
            
        Raises:
            IOError: File read failed
            ValueError: Torrent file format error
        """
        torrent_data_bytes = self.read_torrent_file(torrent_path)
        torrent_data = self.parse_torrent(torrent_data_bytes)
        info_hash = self.get_info_hash(torrent_data)
        
        # Get metadata
        name = self.get_torrent_name(torrent_data)
        trackers = self.get_trackers(torrent_data) if include_trackers else None
        
        # Generate magnet link
        magnet_link = self.generate_magnet_link(info_hash, name, trackers)
        
        metadata = {
            'name': name,
            'trackers': trackers if include_trackers else [],
            'info_hash': info_hash,
            'file_size': torrent_path.stat().st_size if torrent_path.exists() else 0
        }
        
        return magnet_link, info_hash, metadata
    
    def convert_from_url(self, url: str, include_trackers: bool = False) -> Tuple[str, str, Dict]:
        """
        Download torrent file from URL and convert to magnet link
        
        Args:
            url: URL of the torrent file
            include_trackers: Whether to include trackers in the magnet link
            
        Returns:
            Tuple of (magnet_link, info_hash, metadata)
            metadata contains: name, trackers, etc.
            
        Raises:
            IOError: Download failed
            ValueError: Torrent file format error
        """
        # Download torrent file
        torrent_data_bytes = self.download_torrent_file(url)
        
        # Parse torrent data
        torrent_data = self.parse_torrent(torrent_data_bytes)
        info_hash = self.get_info_hash(torrent_data)
        
        # Get metadata
        name = self.get_torrent_name(torrent_data)
        trackers = self.get_trackers(torrent_data) if include_trackers else None
        
        # Generate magnet link
        magnet_link = self.generate_magnet_link(info_hash, name, trackers)
        
        metadata = {
            'name': name,
            'trackers': trackers if include_trackers else [],
            'info_hash': info_hash,
            'file_size': len(torrent_data_bytes),
            'source_url': url
        }
        
        return magnet_link, info_hash, metadata
