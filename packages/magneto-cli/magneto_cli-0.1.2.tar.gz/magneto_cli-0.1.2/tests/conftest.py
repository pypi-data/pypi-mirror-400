"""
Pytest configuration and fixtures
"""
import hashlib

import bencode
import pytest


@pytest.fixture
def mock_torrent_data():
    """Create mock torrent data dictionary"""
    info_dict = {
        b'name': b'Test Torrent File',
        b'piece length': 262144,
        b'pieces': b'0' * 20,  # Mock piece hash
        b'length': 1024 * 1024,  # 1MB
    }
    
    torrent_dict = {
        b'announce': b'http://tracker.example.com/announce',
        b'announce-list': [
            [b'http://tracker1.example.com/announce'],
            [b'http://tracker2.example.com/announce'],
        ],
        b'info': info_dict,
    }
    
    return torrent_dict


@pytest.fixture
def mock_torrent_bytes(mock_torrent_data):
    """Create mock torrent file as bytes"""
    return bencode.bencode(mock_torrent_data)


@pytest.fixture
def mock_torrent_file(tmp_path, mock_torrent_bytes):
    """Create a temporary mock torrent file"""
    torrent_file = tmp_path / "test.torrent"
    torrent_file.write_bytes(mock_torrent_bytes)
    return torrent_file


@pytest.fixture
def mock_torrent_file_with_name(tmp_path, mock_torrent_data):
    """Create a mock torrent file with specific name"""
    # Add name at root level
    mock_torrent_data[b'name'] = b'Root Level Name'
    torrent_bytes = bencode.bencode(mock_torrent_data)
    torrent_file = tmp_path / "named.torrent"
    torrent_file.write_bytes(torrent_bytes)
    return torrent_file


@pytest.fixture
def mock_torrent_file_no_trackers(tmp_path):
    """Create a mock torrent file without trackers"""
    info_dict = {
        b'name': b'No Tracker Torrent',
        b'piece length': 262144,
        b'pieces': b'0' * 20,
        b'length': 512 * 1024,
    }
    
    torrent_dict = {
        b'info': info_dict,
    }
    
    torrent_bytes = bencode.bencode(torrent_dict)
    torrent_file = tmp_path / "no_trackers.torrent"
    torrent_file.write_bytes(torrent_bytes)
    return torrent_file


@pytest.fixture
def mock_torrent_file_invalid(tmp_path):
    """Create an invalid torrent file"""
    invalid_file = tmp_path / "invalid.torrent"
    invalid_file.write_bytes(b'This is not a valid torrent file')
    return invalid_file


@pytest.fixture
def mock_torrent_file_missing_info(tmp_path):
    """Create a torrent file missing info field"""
    torrent_dict = {
        b'announce': b'http://tracker.example.com/announce',
        # Missing 'info' field
    }
    
    torrent_bytes = bencode.bencode(torrent_dict)
    torrent_file = tmp_path / "missing_info.torrent"
    torrent_file.write_bytes(torrent_bytes)
    return torrent_file


@pytest.fixture
def expected_info_hash(mock_torrent_data):
    """Calculate expected info hash from mock data"""
    info_encoded = bencode.bencode(mock_torrent_data[b'info'])
    info_hash = hashlib.sha1(info_encoded).digest()
    return info_hash.hex().upper()


@pytest.fixture
def sample_torrent_dir(tmp_path, mock_torrent_bytes):
    """Create a directory with multiple mock torrent files"""
    torrent_dir = tmp_path / "torrents"
    torrent_dir.mkdir()
    
    # Create multiple torrent files
    for i in range(3):
        torrent_file = torrent_dir / f"test_{i}.torrent"
        torrent_file.write_bytes(mock_torrent_bytes)
    
    return torrent_dir

