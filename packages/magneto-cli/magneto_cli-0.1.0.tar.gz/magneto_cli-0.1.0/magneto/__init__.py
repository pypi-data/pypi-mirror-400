"""
Magneto - Tool for batch converting torrent files to magnet links
"""
__version__ = "0.1.0"
__author__ = ""

from .core import TorrentConverter
from .parser import ArgumentParser
from .ui import UI

__all__ = ["TorrentConverter", "ArgumentParser", "UI"]
