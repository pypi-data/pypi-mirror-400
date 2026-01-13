"""
Core functionality for BHDownloader.

This module provides the main download functions and URL resolution logic.
"""

import os
import re
import logging
from dataclasses import dataclass, asdict
from typing import Optional, Callable, Dict, Any, List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Configure logging
logger = logging.getLogger(__name__)

# Valid domains for BuzzHeavier/FuckingFast
VALID_DOMAINS = [
    "buzzheavier.com",
    "bzzhr.co", 
    "fuckingfast.net",
    "fuckingfast.co",
]

# Default configuration
DEFAULT_TIMEOUT = 30
DEFAULT_CHUNK_SIZE = 8192
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class BHDownloaderError(Exception):
    """Base exception for BHDownloader errors."""
    pass


class InvalidURLError(BHDownloaderError):
    """Raised when the URL or ID is invalid."""
    pass


class DownloadError(BHDownloaderError):
    """Raised when download fails."""
    pass


class FileNotFoundError(BHDownloaderError):
    """Raised when the file is not found or expired."""
    pass


@dataclass
class FileInfo:
    """
    Information about a file on BuzzHeavier/FuckingFast.
    
    Attributes:
        filename: Original filename of the file.
        file_id: The unique file identifier.
        page_url: The original page URL.
        download_url: Direct download URL (time-limited).
        size: File size in bytes (None if unknown).
        size_formatted: Human-readable file size.
        content_type: MIME type of the file (None if unknown).
        is_available: Whether the file is available for download.
        error: Error message if file is not available.
    """
    filename: str
    file_id: str
    page_url: str
    download_url: str
    size: Optional[int] = None
    size_formatted: Optional[str] = None
    content_type: Optional[str] = None
    is_available: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert FileInfo to a dictionary."""
        return asdict(self)
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        lines = [
            f"Filename:     {self.filename}",
            f"File ID:      {self.file_id}",
            f"Page URL:     {self.page_url}",
            f"Download URL: {self.download_url}",
        ]
        if self.size_formatted:
            lines.append(f"Size:         {self.size_formatted}")
        if self.content_type:
            lines.append(f"Content-Type: {self.content_type}")
        lines.append(f"Available:    {'Yes' if self.is_available else 'No'}")
        if self.error:
            lines.append(f"Error:        {self.error}")
        return "\n".join(lines)


def _format_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def _extract_file_id(url: str) -> str:
    """Extract the file ID from a BuzzHeavier URL."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    # Handle paths like "/abc123xyz456" or "/abc123xyz456/download"
    parts = path.split("/")
    return parts[0] if parts else ""


def resolve_url(input_str: str) -> str:
    """
    Resolve an input string to a valid BuzzHeavier URL.
    
    Args:
        input_str: Either a full URL or a 12-character file ID.
        
    Returns:
        A valid BuzzHeavier URL.
        
    Raises:
        InvalidURLError: If the input is not a valid URL or ID.
        
    Examples:
        >>> resolve_url("https://fuckingfast.net/2dqn6xfvimft")
        'https://fuckingfast.net/2dqn6xfvimft'
        >>> resolve_url("2dqn6xfvimft")
        'https://buzzheavier.com/2dqn6xfvimft'
    """
    input_str = input_str.strip()
    
    if not input_str:
        raise InvalidURLError("Input cannot be empty")
    
    # Handle full URLs
    if input_str.startswith(("http://", "https://")):
        parsed = urlparse(input_str)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
            
        for valid_domain in VALID_DOMAINS:
            if domain == valid_domain or domain.endswith("." + valid_domain):
                return input_str
                
        raise InvalidURLError(
            f"URL domain '{domain}' not recognized. "
            f"Valid domains: {', '.join(VALID_DOMAINS)}"
        )
    
    # Handle file IDs (typically 12 alphanumeric characters)
    if re.match(r"^[a-zA-Z0-9]{10,14}$", input_str):
        return f"https://{VALID_DOMAINS[0]}/{input_str}"
    
    raise InvalidURLError(
        f"Invalid input: '{input_str}'. "
        "Please provide a valid URL or file ID."
    )


def get_download_link(
    url: str,
    timeout: int = DEFAULT_TIMEOUT,
    session: Optional[requests.Session] = None,
) -> tuple[str, str]:
    """
    Get the direct download link and filename from a BuzzHeavier page.
    
    Args:
        url: The BuzzHeavier page URL.
        timeout: Request timeout in seconds.
        session: Optional requests session for connection pooling.
        
    Returns:
        A tuple of (download_url, filename).
        
    Raises:
        DownloadError: If the download link cannot be obtained.
        FileNotFoundError: If the file doesn't exist or has expired.
    """
    sess = session or requests.Session()
    
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
    }
    
    try:
        # Get the page to extract the title (filename)
        response = sess.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise FileNotFoundError(f"File not found or expired: {url}")
        raise DownloadError(f"Failed to access page: {e}")
    except requests.exceptions.RequestException as e:
        raise DownloadError(f"Network error: {e}")
    
    # Parse the page for the title
    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.title
    
    if not title_tag or not title_tag.string:
        raise DownloadError("Could not extract filename from page")
    
    filename = title_tag.string.strip()
    logger.debug(f"Extracted filename: {filename}")
    
    # Get the download redirect
    download_url = url.rstrip("/") + "/download"
    download_headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "hx-current-url": url,
        "hx-request": "true",
        "referer": url,
    }
    
    try:
        head_response = sess.head(
            download_url,
            headers=download_headers,
            allow_redirects=False,
            timeout=timeout,
        )
    except requests.exceptions.RequestException as e:
        raise DownloadError(f"Failed to get download link: {e}")
    
    hx_redirect = head_response.headers.get("hx-redirect")
    
    if not hx_redirect:
        raise DownloadError(
            "Download link not found. "
            "The file may be a directory or the link format has changed."
        )
    
    # Construct the final download URL
    parsed = urlparse(url)
    if hx_redirect.startswith("/"):
        final_url = f"{parsed.scheme}://{parsed.netloc}{hx_redirect}"
    else:
        final_url = hx_redirect
    
    logger.debug(f"Download URL: {final_url}")
    
    return final_url, filename


def get_file_info(
    input_str: str,
    timeout: int = DEFAULT_TIMEOUT,
    fetch_size: bool = True,
) -> FileInfo:
    """
    Get comprehensive information about a file without downloading it.
    
    This function retrieves the filename, direct download URL, file size,
    and other metadata without actually downloading the file.
    
    Args:
        input_str: URL or file ID to get info for.
        timeout: Request timeout in seconds.
        fetch_size: Whether to make an extra HEAD request to get file size.
        
    Returns:
        FileInfo object containing all file metadata.
        
    Raises:
        InvalidURLError: If the input is invalid.
        FileNotFoundError: If the file doesn't exist.
        DownloadError: If fetching info fails.
        
    Examples:
        >>> info = get_file_info("https://fuckingfast.net/abc123xyz456")
        >>> print(info.filename)
        'myfile.zip'
        >>> print(info.download_url)
        'https://trashbytes.net/d/abc123xyz456?v=...'
        >>> print(info.size_formatted)
        '1.23 MB'
    """
    # Resolve the URL
    url = resolve_url(input_str)
    file_id = _extract_file_id(url)
    
    with requests.Session() as session:
        try:
            # Get download link and filename
            download_url, filename = get_download_link(
                url, timeout=timeout, session=session
            )
            
            size = None
            size_formatted = None
            content_type = None
            
            # Optionally fetch file size via streaming GET request
            # (HEAD requests don't always return content-length on CDNs)
            if fetch_size:
                try:
                    # Use GET with stream=True to only fetch headers
                    get_response = session.get(
                        download_url,
                        headers={"User-Agent": DEFAULT_USER_AGENT},
                        timeout=timeout,
                        stream=True,
                    )
                    get_response.raise_for_status()
                    
                    content_length = get_response.headers.get("content-length")
                    if content_length:
                        size = int(content_length)
                        size_formatted = _format_size(size)
                    
                    content_type = get_response.headers.get("content-type")
                    
                    # Close the connection without downloading the body
                    get_response.close()
                except requests.exceptions.RequestException:
                    # Size fetch failed, but we still have the download URL
                    logger.debug("Failed to fetch file size")
            
            return FileInfo(
                filename=filename,
                file_id=file_id,
                page_url=url,
                download_url=download_url,
                size=size,
                size_formatted=size_formatted,
                content_type=content_type,
                is_available=True,
                error=None,
            )
            
        except FileNotFoundError as e:
            return FileInfo(
                filename="",
                file_id=file_id,
                page_url=url,
                download_url="",
                is_available=False,
                error=str(e),
            )
        except DownloadError as e:
            return FileInfo(
                filename="",
                file_id=file_id,
                page_url=url,
                download_url="",
                is_available=False,
                error=str(e),
            )


def get_multiple_file_info(
    inputs: List[str],
    timeout: int = DEFAULT_TIMEOUT,
    fetch_size: bool = True,
) -> List[FileInfo]:
    """
    Get information about multiple files.
    
    Args:
        inputs: List of URLs or file IDs.
        timeout: Request timeout in seconds.
        fetch_size: Whether to fetch file sizes.
        
    Returns:
        List of FileInfo objects.
        
    Examples:
        >>> infos = get_multiple_file_info(["abc123", "def456"])
        >>> for info in infos:
        ...     print(f"{info.filename}: {info.download_url}")
    """
    results = []
    for input_str in inputs:
        try:
            info = get_file_info(input_str, timeout=timeout, fetch_size=fetch_size)
            results.append(info)
        except InvalidURLError as e:
            results.append(FileInfo(
                filename="",
                file_id=input_str,
                page_url="",
                download_url="",
                is_available=False,
                error=str(e),
            ))
    return results


def download_file(
    url: str,
    output_path: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout: int = DEFAULT_TIMEOUT,
    show_progress: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    session: Optional[requests.Session] = None,
) -> str:
    """
    Download a file from a direct URL.
    
    Args:
        url: Direct download URL.
        output_path: Path where the file will be saved.
        chunk_size: Size of chunks for streaming download.
        timeout: Request timeout in seconds.
        show_progress: Whether to show a progress bar.
        progress_callback: Optional callback(downloaded, total) for custom progress.
        session: Optional requests session.
        
    Returns:
        The path to the downloaded file.
        
    Raises:
        DownloadError: If the download fails.
    """
    sess = session or requests.Session()
    
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
    }
    
    try:
        response = sess.get(
            url,
            headers=headers,
            stream=True,
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise DownloadError(f"Download failed: {e}")
    
    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Set up progress bar
    progress_bar = None
    if show_progress and total_size > 0:
        progress_bar = tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=os.path.basename(output_path),
        )
    
    try:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if progress_bar:
                        progress_bar.update(len(chunk))
                    
                    if progress_callback:
                        progress_callback(downloaded, total_size)
    finally:
        if progress_bar:
            progress_bar.close()
    
    return output_path


def download(
    input_str: str,
    output_dir: Optional[str] = None,
    output_filename: Optional[str] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout: int = DEFAULT_TIMEOUT,
    show_progress: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    quiet: bool = False,
) -> str:
    """
    Download a file from BuzzHeavier/FuckingFast.
    
    This is the main high-level function for downloading files.
    
    Args:
        input_str: URL or file ID to download.
        output_dir: Directory to save the file (default: current directory).
        output_filename: Custom filename (default: use original filename).
        chunk_size: Size of chunks for streaming download.
        timeout: Request timeout in seconds.
        show_progress: Whether to show a progress bar.
        progress_callback: Optional callback(downloaded, total) for custom progress.
        quiet: If True, suppress all output including progress.
        
    Returns:
        The path to the downloaded file.
        
    Raises:
        InvalidURLError: If the input is invalid.
        FileNotFoundError: If the file doesn't exist.
        DownloadError: If the download fails.
        
    Examples:
        >>> # Download by URL
        >>> download("https://fuckingfast.net/abc123xyz456")
        '/current/dir/filename.zip'
        
        >>> # Download by ID
        >>> download("abc123xyz456", output_dir="/downloads")
        '/downloads/filename.zip'
        
        >>> # Download with custom filename
        >>> download("abc123xyz456", output_filename="myfile.zip")
        '/current/dir/myfile.zip'
    """
    if quiet:
        show_progress = False
    
    # Resolve the URL
    url = resolve_url(input_str)
    
    if not quiet:
        logger.info(f"Fetching: {url}")
    
    # Get the download link and filename
    with requests.Session() as session:
        download_url, original_filename = get_download_link(
            url, timeout=timeout, session=session
        )
        
        # Determine output path
        filename = output_filename or original_filename
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename)
        else:
            output_path = filename
        
        if not quiet:
            logger.info(f"Downloading: {filename}")
        
        # Download the file
        result_path = download_file(
            url=download_url,
            output_path=output_path,
            chunk_size=chunk_size,
            timeout=timeout,
            show_progress=show_progress,
            progress_callback=progress_callback,
            session=session,
        )
        
        if not quiet:
            logger.info(f"Saved: {result_path}")
        
        return result_path
