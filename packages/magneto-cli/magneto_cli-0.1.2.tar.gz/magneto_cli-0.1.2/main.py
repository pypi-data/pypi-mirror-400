#!/usr/bin/env python3
"""
Magneto - Command-line tool for batch converting torrent files to magnet links
Main entry point (wrapper for development use)

This file is kept for development convenience. When installed via pip,
the entry point uses magneto.main:main instead.
"""
from magneto.main import main

if __name__ == "__main__":
    main()
