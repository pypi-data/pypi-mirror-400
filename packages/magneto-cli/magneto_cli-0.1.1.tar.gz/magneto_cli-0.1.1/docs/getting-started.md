# Getting Started

This guide will help you quickly get started with Magneto. In just a few minutes, you'll be able to start batch converting torrent files.

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.7+ installed**
   ```bash
   python --version
   # or
   python3 --version
   ```

2. **Magneto installed**
   ```bash
   pip install magneto-cli
   ```

## Simplest Usage

### 1. Convert a Single File

```bash
magneto file.torrent
```

This will:
- Read the `file.torrent` file
- Generate a magnet link
- Save results to `magnet_links.txt`

### 2. Convert All Files in a Folder

```bash
magneto folder/
```

This will:
- Search for all `.torrent` files in the `folder/` directory
- Convert them in batch
- Save results to `folder/magnet_links.txt`

## Viewing Results

After conversion, you can:

1. **View the output file**
   - By default, results are saved in `magnet_links.txt`
   - The file contains complete conversion information

2. **Use standard output**
   ```bash
   magneto folder/ --stdout
   ```
   Results will be printed directly to the terminal

3. **Get links only**
   ```bash
   magneto folder/ --stdout -f links_only
   ```
   Only output magnet links for easy copying

## Common Command Examples

### Recursive Search

```bash
magneto folder/ -r
```

### Output JSON Format

```bash
magneto folder/ -f json
```

### Include Tracker Information

```bash
magneto folder/ --include-trackers
```

### Verbose Output Mode

```bash
magneto folder/ -v
```

## Next Steps

- [Installation Guide](/installation) - Learn detailed installation methods
- [Usage Guide](/usage) - Learn more advanced features
- [API Reference](/api-reference) - View complete API documentation

