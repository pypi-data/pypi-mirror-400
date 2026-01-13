# BHDownloader

A fast and simple Python downloader for **BuzzHeavier** and **FuckingFast** file hosting services.

[![PyPI version](https://badge.fury.io/py/bhdownloader.svg)](https://pypi.org/project/bhdownloader/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Download files** using URLs or file IDs
- **Extract download links** without downloading (`-l/--link-only`)
- **Get file info** (name, size, type) without downloading (`-i/--info`)
- **Batch processing** from a file containing multiple links
- **Parallel operations** for faster batch processing (`-p N`)
- **JSON output** for easy scripting and automation (`-j/--json`)
- **Progress bar** with download statistics
- **Python API** for integration into your projects
- **Cross-platform** (Windows, macOS, Linux)

## Supported Domains

- `buzzheavier.com`
- `bzzhr.co`
- `fuckingfast.net`
- `fuckingfast.co`

## Installation

```bash
pip install bhdownloader
```

## Quick Start

```bash
# Download a file
bhdownloader https://fuckingfast.net/abc123xyz456

# Get download link only (no download)
bhdownloader -l https://fuckingfast.net/abc123xyz456

# Get file info
bhdownloader -i https://fuckingfast.net/abc123xyz456
```

## Command-Line Usage

### Download Files

```bash
# Download using full URL
bhdownloader https://fuckingfast.net/abc123xyz456

# Download using just the file ID
bhdownloader abc123xyz456

# Download to a specific directory
bhdownloader abc123xyz456 -o ./downloads

# Short alias
bhd abc123xyz456
```

### Get Download Links (No Download)

Extract direct download links without actually downloading the files:

```bash
# Get link for a single file
bhdownloader -l https://fuckingfast.net/abc123xyz456
# Output: https://trashbytes.net/d/abc123xyz456?v=...

# Get links for multiple files and save to a file
bhdownloader -l -f urls.txt -O links.txt

# Get links in JSON format
bhdownloader -l -f urls.txt --json

# Get links in parallel (faster for many files)
bhdownloader -l -f urls.txt -p 5 --json > links.json
```

### Get File Information

View file metadata without downloading:

```bash
# Get info for a single file
bhdownloader -i https://fuckingfast.net/abc123xyz456
# Output:
# Filename:     myfile.zip
# File ID:      abc123xyz456
# Page URL:     https://fuckingfast.net/abc123xyz456
# Download URL: https://trashbytes.net/d/abc123xyz456?v=...
# Size:         1.23 MB
# Content-Type: application/zip
# Available:    Yes

# Get info in JSON format
bhdownloader -i abc123xyz456 --json

# Get info for multiple files
bhdownloader -i -f urls.txt --json
```

### Batch Operations

Create a text file with one URL or ID per line:

```text
# urls.txt - Lines starting with # are ignored
https://fuckingfast.net/abc123xyz456
https://buzzheavier.com/def789ghi012
jkl345mno678
```

Then process the batch:

```bash
# Download all files
bhdownloader -f urls.txt -o ./downloads

# Download with 3 parallel connections
bhdownloader -f urls.txt -o ./downloads -p 3

# Extract all links
bhdownloader -l -f urls.txt -O links.txt

# Get info for all files
bhdownloader -i -f urls.txt --json > info.json
```

### All CLI Options

```
Usage: bhdownloader [OPTIONS] [URL]

Mode options (default: download):
  -l, --link-only       Get direct download link(s) without downloading
  -i, --info            Show file information without downloading

Input options:
  URL                   URL or file ID to process
  -f, --file FILE       File containing URLs or IDs (one per line)

Output options:
  -o, --output-dir DIR  Output directory for downloads (default: current)
  -O, --output-file FILE  Output file for links (use with -l)
  -j, --json            Output results in JSON format (use with -l or -i)

Processing options:
  -p, --parallel N      Number of parallel operations (default: 1)
  -t, --timeout SECS    Request timeout in seconds (default: 30)

Display options:
  -q, --quiet           Suppress output except errors
  -v, --verbose         Enable verbose/debug output
  --no-banner           Don't show the banner

Other:
  -V, --version         Show version and exit
  -h, --help            Show help message and exit
```

## Python API

### Basic Usage

```python
from bhdownloader import download, get_file_info, get_download_link

# Download a file
download("https://fuckingfast.net/abc123xyz456")
download("abc123xyz456", output_dir="./downloads")

# Get download link without downloading
url = resolve_url("abc123xyz456")
download_url, filename = get_download_link(url)
print(f"Link: {download_url}")

# Get comprehensive file info
info = get_file_info("abc123xyz456")
print(f"Filename: {info.filename}")
print(f"Size: {info.size_formatted}")
print(f"Download URL: {info.download_url}")
```

### FileInfo Object

The `get_file_info()` function returns a `FileInfo` object with these attributes:

```python
from bhdownloader import get_file_info, FileInfo

info: FileInfo = get_file_info("abc123xyz456")

info.filename       # Original filename (e.g., "myfile.zip")
info.file_id        # File ID (e.g., "abc123xyz456")
info.page_url       # Page URL (e.g., "https://buzzheavier.com/abc123xyz456")
info.download_url   # Direct download URL (time-limited)
info.size           # File size in bytes (or None)
info.size_formatted # Human-readable size (e.g., "1.23 MB")
info.content_type   # MIME type (e.g., "application/zip")
info.is_available   # True if file exists and is downloadable
info.error          # Error message if not available

# Convert to dictionary (useful for JSON serialization)
data = info.to_dict()

# Pretty print
print(info)
```

### Batch Operations

```python
from bhdownloader import get_file_info, get_multiple_file_info

# Get info for multiple files
urls = ["abc123xyz456", "def789ghi012", "jkl345mno678"]
infos = get_multiple_file_info(urls)

for info in infos:
    if info.is_available:
        print(f"{info.filename}: {info.download_url}")
    else:
        print(f"{info.file_id}: {info.error}")
```

### Download with Options

```python
from bhdownloader import download

# Download with all options
result = download(
    input_str="abc123xyz456",
    output_dir="./downloads",
    output_filename="custom_name.zip",  # Optional: rename file
    timeout=60,                          # Request timeout
    show_progress=True,                  # Show progress bar
    quiet=False,                         # Print status messages
)
print(f"Downloaded to: {result}")

# Download with custom progress callback
def my_progress(downloaded: int, total: int):
    percent = (downloaded / total) * 100 if total else 0
    print(f"\rProgress: {percent:.1f}%", end="", flush=True)

download(
    "abc123xyz456",
    show_progress=False,
    progress_callback=my_progress,
)
```

### Error Handling

```python
from bhdownloader import download, get_file_info
from bhdownloader import (
    BHDownloaderError,   # Base exception
    InvalidURLError,     # Invalid URL or file ID
    DownloadError,       # Download failed
    FileNotFoundError,   # File not found or expired
)

try:
    download("abc123xyz456")
except InvalidURLError as e:
    print(f"Invalid URL or ID: {e}")
except FileNotFoundError as e:
    print(f"File not found or expired: {e}")
except DownloadError as e:
    print(f"Download failed: {e}")
except BHDownloaderError as e:
    print(f"General error: {e}")

# Or use get_file_info which doesn't raise for unavailable files
info = get_file_info("abc123xyz456")
if not info.is_available:
    print(f"File unavailable: {info.error}")
```

### URL Resolution

```python
from bhdownloader import resolve_url, VALID_DOMAINS

# Convert file ID to full URL
url = resolve_url("abc123xyz456")
# Returns: "https://buzzheavier.com/abc123xyz456"

# Full URLs are validated and returned as-is
url = resolve_url("https://fuckingfast.net/abc123xyz456")
# Returns: "https://fuckingfast.net/abc123xyz456"

# See supported domains
print(VALID_DOMAINS)
# ['buzzheavier.com', 'bzzhr.co', 'fuckingfast.net', 'fuckingfast.co']
```

## API Reference

### Functions

| Function | Description |
|----------|-------------|
| `download(input_str, **kwargs)` | Download a file |
| `get_file_info(input_str, timeout, fetch_size)` | Get file metadata |
| `get_multiple_file_info(inputs, timeout, fetch_size)` | Get metadata for multiple files |
| `get_download_link(url, timeout, session)` | Get direct download URL and filename |
| `resolve_url(input_str)` | Convert ID to full URL |
| `download_file(url, output_path, **kwargs)` | Download from direct URL |

### Classes

| Class | Description |
|-------|-------------|
| `FileInfo` | Dataclass containing file metadata |

### Exceptions

| Exception | Description |
|-----------|-------------|
| `BHDownloaderError` | Base exception for all errors |
| `InvalidURLError` | Invalid URL or file ID |
| `DownloadError` | Download operation failed |
| `FileNotFoundError` | File not found or expired |

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `VALID_DOMAINS` | `[...]` | List of supported domains |
| `DEFAULT_TIMEOUT` | `30` | Default request timeout (seconds) |
| `DEFAULT_CHUNK_SIZE` | `8192` | Default download chunk size (bytes) |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### v1.1.0
- Added `-l/--link-only` mode to extract download links without downloading
- Added `-i/--info` mode to view file information
- Added `-j/--json` flag for JSON output
- Added `-O/--output-file` option to save links to a file
- Added `get_file_info()` and `get_multiple_file_info()` functions
- Added `FileInfo` dataclass with file metadata
- Improved error handling and user feedback
- Better parallel processing support

### v1.0.0
- Initial release
- Basic download functionality
- Batch download support
- Parallel downloads
- Python API
