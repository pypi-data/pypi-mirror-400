"""
User interface module - Handles output and user interaction
"""
import sys
from pathlib import Path
from typing import List, Tuple

try:
    # Try to import colorama for Windows color output support
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    # Create empty color classes
    class Fore:
        GREEN = ""
        RED = ""
        YELLOW = ""
        BLUE = ""
        CYAN = ""
        MAGENTA = ""
        RESET = ""
    
    class Style:
        BRIGHT = ""
        RESET_ALL = ""


class UI:
    """User interface handler"""
    
    def __init__(self, verbose: bool = False, quiet: bool = False, use_colors: bool = True):
        """
        Initialize UI
        
        Args:
            verbose: Whether to show detailed information
            quiet: Whether to use quiet mode (only show errors)
            use_colors: Whether to use colored output
        """
        self.verbose = verbose
        self.quiet = quiet
        self.use_colors = use_colors and HAS_COLORAMA
        self.success_count = 0
        self.error_count = 0
    
    def _colorize(self, text: str, color: str) -> str:
        """Add color to text (if supported)"""
        if self.use_colors:
            return f"{color}{text}{Style.RESET_ALL}"
        return text
    
    def print_success(self, message: str):
        """Print success message"""
        if not self.quiet:
            print(self._colorize(f"✓ {message}", Fore.GREEN))
        self.success_count += 1
    
    def print_error(self, message: str):
        """Print error message"""
        print(self._colorize(f"✗ {message}", Fore.RED), file=sys.stderr)
        self.error_count += 1
    
    def print_warning(self, message: str):
        """Print warning message"""
        if not self.quiet:
            print(self._colorize(f"⚠ {message}", Fore.YELLOW))
    
    def print_info(self, message: str):
        """Print info message"""
        if not self.quiet:
            print(self._colorize(f"ℹ {message}", Fore.CYAN))
    
    def print_verbose(self, message: str):
        """Print verbose message"""
        if self.verbose and not self.quiet:
            print(self._colorize(f"  {message}", Fore.BLUE))
    
    def print_header(self, message: str):
        """Print header"""
        if not self.quiet:
            print(self._colorize(f"\n{message}", Style.BRIGHT + Fore.MAGENTA))
    
    def print_separator(self):
        """Print separator line"""
        if not self.quiet:
            print("-" * 80)
    
    def print_progress(self, current: int, total: int, filename: str):
        """Print progress information"""
        if not self.quiet:
            percentage = (current / total * 100) if total > 0 else 0
            print(f"[{current}/{total}] ({percentage:.1f}%) {filename}")
    
    def print_summary(self):
        """Print processing summary"""
        if not self.quiet:
            total = self.success_count + self.error_count
            print("\n" + "=" * 80)
            print(f"Processing complete: {total} file(s) total")
            print(self._colorize(f"Success: {self.success_count}", Fore.GREEN))
            if self.error_count > 0:
                print(self._colorize(f"Failed: {self.error_count}", Fore.RED))
            print("=" * 80)
    
    def save_results(
        self,
        results: List[Tuple[str, str, str, dict]],
        output_file: Path,
        format_type: str = "full"
    ):
        """
        Save results to file
        
        Args:
            results: Results list, each element is (file_path, magnet_link, info_hash, metadata)
            output_file: Output file path
            format_type: Output format type ("full", "links_only", "json")
        """
        try:
            if format_type == "json":
                import json
                output_data = []
                for torrent_path, magnet_link, info_hash, metadata in results:
                    if not magnet_link.startswith("Error"):
                        output_data.append({
                            "file": str(torrent_path),
                            "magnet": magnet_link,
                            "info_hash": info_hash,
                            "name": metadata.get('name', ''),
                            "trackers": metadata.get('trackers', [])
                        })
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            elif format_type == "links_only":
                # Save magnet links only
                with open(output_file, 'w', encoding='utf-8') as f:
                    for torrent_path, magnet_link, info_hash, metadata in results:
                        if not magnet_link.startswith("Error"):
                            f.write(f"{magnet_link}\n")
            
            else:  # full format
                # Full format
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write("Torrent to Magnet Link Conversion Results\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for torrent_path, magnet_link, info_hash, metadata in results:
                        f.write(f"File: {torrent_path}\n")
                        f.write(f"Magnet Link: {magnet_link}\n")
                        if info_hash:
                            f.write(f"Info Hash: {info_hash}\n")
                        if metadata.get('name'):
                            f.write(f"Name: {metadata['name']}\n")
                        if metadata.get('trackers'):
                            f.write(f"Trackers: {len(metadata['trackers'])} found\n")
                        f.write("-" * 80 + "\n\n")
                    
                    # Magnet link list
                    f.write("\n" + "=" * 80 + "\n")
                    f.write("Magnet Link List (Links Only)\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for torrent_path, magnet_link, info_hash, metadata in results:
                        if not magnet_link.startswith("Error"):
                            f.write(f"{magnet_link}\n")
            
            if not self.quiet:
                print(self._colorize(f"\nResults saved to: {output_file}", Fore.GREEN))
        
        except Exception as e:
            self.print_error(f"Error saving file: {e}")
    
    def print_results(
        self,
        results: List[Tuple[str, str, str, dict]],
        format_type: str = "full"
    ):
        """
        Print results to stdout
        
        Args:
            results: Results list, each element is (file_path, magnet_link, info_hash, metadata)
            format_type: Output format type ("full", "links_only", "json")
        """
        try:
            if format_type == "json":
                import json
                output_data = []
                for torrent_path, magnet_link, info_hash, metadata in results:
                    if not magnet_link.startswith("Error"):
                        output_data.append({
                            "file": str(torrent_path),
                            "magnet": magnet_link,
                            "info_hash": info_hash,
                            "name": metadata.get('name', ''),
                            "trackers": metadata.get('trackers', [])
                        })
                
                print(json.dumps(output_data, ensure_ascii=False, indent=2))
            
            elif format_type == "links_only":
                # Print magnet links only
                for torrent_path, magnet_link, info_hash, metadata in results:
                    if not magnet_link.startswith("Error"):
                        print(magnet_link)
            
            else:  # full format
                # Full format
                print("=" * 80)
                print("Torrent to Magnet Link Conversion Results")
                print("=" * 80)
                print()
                
                for torrent_path, magnet_link, info_hash, metadata in results:
                    print(f"File: {torrent_path}")
                    print(f"Magnet Link: {magnet_link}")
                    if info_hash:
                        print(f"Info Hash: {info_hash}")
                    if metadata.get('name'):
                        print(f"Name: {metadata['name']}")
                    if metadata.get('trackers'):
                        print(f"Trackers: {len(metadata['trackers'])} found")
                    print("-" * 80)
                    print()
                
                # Magnet link list
                print("=" * 80)
                print("Magnet Link List (Links Only)")
                print("=" * 80)
                print()
                
                for torrent_path, magnet_link, info_hash, metadata in results:
                    if not magnet_link.startswith("Error"):
                        print(magnet_link)
        
        except Exception as e:
            self.print_error(f"Error printing results: {e}")
