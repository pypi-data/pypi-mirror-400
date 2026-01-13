# BHDownloader

A fast and simple Python downloader for **BuzzHeavier** and **FuckingFast** file hosting services.

## Features

- Download files using URLs or file IDs
- Batch download from a file containing multiple links
- Parallel downloads for faster batch processing
- Progress bar with download statistics
- Python API for integration into your projects
- Cross-platform (Windows, macOS, Linux)

## Supported Domains

- `buzzheavier.com`
- `bzzhr.co`
- `fuckingfast.net`
- `fuckingfast.co`

## Installation

```bash
pip install bhdownloader
```

## Command-Line Usage

### Download a single file

```bash
# Using full URL
bhdownloader https://fuckingfast.net/abc123xyz456

# Using just the file ID
bhdownloader abc123xyz456

# Using the short alias
bhd abc123xyz456
```

### Download to a specific directory

```bash
bhdownloader https://fuckingfast.net/abc123xyz456 -o ./downloads
```

### Batch download from a file

Create a text file with one URL or ID per line:

```text
# urls.txt
https://fuckingfast.net/abc123xyz456
https://buzzheavier.com/def789ghi012
jkl345mno678
```

Then run:

```bash
bhdownloader -f urls.txt -o ./downloads
```

### Parallel downloads

Download multiple files simultaneously:

```bash
bhdownloader -f urls.txt -p 3 -o ./downloads
```

### All CLI Options

```
Usage: bhdownloader [OPTIONS] [URL]

Options:
  URL                     URL or file ID to download
  -f, --file FILE         File containing URLs or IDs (one per line)
  -o, --output-dir DIR    Output directory (default: current directory)
  -p, --parallel N        Number of parallel downloads (default: 1)
  -t, --timeout SECONDS   Request timeout in seconds (default: 30)
  -q, --quiet             Suppress output except errors
  -v, --verbose           Enable verbose/debug output
  --no-banner             Don't show the banner
  -V, --version           Show version and exit
  -h, --help              Show help message and exit
```

## Python API

### Basic usage

```python
from bhdownloader import download

# Download by URL
download("https://fuckingfast.net/abc123xyz456")

# Download by file ID
download("abc123xyz456")

# Download to specific directory
download("abc123xyz456", output_dir="./downloads")

# Download with custom filename
download("abc123xyz456", output_filename="myfile.zip")

# Quiet mode (no progress bar)
download("abc123xyz456", quiet=True)
```

### Advanced usage

```python
from bhdownloader import download, resolve_url, get_download_link

# Resolve a file ID to full URL
url = resolve_url("abc123xyz456")
print(url)  # https://buzzheavier.com/abc123xyz456

# Get direct download link without downloading
download_url, filename = get_download_link("https://fuckingfast.net/abc123xyz456")
print(f"Direct URL: {download_url}")
print(f"Filename: {filename}")

# Download with custom progress callback
def my_progress(downloaded, total):
    percent = (downloaded / total) * 100 if total else 0
    print(f"Progress: {percent:.1f}%")

download(
    "abc123xyz456",
    show_progress=False,
    progress_callback=my_progress
)
```

### Error handling

```python
from bhdownloader import download
from bhdownloader.core import (
    InvalidURLError,
    DownloadError,
    FileNotFoundError,
    BHDownloaderError,
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
```

## API Reference

### Functions

#### `download(input_str, **kwargs) -> str`

Download a file from BuzzHeavier/FuckingFast.

**Parameters:**
- `input_str` (str): URL or file ID to download
- `output_dir` (str, optional): Directory to save the file
- `output_filename` (str, optional): Custom filename
- `chunk_size` (int): Download chunk size (default: 8192)
- `timeout` (int): Request timeout in seconds (default: 30)
- `show_progress` (bool): Show progress bar (default: True)
- `progress_callback` (callable): Custom progress callback
- `quiet` (bool): Suppress all output (default: False)

**Returns:** Path to the downloaded file

#### `resolve_url(input_str) -> str`

Resolve a URL or file ID to a valid BuzzHeavier URL.

#### `get_download_link(url, timeout=30) -> tuple[str, str]`

Get the direct download link and filename from a BuzzHeavier page.

**Returns:** Tuple of (download_url, filename)

### Exceptions

- `BHDownloaderError`: Base exception for all errors
- `InvalidURLError`: Invalid URL or file ID
- `DownloadError`: Download failed
- `FileNotFoundError`: File not found or expired

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
