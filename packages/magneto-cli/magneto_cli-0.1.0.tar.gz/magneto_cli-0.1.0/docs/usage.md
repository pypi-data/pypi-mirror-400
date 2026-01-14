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

