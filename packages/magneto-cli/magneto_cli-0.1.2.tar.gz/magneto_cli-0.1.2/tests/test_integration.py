"""
Integration tests for the complete workflow
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magneto.core import TorrentConverter   
from magneto.parser import ArgumentParser   
from magneto.ui import UI   
from magneto.utils import collect_torrent_files, is_url


@pytest.mark.integration
class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_full_workflow_single_file(self, mock_torrent_file):
        """Test complete workflow with a single file"""
        # Parse arguments
        args = ArgumentParser.parse_args([str(mock_torrent_file)])
        
        # Initialize components
        converter = TorrentConverter()
        _ =UI(verbose=args.verbose, quiet=args.quiet)
        
        # Collect files
        torrent_files = collect_torrent_files(Path(args.input))
        assert len(torrent_files) == 1
        
        # Convert
        results = []
        for torrent_file in torrent_files:
            magnet_link, info_hash, metadata = converter.convert(
                torrent_file,
                include_trackers=args.include_trackers
            )
            results.append((str(torrent_file), magnet_link, info_hash, metadata))
        
        # Verify results
        assert len(results) == 1
        assert results[0][1].startswith("magnet:")
        assert len(results[0][2]) == 40  # Info hash length
    
    def test_full_workflow_multiple_files(self, sample_torrent_dir):
        """Test complete workflow with multiple files"""
        # Parse arguments
        args = ArgumentParser.parse_args([str(sample_torrent_dir)])
        
        # Initialize components
        converter = TorrentConverter()
        _ = UI(verbose=args.verbose, quiet=args.quiet)
        
        # Collect files
        torrent_files = collect_torrent_files(Path(args.input))
        assert len(torrent_files) == 3
        
        # Convert all files
        results = []
        for torrent_file in torrent_files:
            magnet_link, info_hash, metadata = converter.convert(torrent_file)
            results.append((str(torrent_file), magnet_link, info_hash, metadata))
        
        # Verify results
        assert len(results) == 3
        assert all(r[1].startswith("magnet:") for r in results)
    
    def test_workflow_with_trackers(self, mock_torrent_file):
        """Test workflow with trackers included"""
        converter = TorrentConverter()
        magnet_link, info_hash, metadata = converter.convert(
            mock_torrent_file,
            include_trackers=True
        )
        
        assert "&tr=" in magnet_link
        assert len(metadata['trackers']) > 0
    
    def test_workflow_stdout_output(self, mock_torrent_file, capsys):
        """Test workflow with stdout output"""
        args = ArgumentParser.parse_args([
            str(mock_torrent_file),
            '--stdout',
            '--format', 'links_only'
        ])
        
        converter = TorrentConverter()
        ui = UI(quiet=True)  # Quiet to avoid extra output
        
        magnet_link, info_hash, metadata = converter.convert(mock_torrent_file)
        results = [(str(mock_torrent_file), magnet_link, info_hash, metadata)]
        
        ui.print_results(results, args.format)
        captured = capsys.readouterr()
        assert magnet_link in captured.out
    
    def test_workflow_json_output(self, mock_torrent_file, tmp_path):
        """Test workflow with JSON output format"""
        args = ArgumentParser.parse_args([
            str(mock_torrent_file),
            '--format', 'json',
            '--output', str(tmp_path / "output.json")
        ])
        
        converter = TorrentConverter()
        ui = UI(quiet=True)
        
        magnet_link, info_hash, metadata = converter.convert(mock_torrent_file)
        results = [(str(mock_torrent_file), magnet_link, info_hash, metadata)]
        
        output_file = Path(args.output)
        ui.save_results(results, output_file, args.format)
        
        assert output_file.exists()
        import json
        data = json.loads(output_file.read_text())
        assert isinstance(data, list)
        assert data[0]["magnet"] == magnet_link
    
    def test_workflow_url_input(self, mock_torrent_bytes, expected_info_hash):
        """Test complete workflow with URL input"""
        test_url = "http://example.com/file.torrent"
        
        # Mock urlopen to return torrent bytes
        mock_response = MagicMock()
        mock_response.read.return_value = mock_torrent_bytes
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        
        with patch('magneto.core.urllib.request.urlopen', return_value=mock_response):
            # Parse arguments with URL
            args = ArgumentParser.parse_args([test_url])
            
            # Verify URL is detected
            assert is_url(args.input)
            
            # Initialize components
            converter = TorrentConverter()
            ui = UI(verbose=args.verbose, quiet=args.quiet)
            
            # Convert from URL
            magnet_link, info_hash, metadata = converter.convert_from_url(
                test_url,
                include_trackers=args.include_trackers
            )
            
            results = [(test_url, magnet_link, info_hash, metadata)]
            
            # Verify results
            assert len(results) == 1
            assert results[0][1].startswith("magnet:")
            assert results[0][2] == expected_info_hash
            assert results[0][3]['source_url'] == test_url
    
    def test_workflow_url_input_with_trackers(self, mock_torrent_bytes):
        """Test URL input workflow with trackers"""
        test_url = "http://example.com/file.torrent"
        
        mock_response = MagicMock()
        mock_response.read.return_value = mock_torrent_bytes
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        
        with patch('magneto.core.urllib.request.urlopen', return_value=mock_response):
            args = ArgumentParser.parse_args([test_url, '--include-trackers'])
            
            converter = TorrentConverter()
            magnet_link, info_hash, metadata = converter.convert_from_url(
                test_url,
                include_trackers=True
            )
            
            assert "&tr=" in magnet_link
            assert len(metadata['trackers']) > 0
    
    def test_workflow_url_input_stdout(self, mock_torrent_bytes, capsys):
        """Test URL input workflow with stdout output"""
        test_url = "http://example.com/file.torrent"
        
        mock_response = MagicMock()
        mock_response.read.return_value = mock_torrent_bytes
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)
        
        with patch('magneto.core.urllib.request.urlopen', return_value=mock_response):
            args = ArgumentParser.parse_args([
                test_url,
                '--stdout',
                '--format', 'links_only'
            ])
            
            converter = TorrentConverter()
            ui = UI(quiet=True)
            
            magnet_link, info_hash, metadata = converter.convert_from_url(test_url)
            results = [(test_url, magnet_link, info_hash, metadata)]
            
            ui.print_results(results, args.format)
            captured = capsys.readouterr()
            assert magnet_link in captured.out
    
    def test_workflow_url_input_parser_validation(self):
        """Test that parser correctly validates URL input"""
        test_url = "http://example.com/file.torrent"
        
        # Should not raise error for valid URL
        args = ArgumentParser.parse_args([test_url])
        assert args.input == test_url
        
        # Should raise error for invalid path
        with pytest.raises(SystemExit):
            ArgumentParser.parse_args(["/nonexistent/path/file.torrent"])

