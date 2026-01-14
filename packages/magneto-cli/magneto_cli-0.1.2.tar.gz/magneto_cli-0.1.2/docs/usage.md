# Usage Guide

This guide provides detailed information about all features and usage methods of Magneto.

## Basic Usage

### Convert a Single File

```bash
magneto file.torrent
```

### Convert All Files in a Folder

```bash
magneto folder/
```

### Specify Output File

```bash
magneto folder/ -o output.txt
```

## Output Formats

Magneto supports three output formats:

### 1. Full Format (Default)

```bash
magneto folder/ -f full
```

Output example:
```
================================================================================
Torrent to Magnet Link Conversion Results
================================================================================

File: example.torrent
Magnet Link: magnet:?xt=urn:btih:ABC123...&dn=Example
Info Hash: ABC123...
Name: Example
Trackers: 3 found
--------------------------------------------------------------------------------

================================================================================
Magnet Link List (Links Only)
================================================================================

magnet:?xt=urn:btih:ABC123...&dn=Example
```

### 2. Links Only Format

```bash
magneto folder/ -f links_only
```

Output example:
```
magnet:?xt=urn:btih:ABC123...&dn=Example
magnet:?xt=urn:btih:DEF456...&dn=Another
```

### 3. JSON Format

```bash
magneto folder/ -f json
```

Output example:
```json
[
  {
    "file": "example.torrent",
    "magnet": "magnet:?xt=urn:btih:ABC123...&dn=Example",
    "info_hash": "ABC123...",
    "name": "Example",
    "trackers": [
      "http://tracker1.example.com",
      "http://tracker2.example.com"
    ]
  }
]
```

## Search Options

### Recursive Search

Recursively search for torrent files in subdirectories:

```bash
magneto folder/ -r
```

### Case-Sensitive Search

By default, search is case-insensitive (both `.torrent` and `.TORRENT` will be found). If case-sensitive search is needed:

```bash
magneto folder/ --case-sensitive
```

## Conversion Options

### Include Tracker Information

By default, generated magnet links do not include tracker information. To include:

```bash
magneto folder/ --include-trackers
```

Generated magnet links will include all tracker addresses:
```
magnet:?xt=urn:btih:ABC123...&dn=Example&tr=http://tracker1.com&tr=http://tracker2.com
```

## Display Options

### Verbose Output Mode

Display detailed processing information:

```bash
magneto folder/ -v
```

Output includes:
- Info Hash for each file
- File name
- Number of trackers

### Quiet Mode

Only show error messages:

```bash
magneto folder/ -q
```

### Disable Color Output

```bash
magneto folder/ --no-colors
```

## Output Methods

### Save to File (Default)

```bash
magneto folder/ -o output.txt
```

Results will be saved to the specified file. If `-o` is not specified, defaults to `magnet_links.txt`.

### Output to Standard Output

```bash
magneto folder/ --stdout
```

Results will be printed directly to the terminal without saving to a file.

Combine with format options:

```bash
# Output only links to terminal
magneto folder/ --stdout -f links_only

# Output JSON to terminal
magneto folder/ --stdout -f json
```

## Practical Examples

### Example 1: Batch Convert and Save as JSON

```bash
magneto downloads/ -r -f json -o results.json
```

### Example 2: Quickly Get All Magnet Links

```bash
magneto folder/ --stdout -f links_only -q
```

### Example 3: Verbose Mode Conversion with Trackers

```bash
magneto folder/ -v --include-trackers -o output.txt
```

### Example 4: Recursive Search and Output to File

```bash
magneto ~/Downloads/ -r -f full -o ~/magnets.txt
```

## Embed in Code

In addition to the command-line tool, Magneto also provides a Python API that can be used directly in your code.

### Quick Start

Using the `torrent_to_magnet` function is the simplest way to integrate:

```python
from magneto import torrent_to_magnet

# Convert from file path
magnet, info_hash, metadata = torrent_to_magnet("path/to/file.torrent")
print(f"Magnet Link: {magnet}")
print(f"Info Hash: {info_hash}")
print(f"File Name: {metadata['name']}")

# Convert from URL
magnet, info_hash, metadata = torrent_to_magnet("https://example.com/file.torrent")

# Include tracker information
magnet, info_hash, metadata = torrent_to_magnet(
    "file.torrent", 
    include_trackers=True
)
```

### Batch Processing Example

```python
from pathlib import Path
from magneto import torrent_to_magnet

def batch_convert(folder_path: str):
    """Batch convert all torrent files in a folder"""
    folder = Path(folder_path)
    results = []
    
    for torrent_file in folder.glob("*.torrent"):
        try:
            magnet, info_hash, metadata = torrent_to_magnet(torrent_file)
            results.append({
                "file": str(torrent_file),
                "magnet": magnet,
                "info_hash": info_hash,
                "name": metadata["name"]
            })
            print(f"✓ {torrent_file.name}")
        except Exception as e:
            print(f"✗ {torrent_file.name}: {e}")
    
    return results

# Usage example
results = batch_convert("downloads/")
```

### URL Processing Example

```python
from magneto import torrent_to_magnet

def convert_from_url(url: str):
    """Download and convert torrent file from URL"""
    try:
        magnet, info_hash, metadata = torrent_to_magnet(url, include_trackers=True)
        print(f"Magnet Link: {magnet}")
        print(f"Source: {metadata.get('source_url', 'N/A')}")
        return magnet
    except IOError as e:
        print(f"Download failed: {e}")
    except ValueError as e:
        print(f"File format error: {e}")

# Usage example
convert_from_url("https://example.com/torrent.torrent")
```

### Error Handling

```python
from magneto import torrent_to_magnet

try:
    magnet, info_hash, metadata = torrent_to_magnet("file.torrent")
except IOError as e:
    print(f"File read error: {e}")
except ValueError as e:
    print(f"File format error: {e}")
except ImportError as e:
    print(f"Missing dependency: {e}")
```

### Return Value Description

The `torrent_to_magnet` function returns a tuple of three elements:

1. **magnet_link** (str): Generated magnet link
2. **info_hash** (str): Torrent info hash (hexadecimal string, uppercase)
3. **metadata** (Dict): Metadata dictionary containing:
   - `name`: File name
   - `trackers`: List of trackers (included even if `include_trackers=False`)
   - `info_hash`: Info hash
   - `file_size`: File size in bytes
   - `source_url`: Source URL if input is a URL

### More API Usage

For more advanced features (such as custom output formats, batch processing, etc.), please refer to the [API Reference](/api-reference).

## Command-Line Arguments Reference

### Positional Arguments

- `input` - Input torrent file or folder path containing torrent files

### Output Options

- `-o, --output FILE` - Specify output file path (default: `magnet_links.txt` in input directory)
- `-f, --format {full,links_only,json}` - Output format (default: full)
- `--stdout` - Print results to stdout instead of saving to file

### Search Options

- `-r, --recursive` - Recursively search for torrent files in subdirectories
- `--case-sensitive` - Case-sensitive search for file extensions

### Conversion Options

- `--include-trackers` - Include tracker information in magnet links

### Display Options

- `-v, --verbose` - Show verbose output information
- `-q, --quiet` - Quiet mode, only show error messages
- `--no-colors` - Disable colored output

### Other Options

- `-h, --help` - Show help information and exit
- `--version` - Show version information and exit

## Usage Tips

### 1. Pipe Operations

Pipe output to other commands:

```bash
magneto folder/ --stdout -f links_only | grep "ABC123"
```

### 2. Batch Processing Large Folders

For folders containing many files, quiet mode is recommended:

```bash
magneto large_folder/ -r -q -f links_only -o results.txt
```

### 3. Use with Scripts

Using JSON format makes parsing easier in scripts:

```bash
magneto folder/ -f json -o results.json
# Then parse JSON with Python/Node.js, etc.
```

## Error Handling

### Common Errors

1. **File does not exist**
   ```
   Error: Path does not exist: /path/to/file
   ```

2. **File format error**
   ```
   ✗ example.torrent: Unable to parse torrent file
   ```

3. **Permission error**
   ```
   Error: Unable to read file /path/to/file: Permission denied
   ```

### Error Statistics

After processing completes, statistics are displayed:

```
================================================================================
Processing complete: 10 file(s) total
Success: 8
Failed: 2
================================================================================
```

## Next Steps

- [API Reference](/api-reference) - Learn how to use Magneto in code
- [Getting Started](/getting-started) - Review basic usage

