"""
Unit tests for argument parser module
"""
import pytest
from magneto.parser import ArgumentParser


@pytest.mark.unit
class TestArgumentParser:
    """Test cases for ArgumentParser class"""
    
    def test_create_parser(self):
        """Test parser creation"""
        parser = ArgumentParser.create_parser()
        assert parser is not None
        assert parser.prog == 'magneto'
    
    def test_parse_args_with_input(self, mock_torrent_file):
        """Test parsing arguments with input file"""
        args = ArgumentParser.parse_args([str(mock_torrent_file)])
        assert args.input == str(mock_torrent_file)
        assert args.format == 'full'
        assert args.recursive is False
        assert args.verbose is False
        assert args.quiet is False
    
    def test_parse_args_with_format(self, mock_torrent_file):
        """Test parsing arguments with format option"""
        args = ArgumentParser.parse_args([
            str(mock_torrent_file),
            '--format', 'json'
        ])
        assert args.format == 'json'
    
    def test_parse_args_with_recursive(self, sample_torrent_dir):
        """Test parsing arguments with recursive option"""
        args = ArgumentParser.parse_args([
            str(sample_torrent_dir),
            '--recursive'
        ])
        assert args.recursive is True
    
    def test_parse_args_with_verbose(self, mock_torrent_file):
        """Test parsing arguments with verbose option"""
        args = ArgumentParser.parse_args([
            str(mock_torrent_file),
            '--verbose'
        ])
        assert args.verbose is True
    
    def test_parse_args_with_quiet(self, mock_torrent_file):
        """Test parsing arguments with quiet option"""
        args = ArgumentParser.parse_args([
            str(mock_torrent_file),
            '--quiet'
        ])
        assert args.quiet is True
    
    def test_parse_args_with_include_trackers(self, mock_torrent_file):
        """Test parsing arguments with include-trackers option"""
        args = ArgumentParser.parse_args([
            str(mock_torrent_file),
            '--include-trackers'
        ])
        assert args.include_trackers is True
    
    def test_parse_args_with_stdout(self, mock_torrent_file):
        """Test parsing arguments with stdout option"""
        args = ArgumentParser.parse_args([
            str(mock_torrent_file),
            '--stdout'
        ])
        assert args.stdout is True
    
    def test_parse_args_with_output(self, mock_torrent_file, tmp_path):
        """Test parsing arguments with output option"""
        output_file = tmp_path / "output.txt"
        args = ArgumentParser.parse_args([
            str(mock_torrent_file),
            '--output', str(output_file)
        ])
        assert args.output == str(output_file)
    
    def test_parse_args_no_input(self):
        """Test parsing arguments without input (should exit)"""
        with pytest.raises(SystemExit):
            ArgumentParser.parse_args([])
    
    def test_parse_args_nonexistent_path(self):
        """Test parsing arguments with non-existent path"""
        with pytest.raises(SystemExit):
            ArgumentParser.parse_args(['/nonexistent/path'])
    
    def test_parse_args_invalid_format(self, mock_torrent_file):
        """Test parsing arguments with invalid format"""
        with pytest.raises(SystemExit):
            ArgumentParser.parse_args([
                str(mock_torrent_file),
                '--format', 'invalid'
            ])
    
    def test_parse_args_version(self, capsys):
        """Test version option"""
        with pytest.raises(SystemExit) as exc_info:
            ArgumentParser.parse_args(['--version'])
        assert exc_info.value.code == 0
    
    def test_parse_args_help(self, capsys):
        """Test help option"""
        with pytest.raises(SystemExit) as exc_info:
            ArgumentParser.parse_args(['--help'])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert 'magneto' in captured.out
        assert 'Examples:' in captured.out
    
    def test_parse_args_all_options(self, mock_torrent_file, tmp_path):
        """Test parsing with all options"""
        output_file = tmp_path / "output.json"
        args = ArgumentParser.parse_args([
            str(mock_torrent_file),
            '--output', str(output_file),
            '--format', 'json',
            '--recursive',
            '--verbose',
            '--include-trackers',
            '--stdout'
        ])
        assert args.output == str(output_file)
        assert args.format == 'json'
        assert args.recursive is True
        assert args.verbose is True
        assert args.include_trackers is True
        assert args.stdout is True

