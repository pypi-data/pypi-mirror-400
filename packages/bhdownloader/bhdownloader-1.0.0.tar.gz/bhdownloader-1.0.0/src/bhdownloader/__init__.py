"""
BHDownloader - A simple and fast downloader for BuzzHeavier/FuckingFast file hosting.

This package provides both a CLI tool and a Python API for downloading files
from buzzheavier.com, bzzhr.co, fuckingfast.net, and fuckingfast.co.
"""

__version__ = "1.0.0"
__author__ = "BHDownloader Contributors"

from .core import (
    download,
    download_file,
    resolve_url,
    get_download_link,
    VALID_DOMAINS,
)

__all__ = [
    "download",
    "download_file", 
    "resolve_url",
    "get_download_link",
    "VALID_DOMAINS",
    "__version__",
]
