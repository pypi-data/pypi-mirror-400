"""
Command-line argument parsing module
"""
import argparse
import sys
from pathlib import Path

from . import __version__


class ArgumentParser:
    """Command-line argument parser"""
    
    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """
        Create and configure command-line argument parser
        
        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            prog='magneto',
            description='Batch convert torrent files (.torrent) to magnet links and save to txt file',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s file.torrent                    # Convert a single file
  %(prog)s folder/                         # Convert all .torrent files in folder
  %(prog)s http://example.com/file.torrent # Download and convert from URL
  %(prog)s folder/ -o output.txt           # Specify output file
  %(prog)s folder/ -r -f json              # Recursive search and output JSON format
  %(prog)s folder/ -v --include-trackers   # Verbose output with trackers
  %(prog)s folder/ --stdout                # Print results to stdout
  %(prog)s folder/ --stdout -f links_only  # Print only magnet links to stdout
  %(prog)s --help                          # Show help information

For more information, visit: https://github.com/mastaBriX/magneto
            """,
            add_help=True
        )
        
        # Positional arguments
        parser.add_argument(
            'input',
            type=str,
            nargs='?',
            default=None,
            help='Input torrent file, folder path, or URL of torrent file'
        )
        
        # Output options
        output_group = parser.add_argument_group('Output Options')
        output_group.add_argument(
            '-o', '--output',
            type=str,
            default=None,
            metavar='FILE',
            help='Output file path (default: magnet_links.txt in input directory)'
        )
        output_group.add_argument(
            '-f', '--format',
            type=str,
            choices=['full', 'links_only', 'json'],
            default='full',
            help='Output format: full (complete), links_only (links only), json (JSON format) (default: full)'
        )
        output_group.add_argument(
            '--stdout',
            action='store_true',
            help='Print results to stdout instead of saving to file'
        )
        
        # Search options
        search_group = parser.add_argument_group('Search Options')
        search_group.add_argument(
            '-r', '--recursive',
            action='store_true',
            help='Recursively search for torrent files in subdirectories'
        )
        search_group.add_argument(
            '--case-sensitive',
            action='store_true',
            help='Case-sensitive search for file extensions'
        )
        
        # Conversion options
        convert_group = parser.add_argument_group('Conversion Options')
        convert_group.add_argument(
            '--include-trackers',
            action='store_true',
            help='Include tracker information in magnet links'
        )
        
        # Display options
        display_group = parser.add_argument_group('Display Options')
        display_group.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Show verbose output information'
        )
        display_group.add_argument(
            '-q', '--quiet',
            action='store_true',
            help='Quiet mode, only show error messages'
        )
        display_group.add_argument(
            '--no-colors',
            action='store_true',
            help='Disable colored output'
        )
        
        # Other options
        other_group = parser.add_argument_group('Other Options')
        other_group.add_argument(
            '--version',
            action='version',
            version=f'%(prog)s {__version__}'
        )
        
        return parser
    
    @staticmethod
    def parse_args(args=None):
        """
        Parse command-line arguments
        
        Args:
            args: Argument list to parse, if None uses sys.argv
            
        Returns:
            Parsed argument namespace
        """
        parser = ArgumentParser.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Validate arguments
        if parsed_args.input is None:
            parser.print_help()
            sys.exit(1)
        
        # Check if input is URL - if not, validate path exists
        from magneto.utils import is_url
        if not is_url(parsed_args.input):
            input_path = Path(parsed_args.input)
            if not input_path.exists():
                print(f"Error: Path does not exist: {input_path}", file=sys.stderr)
                sys.exit(1)
        
        return parsed_args
