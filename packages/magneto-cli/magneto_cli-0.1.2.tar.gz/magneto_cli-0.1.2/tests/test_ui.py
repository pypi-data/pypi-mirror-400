"""
Unit tests for UI module
"""

import json

import pytest

from magneto.ui import UI


@pytest.mark.unit
class TestUI:
    """Test cases for UI class"""

    def test_init_default(self):
        """Test UI initialization with default parameters"""
        ui = UI()
        assert ui.verbose is False
        assert ui.quiet is False
        assert ui.success_count == 0
        assert ui.error_count == 0

    def test_init_verbose(self):
        """Test UI initialization with verbose mode"""
        ui = UI(verbose=True)
        assert ui.verbose is True

    def test_init_quiet(self):
        """Test UI initialization with quiet mode"""
        ui = UI(quiet=True)
        assert ui.quiet is True

    def test_init_no_colors(self):
        """Test UI initialization without colors"""
        ui = UI(use_colors=False)
        assert ui.use_colors is False

    def test_print_success(self, capsys):
        """Test printing success message"""
        ui = UI()
        ui.print_success("Test success")
        captured = capsys.readouterr()
        assert "Test success" in captured.out
        assert ui.success_count == 1

    def test_print_success_quiet(self, capsys):
        """Test printing success message in quiet mode"""
        ui = UI(quiet=True)
        ui.print_success("Test success")
        captured = capsys.readouterr()
        assert "Test success" not in captured.out
        assert ui.success_count == 1

    def test_print_error(self, capsys):
        """Test printing error message"""
        ui = UI()
        ui.print_error("Test error")
        captured = capsys.readouterr()
        assert "Test error" in captured.err
        assert ui.error_count == 1

    def test_print_warning(self, capsys):
        """Test printing warning message"""
        ui = UI()
        ui.print_warning("Test warning")
        captured = capsys.readouterr()
        assert "Test warning" in captured.out

    def test_print_warning_quiet(self, capsys):
        """Test printing warning message in quiet mode"""
        ui = UI(quiet=True)
        ui.print_warning("Test warning")
        captured = capsys.readouterr()
        assert "Test warning" not in captured.out

    def test_print_info(self, capsys):
        """Test printing info message"""
        ui = UI()
        ui.print_info("Test info")
        captured = capsys.readouterr()
        assert "Test info" in captured.out

    def test_print_verbose(self, capsys):
        """Test printing verbose message"""
        ui = UI(verbose=True)
        ui.print_verbose("Test verbose")
        captured = capsys.readouterr()
        assert "Test verbose" in captured.out

    def test_print_verbose_not_verbose(self, capsys):
        """Test printing verbose message when not in verbose mode"""
        ui = UI(verbose=False)
        ui.print_verbose("Test verbose")
        captured = capsys.readouterr()
        assert "Test verbose" not in captured.out

    def test_print_header(self, capsys):
        """Test printing header"""
        ui = UI()
        ui.print_header("Test Header")
        captured = capsys.readouterr()
        assert "Test Header" in captured.out

    def test_print_progress(self, capsys):
        """Test printing progress"""
        ui = UI()
        ui.print_progress(1, 10, "test.torrent")
        captured = capsys.readouterr()
        assert "test.torrent" in captured.out
        assert "1/10" in captured.out

    def test_print_summary(self, capsys):
        """Test printing summary"""
        ui = UI()
        ui.print_success("File 1")
        ui.print_success("File 2")
        ui.print_error("File 3")
        ui.print_summary()
        captured = capsys.readouterr()
        assert "Processing complete" in captured.out
        assert "2" in captured.out  # success count
        assert "1" in captured.out  # error count

    def test_save_results_full_format(self, tmp_path):
        """Test saving results in full format"""
        ui = UI()
        results = [
            ("file1.torrent", "magnet:?xt=urn:btih:ABC123", "ABC123", {"name": "Test"}),
            ("file2.torrent", "magnet:?xt=urn:btih:DEF456", "DEF456", {}),
        ]
        output_file = tmp_path / "output.txt"
        ui.save_results(results, output_file, "full")

        assert output_file.exists()
        content = output_file.read_text()
        assert "Torrent to Magnet Link Conversion Results" in content
        assert "file1.torrent" in content
        assert "magnet:?xt=urn:btih:ABC123" in content

    def test_save_results_links_only_format(self, tmp_path):
        """Test saving results in links_only format"""
        ui = UI()
        results = [
            ("file1.torrent", "magnet:?xt=urn:btih:ABC123", "ABC123", {}),
            ("file2.torrent", "magnet:?xt=urn:btih:DEF456", "DEF456", {}),
        ]
        output_file = tmp_path / "output.txt"
        ui.save_results(results, output_file, "links_only")

        assert output_file.exists()
        content = output_file.read_text()
        assert "magnet:?xt=urn:btih:ABC123" in content
        assert "magnet:?xt=urn:btih:DEF456" in content
        assert "file1.torrent" not in content

    def test_save_results_json_format(self, tmp_path):
        """Test saving results in JSON format"""
        ui = UI()
        results = [
            ("file1.torrent", "magnet:?xt=urn:btih:ABC123", "ABC123", {"name": "Test"}),
        ]
        output_file = tmp_path / "output.json"
        ui.save_results(results, output_file, "json")

        assert output_file.exists()
        content = json.loads(output_file.read_text())
        assert isinstance(content, list)
        assert len(content) == 1
        assert content[0]["magnet"] == "magnet:?xt=urn:btih:ABC123"

    def test_save_results_with_errors(self, tmp_path):
        """Test saving results that include errors"""
        ui = UI()
        results = [
            ("file1.torrent", "magnet:?xt=urn:btih:ABC123", "ABC123", {}),
            ("file2.torrent", "Error: Invalid file", "", {}),
        ]
        output_file = tmp_path / "output.txt"
        ui.save_results(results, output_file, "links_only")

        content = output_file.read_text()
        assert "magnet:?xt=urn:btih:ABC123" in content
        assert "Error: Invalid file" not in content  # Errors should be filtered

    def test_print_results_full_format(self, capsys):
        """Test printing results in full format"""
        ui = UI()
        results = [
            ("file1.torrent", "magnet:?xt=urn:btih:ABC123", "ABC123", {"name": "Test"}),
        ]
        ui.print_results(results, "full")
        captured = capsys.readouterr()
        assert "Torrent to Magnet Link Conversion Results" in captured.out
        assert "magnet:?xt=urn:btih:ABC123" in captured.out

    def test_print_results_links_only_format(self, capsys):
        """Test printing results in links_only format"""
        ui = UI()
        results = [
            ("file1.torrent", "magnet:?xt=urn:btih:ABC123", "ABC123", {}),
            ("file2.torrent", "magnet:?xt=urn:btih:DEF456", "DEF456", {}),
        ]
        ui.print_results(results, "links_only")
        captured = capsys.readouterr()
        assert "magnet:?xt=urn:btih:ABC123" in captured.out
        assert "magnet:?xt=urn:btih:DEF456" in captured.out
        assert "file1.torrent" not in captured.out

    def test_print_results_json_format(self, capsys):
        """Test printing results in JSON format"""
        ui = UI()
        results = [
            ("file1.torrent", "magnet:?xt=urn:btih:ABC123", "ABC123", {"name": "Test"}),
        ]
        ui.print_results(results, "json")
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert isinstance(output, list)
        assert output[0]["magnet"] == "magnet:?xt=urn:btih:ABC123"
