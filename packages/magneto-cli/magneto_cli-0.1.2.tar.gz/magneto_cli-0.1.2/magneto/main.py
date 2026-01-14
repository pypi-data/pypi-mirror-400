#!/usr/bin/env python3
"""
Magneto - Command-line tool for batch converting torrent files to magnet links
Main entry point
"""
import sys
from pathlib import Path

from magneto.core import TorrentConverter
from magneto.parser import ArgumentParser
from magneto.ui import UI
from magneto.utils import collect_torrent_files, get_output_path, is_url


def main():
    """Main function"""
    args = None
    try:
        # Parse command line arguments
        args = ArgumentParser.parse_args()
        
        # Initialize components
        converter = TorrentConverter()
        ui = UI(
            verbose=args.verbose,
            quiet=args.quiet,
            use_colors=not args.no_colors
        )
        
        # Check if input is a URL
        input_str = args.input
        
        if is_url(input_str):
            # Handle URL input
            ui.print_header("Downloading torrent file from URL...")
            ui.print_info(f"URL: {input_str}")
            
            results = []
            try:
                ui.print_progress(1, 1, input_str)
                magnet_link, info_hash, metadata = converter.convert_from_url(
                    input_str,
                    include_trackers=args.include_trackers
                )
                
                results.append((input_str, magnet_link, info_hash, metadata))
                ui.print_success(f"Downloaded and converted: {input_str}")
                
                if args.verbose:
                    ui.print_verbose(f"  Info Hash: {info_hash}")
                    if metadata.get('name'):
                        ui.print_verbose(f"  Name: {metadata['name']}")
                    if metadata.get('trackers'):
                        ui.print_verbose(f"  Trackers: {len(metadata['trackers'])} found")
                    if metadata.get('file_size'):
                        ui.print_verbose(f"  File Size: {metadata['file_size']} bytes")
            
            except Exception as e:
                error_msg = str(e)
                results.append((input_str, f"Error: {error_msg}", "", {}))
                ui.print_error(f"{input_str}: {error_msg}")
        else:
            # Handle file/directory input
            input_path = Path(args.input)
            
            if not input_path.exists():
                ui.print_error(f"Path does not exist: {input_path}")
                sys.exit(1)
            
            # Collect torrent files
            ui.print_header("Searching for torrent files...")
            torrent_files = collect_torrent_files(
                input_path,
                recursive=args.recursive,
                case_sensitive=args.case_sensitive
            )
            
            if not torrent_files:
                ui.print_warning(f"No .torrent files found: {input_path}")
                sys.exit(0)
            
            ui.print_info(f"Found {len(torrent_files)} torrent file(s)")
            if args.recursive:
                ui.print_verbose("Search mode: Recursive")
            else:
                ui.print_verbose("Search mode: Current directory only")
            
            # Process files
            ui.print_header("Starting conversion...")
            results = []
            
            for idx, torrent_file in enumerate(torrent_files, 1):
                ui.print_progress(idx, len(torrent_files), torrent_file.name)
                
                try:
                    magnet_link, info_hash, metadata = converter.convert(
                        torrent_file,
                        include_trackers=args.include_trackers
                    )
                    
                    results.append((str(torrent_file), magnet_link, info_hash, metadata))
                    ui.print_success(f"{torrent_file.name}")
                    
                    if args.verbose:
                        ui.print_verbose(f"  Info Hash: {info_hash}")
                        if metadata.get('name'):
                            ui.print_verbose(f"  Name: {metadata['name']}")
                        if metadata.get('trackers'):
                            ui.print_verbose(f"  Trackers: {len(metadata['trackers'])} found")
                
                except Exception as e:
                    error_msg = str(e)
                    results.append((str(torrent_file), f"Error: {error_msg}", "", {}))
                    ui.print_error(f"{torrent_file.name}: {error_msg}")
        
        # Save or print results
        if results:
            if args.stdout:
                # Print results to stdout
                ui.print_results(results, format_type=args.format)
            else:
                # Save results to file
                # Determine input path for output path calculation
                if is_url(input_str):
                    # For URL input, use current directory
                    input_path_for_output = Path.cwd()
                else:
                    input_path_for_output = Path(args.input)
                
                output_path = get_output_path(
                    input_path_for_output,
                    Path(args.output) if args.output else None
                )
                
                # Adjust output file extension based on format
                if args.format == 'json' and output_path.suffix != '.json':
                    output_path = output_path.with_suffix('.json')
                elif args.format != 'json' and output_path.suffix == '.json':
                    output_path = output_path.with_suffix('.txt')
                
                ui.print_header("Saving results...")
                ui.save_results(results, output_path, format_type=args.format)
        
        # Display summary
        ui.print_summary()
        
        # Return non-zero exit code if there were errors
        if ui.error_count > 0:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled", file=sys.stderr)
        sys.exit(130)
    
    except Exception as e:
        print(f"Unexpected error occurred: {e}", file=sys.stderr)
        if args and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
