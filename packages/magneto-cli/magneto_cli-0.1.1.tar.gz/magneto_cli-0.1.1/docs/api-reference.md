# API Reference

This document describes the Python API of Magneto, suitable for developers who need to integrate Magneto functionality into their code.

## Core Modules

### TorrentConverter

`magneto.core.TorrentConverter` is the core conversion class responsible for converting torrent files to magnet links.

#### Initialization

```python
from magneto.core import TorrentConverter

converter = TorrentConverter()
```

#### Methods

##### `read_torrent_file(torrent_path: Path) -> bytes`

Read torrent file content.

**Parameters:**
- `torrent_path` (Path): Path to the torrent file

**Returns:**
- `bytes`: Binary content of the file

**Raises:**
- `IOError`: File read failed

**Example:**
```python
from pathlib import Path

data = converter.read_torrent_file(Path("example.torrent"))
```

##### `parse_torrent(torrent_data: bytes) -> Dict`

Parse torrent file data.

**Parameters:**
- `torrent_data` (bytes): Binary data of the torrent file

**Returns:**
- `Dict`: Parsed torrent data dictionary

**Raises:**
- `ValueError`: Torrent file format error

**Example:**
```python
torrent_data = converter.parse_torrent(data)
```

##### `get_info_hash(torrent_data: Dict) -> str`

Extract Info Hash from torrent data.

**Parameters:**
- `torrent_data` (Dict): Parsed torrent data dictionary

**Returns:**
- `str`: Info Hash as hexadecimal string (uppercase)

**Raises:**
- `ValueError`: Torrent data missing info field

**Example:**
```python
info_hash = converter.get_info_hash(torrent_data)
# Output: "ABC123DEF456..."
```

##### `get_torrent_name(torrent_data: Dict) -> Optional[str]`

Extract file name from torrent data.

**Parameters:**
- `torrent_data` (Dict): Parsed torrent data dictionary

**Returns:**
- `Optional[str]`: File name, or None if not present

**Example:**
```python
name = converter.get_torrent_name(torrent_data)
# Output: "Example File"
```

##### `get_trackers(torrent_data: Dict) -> list`

Extract tracker list from torrent data.

**Parameters:**
- `torrent_data` (Dict): Parsed torrent data dictionary

**Returns:**
- `list`: List of tracker URLs

**Example:**
```python
trackers = converter.get_trackers(torrent_data)
# Output: ["http://tracker1.example.com", "http://tracker2.example.com"]
```

##### `generate_magnet_link(info_hash: str, name: Optional[str] = None, trackers: Optional[list] = None) -> str`

Generate magnet link.

**Parameters:**
- `info_hash` (str): Info Hash string
- `name` (Optional[str]): File name (optional)
- `trackers` (Optional[list]): Tracker list (optional)

**Returns:**
- `str`: Complete magnet link

**Example:**
```python
magnet = converter.generate_magnet_link(
    info_hash="ABC123...",
    name="Example",
    trackers=["http://tracker.example.com"]
)
# Output: "magnet:?xt=urn:btih:ABC123...&dn=Example&tr=http://tracker.example.com"
```

##### `convert(torrent_path: Path, include_trackers: bool = False) -> Tuple[str, str, Dict]`

Convert a single torrent file to magnet link.

**Parameters:**
- `torrent_path` (Path): Path to the torrent file
- `include_trackers` (bool): Whether to include trackers in the magnet link

**Returns:**
- `Tuple[str, str, Dict]`: (magnet_link, info_hash, metadata)
  - `magnet_link`: Magnet link
  - `info_hash`: Info Hash
  - `metadata`: Metadata dictionary containing:
    - `name`: File name
    - `trackers`: Tracker list
    - `info_hash`: Info Hash
    - `file_size`: File size

**Raises:**
- `IOError`: File read failed
- `ValueError`: Torrent file format error

**Example:**
```python
from pathlib import Path

magnet_link, info_hash, metadata = converter.convert(
    Path("example.torrent"),
    include_trackers=True
)

print(f"Magnet: {magnet_link}")
print(f"Info Hash: {info_hash}")
print(f"Name: {metadata['name']}")
print(f"Trackers: {metadata['trackers']}")
```

## Utility Functions

### `collect_torrent_files`

`magneto.utils.collect_torrent_files` - Collect torrent files.

```python
from magneto.utils import collect_torrent_files
from pathlib import Path

# Collect torrent files in current directory
files = collect_torrent_files(Path("folder/"))

# Recursive search
files = collect_torrent_files(Path("folder/"), recursive=True)

# Case-sensitive search
files = collect_torrent_files(Path("folder/"), case_sensitive=True)
```

**Parameters:**
- `input_path` (Path): Input path (file or directory)
- `recursive` (bool): Whether to recursively search subdirectories (default: False)
- `case_sensitive` (bool): Whether to be case-sensitive (default: False)

**Returns:**
- `List[Path]`: List of torrent file paths

### `get_output_path`

`magneto.utils.get_output_path` - Determine output file path.

```python
from magneto.utils import get_output_path
from pathlib import Path

# Auto-determine output path
output = get_output_path(Path("folder/"))

# Specify output path
output = get_output_path(Path("folder/"), Path("custom_output.txt"))
```

**Parameters:**
- `input_path` (Path): Input path
- `output_path` (Optional[Path]): User-specified output path (optional)
- `default_name` (str): Default output file name (default: "magnet_links.txt")

**Returns:**
- `Path`: Output file path

## UI Module

### UI

`magneto.ui.UI` - User interface handler.

```python
from magneto.ui import UI

# Initialize UI
ui = UI(verbose=True, quiet=False, use_colors=True)

# Print messages
ui.print_success("Conversion successful")
ui.print_error("Conversion failed")
ui.print_warning("Warning message")
ui.print_info("Info message")
ui.print_verbose("Verbose message")

# Save results
results = [
    ("file.torrent", "magnet:...", "ABC123...", {"name": "Example"})
]
ui.save_results(results, Path("output.txt"), format_type="full")

# Print results to stdout
ui.print_results(results, format_type="json")

# Print summary
ui.print_summary()
```

**Initialization Parameters:**
- `verbose` (bool): Whether to show detailed information (default: False)
- `quiet` (bool): Whether to use quiet mode (default: False)
- `use_colors` (bool): Whether to use colored output (default: True)

## Complete Examples

### Example 1: Batch Convert Files

```python
from pathlib import Path
from magneto.core import TorrentConverter
from magneto.utils import collect_torrent_files

converter = TorrentConverter()
torrent_files = collect_torrent_files(Path("folder/"), recursive=True)

results = []
for torrent_file in torrent_files:
    try:
        magnet_link, info_hash, metadata = converter.convert(
            torrent_file,
            include_trackers=True
        )
        results.append((str(torrent_file), magnet_link, info_hash, metadata))
        print(f"✓ {torrent_file.name}: {magnet_link}")
    except Exception as e:
        print(f"✗ {torrent_file.name}: {e}")
```

### Example 2: Custom Output Format

```python
import json
from pathlib import Path
from magneto.core import TorrentConverter

converter = TorrentConverter()
torrent_file = Path("example.torrent")

magnet_link, info_hash, metadata = converter.convert(torrent_file)

output = {
    "file": str(torrent_file),
    "magnet": magnet_link,
    "info_hash": info_hash,
    "name": metadata.get("name"),
    "trackers": metadata.get("trackers", [])
}

with open("output.json", "w", encoding="utf-8") as f:
    json.dump([output], f, ensure_ascii=False, indent=2)
```

### Example 3: Integration into Scripts

```python
#!/usr/bin/env python3
"""Custom conversion script"""
from pathlib import Path
from magneto.core import TorrentConverter
from magneto.utils import collect_torrent_files

def convert_folder(folder_path: str, output_file: str):
    converter = TorrentConverter()
    torrent_files = collect_torrent_files(Path(folder_path), recursive=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        for torrent_file in torrent_files:
            try:
                magnet_link, _, _ = converter.convert(torrent_file)
                f.write(f"{magnet_link}\n")
                print(f"✓ {torrent_file.name}")
            except Exception as e:
                print(f"✗ {torrent_file.name}: {e}")

if __name__ == "__main__":
    convert_folder("downloads/", "magnets.txt")
```

## Exception Handling

### Common Exceptions

- `IOError`: File read failed
- `ValueError`: Torrent file format error or missing required fields
- `ImportError`: Missing required dependencies (e.g., bencode)

### Exception Handling Example

```python
from magneto.core import TorrentConverter
from pathlib import Path

converter = TorrentConverter()

try:
    magnet_link, info_hash, metadata = converter.convert(Path("file.torrent"))
except IOError as e:
    print(f"File read error: {e}")
except ValueError as e:
    print(f"File format error: {e}")
except Exception as e:
    print(f"Unknown error: {e}")
```

## Type Hints

All functions and classes include complete type hints for IDE autocompletion and type checking.

```python
from typing import Dict, Optional, Tuple, List
from pathlib import Path
```

## Next Steps

- [Usage Guide](/usage) - Learn command-line usage
- [Getting Started](/getting-started) - Learn basic usage

