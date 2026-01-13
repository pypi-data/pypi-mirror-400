"""
BHDownloader - A simple and fast downloader for BuzzHeavier/FuckingFast file hosting.

This package provides both a CLI tool and a Python API for downloading files
from buzzheavier.com, bzzhr.co, fuckingfast.net, and fuckingfast.co.
"""

__version__ = "1.1.0"
__author__ = "BHDownloader Contributors"

from .core import (
    # Main functions
    download,
    download_file,
    resolve_url,
    get_download_link,
    get_file_info,
    get_multiple_file_info,
    # Data classes
    FileInfo,
    # Constants
    VALID_DOMAINS,
    DEFAULT_TIMEOUT,
    DEFAULT_CHUNK_SIZE,
    # Exceptions
    BHDownloaderError,
    InvalidURLError,
    DownloadError,
    FileNotFoundError,
)

__all__ = [
    # Main functions
    "download",
    "download_file",
    "resolve_url",
    "get_download_link",
    "get_file_info",
    "get_multiple_file_info",
    # Data classes
    "FileInfo",
    # Constants
    "VALID_DOMAINS",
    "DEFAULT_TIMEOUT",
    "DEFAULT_CHUNK_SIZE",
    # Exceptions
    "BHDownloaderError",
    "InvalidURLError",
    "DownloadError",
    "FileNotFoundError",
    # Metadata
    "__version__",
]
