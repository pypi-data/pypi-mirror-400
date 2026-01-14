"""text_only_scanner

Small library to detect text files and reject non-text/binary files.
"""
__all__ = ["is_text_file", "filter_text_files"]

from .detector import is_text_file, filter_text_files

__version__ = "0.1.1"
