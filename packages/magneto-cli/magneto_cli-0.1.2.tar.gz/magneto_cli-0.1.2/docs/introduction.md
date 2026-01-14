# Introduction

Magneto is a powerful and user-friendly command-line tool for batch converting torrent files (.torrent) to magnet links.

## What are Magnet Links?

Magnet links are a special type of hyperlink that identify and locate files by their content hash rather than by their location. Magnet links typically start with `magnet:?` and contain the following information:

- **Info Hash (xt)**: A unique identifier for the file, generated using the SHA-1 hash algorithm
- **Display Name (dn)**: An optional display name
- **Tracker (tr)**: Optional tracker server addresses

## Why Use Magneto?

### Limitations of Traditional Torrent Files

Traditional torrent files require:
- Downloading and saving `.torrent` files
- Opening with a BitTorrent client
- Taking up storage space
- Managing multiple files can be cumbersome

### Advantages of Magnet Links

- **Lightweight**: Only requires a link string, no file needed
- **Easy to Share**: Can be easily copied and pasted
- **Good Compatibility**: Most modern BitTorrent clients support them
- **Easy to Manage**: Can be stored in text files for batch management

### Features of Magneto

✨ **Batch Processing** - Support single file or entire folder batch conversion  
🔍 **Recursive Search** - Recursively search for torrent files in subdirectories  
🎨 **Beautiful Output** - Colored terminal output with clear progress display  
📝 **Multiple Formats** - Support full format, links only, and JSON format output  
🔗 **Tracker Support** - Optionally include tracker information in magnet links  
📊 **Detailed Statistics** - Display processing progress and success/failure statistics  
🎯 **Flexible Configuration** - Rich command-line argument options  

## Use Cases

- **Batch Conversion**: Convert large numbers of torrent files to magnet links
- **File Organization**: Convert torrent files to more manageable magnet link format
- **Automation Scripts**: Integrate batch conversion functionality into scripts
- **Data Migration**: Migrate from torrent files to magnet links

## System Requirements

- Python 3.7 or higher
- Windows, macOS, or Linux operating system

## Next Steps

- [Getting Started](/getting-started) - Learn how to quickly use Magneto
- [Installation](/installation) - Detailed installation instructions
- [Usage Guide](/usage) - Learn how to use various features

