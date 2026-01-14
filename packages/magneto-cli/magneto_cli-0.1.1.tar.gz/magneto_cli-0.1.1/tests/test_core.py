"""
Unit tests for core conversion module
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magneto.core import TorrentConverter


@pytest.mark.unit
class TestTorrentConverter:
    """Test cases for TorrentConverter class"""
    
    def test_init_success(self):
        """Test successful initialization"""
        converter = TorrentConverter()
        assert converter is not None
    
    def test_init_missing_bencode(self, monkeypatch):
        """Test initialization when bencode is not available"""
        monkeypatch.setattr('magneto.core.bencode', None)
        with pytest.raises(ImportError, match="bencode module is not installed"):
            TorrentConverter()
    
    def test_read_torrent_file(self, mock_torrent_file):
        """Test reading torrent file"""
        converter = TorrentConverter()
        data = converter.read_torrent_file(mock_torrent_file)
        assert isinstance(data, bytes)
        assert len(data) > 0
    
    def test_read_torrent_file_not_found(self):
        """Test reading non-existent torrent file"""
        converter = TorrentConverter()
        fake_path = Path("/nonexistent/path/file.torrent")
        with pytest.raises(IOError, match="Unable to read file"):
            converter.read_torrent_file(fake_path)
    
    def test_parse_torrent(self, mock_torrent_bytes, mock_torrent_data):
        """Test parsing torrent data"""
        converter = TorrentConverter()
        parsed = converter.parse_torrent(mock_torrent_bytes)
        assert isinstance(parsed, dict)
        # bencode.py converts byte keys to string keys
        assert 'info' in parsed or b'info' in parsed
        # Check that info dict exists
        info_key = 'info' if 'info' in parsed else b'info'
        assert info_key in parsed
    
    def test_parse_torrent_invalid(self):
        """Test parsing invalid torrent data"""
        converter = TorrentConverter()
        invalid_data = b'This is not valid bencode'
        with pytest.raises(ValueError, match="Unable to parse torrent file"):
            converter.parse_torrent(invalid_data)
    
    def test_get_info_hash(self, mock_torrent_bytes, expected_info_hash):
        """Test extracting info hash"""
        converter = TorrentConverter()
        # Parse the torrent to get the actual decoded structure
        torrent_data = converter.parse_torrent(mock_torrent_bytes)
        info_hash = converter.get_info_hash(torrent_data)
        assert isinstance(info_hash, str)
        assert len(info_hash) == 40  # SHA1 hex is 40 characters
        assert info_hash.isupper()
        assert info_hash == expected_info_hash
    
    def test_get_info_hash_missing_info(self):
        """Test extracting info hash when info field is missing"""
        converter = TorrentConverter()
        # Use string keys as bencode.py converts them
        torrent_data = {'announce': 'http://tracker.example.com'}
        with pytest.raises(ValueError, match="Torrent file is missing info field"):
            converter.get_info_hash(torrent_data)
    
    def test_get_torrent_name_from_info(self, mock_torrent_bytes):
        """Test extracting name from info.name"""
        converter = TorrentConverter()
        # Parse to get actual decoded structure
        torrent_data = converter.parse_torrent(mock_torrent_bytes)
        name = converter.get_torrent_name(torrent_data)
        assert name == "Test Torrent File"
    
    def test_get_torrent_name_from_root(self):
        """Test extracting name from root level"""
        converter = TorrentConverter()
        # Use string keys as bencode.py converts them
        torrent_data = {
            'name': b'Root Name',
            'info': {'piece length': 262144}
        }
        name = converter.get_torrent_name(torrent_data)
        assert name == "Root Name"
    
    def test_get_torrent_name_not_found(self):
        """Test when name is not present"""
        converter = TorrentConverter()
        # Use string keys as bencode.py converts them
        torrent_data = {'info': {'piece length': 262144}}
        name = converter.get_torrent_name(torrent_data)
        assert name is None
    
    def test_get_torrent_name_bytes_decoding(self):
        """Test name decoding from bytes"""
        converter = TorrentConverter()
        # Use string keys as bencode.py converts them
        torrent_data = {
            'info': {
                'name': b'Test\xc3\xa9 File',  # UTF-8 encoded
                'piece length': 262144
            }
        }
        name = converter.get_torrent_name(torrent_data)
        assert isinstance(name, str)
        assert 'Test' in name
    
    def test_generate_magnet_link_basic(self):
        """Test generating basic magnet link"""
        converter = TorrentConverter()
        info_hash = "A" * 40
        magnet = converter.generate_magnet_link(info_hash)
        assert magnet.startswith("magnet:?xt=urn:btih:")
        assert info_hash in magnet
    
    def test_generate_magnet_link_with_name(self):
        """Test generating magnet link with name"""
        converter = TorrentConverter()
        info_hash = "A" * 40
        name = "Test File"
        magnet = converter.generate_magnet_link(info_hash, name)
        assert "&dn=" in magnet
        assert "Test%20File" in magnet or "Test+File" in magnet
    
    def test_generate_magnet_link_with_trackers(self):
        """Test generating magnet link with trackers"""
        converter = TorrentConverter()
        info_hash = "A" * 40
        trackers = ["http://tracker1.example.com", "http://tracker2.example.com"]
        magnet = converter.generate_magnet_link(info_hash, trackers=trackers)
        assert "&tr=" in magnet
        assert "tracker1" in magnet
        assert "tracker2" in magnet
    
    def test_generate_magnet_link_with_all(self):
        """Test generating magnet link with all parameters"""
        converter = TorrentConverter()
        info_hash = "A" * 40
        name = "Complete Test"
        trackers = ["http://tracker.example.com"]
        magnet = converter.generate_magnet_link(info_hash, name, trackers)
        assert "magnet:?xt=urn:btih:" in magnet
        assert "&dn=" in magnet
        assert "&tr=" in magnet
    
    def test_get_trackers_from_announce(self):
        """Test extracting trackers from announce field"""
        converter = TorrentConverter()
        # Use string keys as bencode.py converts them
        torrent_data = {
            'announce': b'http://tracker.example.com/announce'
        }
        trackers = converter.get_trackers(torrent_data)
        assert len(trackers) == 1
        assert "tracker.example.com" in trackers[0]
    
    def test_get_trackers_from_announce_list(self, mock_torrent_bytes):
        """Test extracting trackers from announce-list"""
        converter = TorrentConverter()
        # Parse to get actual decoded structure
        torrent_data = converter.parse_torrent(mock_torrent_bytes)
        trackers = converter.get_trackers(torrent_data)
        assert len(trackers) >= 1
        assert any("tracker1" in t or "tracker2" in t or "tracker.example.com" in t for t in trackers)
    
    def test_get_trackers_no_trackers(self):
        """Test when no trackers are present"""
        converter = TorrentConverter()
        torrent_data = {b'info': {b'piece length': 262144}}
        trackers = converter.get_trackers(torrent_data)
        assert trackers == []
    
    def test_convert_full(self, mock_torrent_file, expected_info_hash):
        """Test full conversion process"""
        converter = TorrentConverter()
        magnet_link, info_hash, metadata = converter.convert(mock_torrent_file)
        
        assert isinstance(magnet_link, str)
        assert magnet_link.startswith("magnet:")
        assert info_hash == expected_info_hash
        assert isinstance(metadata, dict)
        assert 'name' in metadata
        assert 'trackers' in metadata
        assert 'info_hash' in metadata
    
    def test_convert_with_trackers(self, mock_torrent_file):
        """Test conversion with trackers included"""
        converter = TorrentConverter()
        magnet_link, info_hash, metadata = converter.convert(
            mock_torrent_file, 
            include_trackers=True
        )
        
        assert "&tr=" in magnet_link
        assert len(metadata['trackers']) > 0
    
    def test_convert_without_trackers(self, mock_torrent_file):
        """Test conversion without trackers"""
        converter = TorrentConverter()
        magnet_link, info_hash, metadata = converter.convert(
            mock_torrent_file,
            include_trackers=False
        )
        
        # Trackers might still be in metadata but not in magnet link
        assert isinstance(metadata['trackers'], list)
    
    def test_convert_invalid_file(self, mock_torrent_file_invalid):
        """Test conversion of invalid torrent file"""
        converter = TorrentConverter()
        with pytest.raises(ValueError, match="Unable to parse torrent file"):
            converter.convert(mock_torrent_file_invalid)
    
    def test_convert_missing_info(self, mock_torrent_file_missing_info):
        """Test conversion of torrent file missing info field"""
        converter = TorrentConverter()
        with pytest.raises(ValueError, match="Torrent file is missing info field"):
            converter.convert(mock_torrent_file_missing_info)


@pytest.mark.unit
class TestTorrentConverterDownload:
    """Test cases for TorrentConverter download and URL conversion methods"""
    
    def test_download_torrent_file_success(self, mock_torrent_bytes):
        """Test successful torrent file download"""
        converter = TorrentConverter()
        test_url = "http://example.com/file.torrent"
        
        # Mock urlopen to return torrent bytes
        mock_response = MagicMock()
        mock_response.read.return_value = mock_torrent_bytes
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        
        with patch('magneto.core.urllib.request.urlopen', return_value=mock_response):
            data = converter.download_torrent_file(test_url)
        
        assert isinstance(data, bytes)
        assert len(data) > 0
        assert data == mock_torrent_bytes
    
    def test_download_torrent_file_empty_response(self):
        """Test download with empty response"""
        converter = TorrentConverter()
        test_url = "http://example.com/empty.torrent"
        
        mock_response = MagicMock()
        mock_response.read.return_value = b''
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        
        with patch('magneto.core.urllib.request.urlopen', return_value=mock_response):
            with pytest.raises(IOError, match="Downloaded file is empty"):
                converter.download_torrent_file(test_url)
    
    def test_download_torrent_file_url_error(self):
        """Test download with URL error"""
        converter = TorrentConverter()
        test_url = "http://example.com/file.torrent"
        
        from urllib.error import URLError
        with patch('magneto.core.urllib.request.urlopen', side_effect=URLError("Connection failed")):
            with pytest.raises(IOError, match="Unable to download from URL"):
                converter.download_torrent_file(test_url)
    
    def test_download_torrent_file_timeout(self):
        """Test download with timeout"""
        converter = TorrentConverter()
        test_url = "http://example.com/file.torrent"
        
        import socket
        with patch('magneto.core.urllib.request.urlopen', side_effect=socket.timeout("Timeout")):
            with pytest.raises(IOError, match="Error downloading torrent file"):
                converter.download_torrent_file(test_url, timeout=1)
    
    def test_download_torrent_file_user_agent(self, mock_torrent_bytes):
        """Test that User-Agent header is set"""
        converter = TorrentConverter()
        test_url = "http://example.com/file.torrent"
        
        mock_response = MagicMock()
        mock_response.read.return_value = mock_torrent_bytes
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        
        with patch('magneto.core.urllib.request.urlopen', return_value=mock_response) as mock_urlopen:
            with patch('magneto.core.urllib.request.Request') as mock_request:
                mock_req_instance = MagicMock()
                mock_request.return_value = mock_req_instance
                
                converter.download_torrent_file(test_url)
                
                # Verify Request was created with URL
                mock_request.assert_called_once_with(test_url)
                # Verify User-Agent header was added
                mock_req_instance.add_header.assert_called_once()
                call_args = mock_req_instance.add_header.call_args[0]
                assert call_args[0] == 'User-Agent'
    
    def test_convert_from_url_success(self, mock_torrent_bytes, expected_info_hash):
        """Test successful conversion from URL"""
        converter = TorrentConverter()
        test_url = "http://example.com/file.torrent"
        
        mock_response = MagicMock()
        mock_response.read.return_value = mock_torrent_bytes
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        
        with patch('magneto.core.urllib.request.urlopen', return_value=mock_response):
            magnet_link, info_hash, metadata = converter.convert_from_url(test_url)
        
        assert isinstance(magnet_link, str)
        assert magnet_link.startswith("magnet:")
        assert info_hash == expected_info_hash
        assert isinstance(metadata, dict)
        assert 'name' in metadata
        assert 'source_url' in metadata
        assert metadata['source_url'] == test_url
        assert 'file_size' in metadata
        assert metadata['file_size'] == len(mock_torrent_bytes)
    
    def test_convert_from_url_with_trackers(self, mock_torrent_bytes):
        """Test conversion from URL with trackers"""
        converter = TorrentConverter()
        test_url = "http://example.com/file.torrent"
        
        mock_response = MagicMock()
        mock_response.read.return_value = mock_torrent_bytes
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        
        with patch('magneto.core.urllib.request.urlopen', return_value=mock_response):
            magnet_link, info_hash, metadata = converter.convert_from_url(
                test_url,
                include_trackers=True
            )
        
        assert "&tr=" in magnet_link
        assert len(metadata['trackers']) > 0
    
    def test_convert_from_url_without_trackers(self, mock_torrent_bytes):
        """Test conversion from URL without trackers"""
        converter = TorrentConverter()
        test_url = "http://example.com/file.torrent"
        
        mock_response = MagicMock()
        mock_response.read.return_value = mock_torrent_bytes
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        
        with patch('magneto.core.urllib.request.urlopen', return_value=mock_response):
            magnet_link, info_hash, metadata = converter.convert_from_url(
                test_url,
                include_trackers=False
            )
        
        assert isinstance(metadata['trackers'], list)
    
    def test_convert_from_url_download_error(self):
        """Test conversion from URL when download fails"""
        converter = TorrentConverter()
        test_url = "http://example.com/file.torrent"
        
        from urllib.error import URLError
        with patch('magneto.core.urllib.request.urlopen', side_effect=URLError("Connection failed")):
            with pytest.raises(IOError, match="Unable to download from URL"):
                converter.convert_from_url(test_url)
    
    def test_convert_from_url_invalid_torrent(self):
        """Test conversion from URL with invalid torrent data"""
        converter = TorrentConverter()
        test_url = "http://example.com/invalid.torrent"
        
        mock_response = MagicMock()
        mock_response.read.return_value = b'Invalid torrent data'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        
        with patch('magneto.core.urllib.request.urlopen', return_value=mock_response):
            with pytest.raises(ValueError, match="Unable to parse torrent file"):
                converter.convert_from_url(test_url)

