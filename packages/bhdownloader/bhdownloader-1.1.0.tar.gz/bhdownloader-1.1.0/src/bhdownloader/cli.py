"""
Command-line interface for BHDownloader.

Provides a user-friendly CLI for downloading files from BuzzHeavier/FuckingFast.
"""

import argparse
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any

from . import __version__
from .core import (
    download,
    get_file_info,
    get_download_link,
    resolve_url,
    FileInfo,
    BHDownloaderError,
    InvalidURLError,
    DownloadError,
    FileNotFoundError,
    VALID_DOMAINS,
)


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging based on verbosity settings."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s" if not verbose else "%(levelname)s: %(message)s",
    )


def print_banner() -> None:
    """Print the application banner."""
    print(f"""
╔══════════════════════════════════════════════════════╗
║  BHDownloader v{__version__:<39} ║
║  Fast downloader for BuzzHeavier & FuckingFast       ║
╚══════════════════════════════════════════════════════╝
""")


def read_urls_from_file(file_path: str) -> List[str]:
    """
    Read URLs/IDs from a file, one per line.
    
    Ignores empty lines and lines starting with #.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "r") as f:
        lines = [
            line.strip() 
            for line in f 
            if line.strip() and not line.strip().startswith("#")
        ]
    
    return lines


# =============================================================================
# Link-only mode functions
# =============================================================================

def get_link_single(
    input_str: str,
    timeout: int = 30,
    quiet: bool = False,
) -> Optional[str]:
    """
    Get download link for a single URL/ID.
    
    Returns the download URL or None on failure.
    """
    try:
        url = resolve_url(input_str)
        download_url, filename = get_download_link(url, timeout=timeout)
        return download_url
    except InvalidURLError as e:
        if not quiet:
            print(f"✗ Invalid URL/ID: {e}", file=sys.stderr)
    except FileNotFoundError as e:
        if not quiet:
            print(f"✗ File not found: {e}", file=sys.stderr)
    except DownloadError as e:
        if not quiet:
            print(f"✗ Error: {e}", file=sys.stderr)
    except Exception as e:
        if not quiet:
            print(f"✗ Unexpected error: {e}", file=sys.stderr)
    
    return None


def handle_link_only(
    inputs: List[str],
    parallel: int = 1,
    timeout: int = 30,
    output_file: Optional[str] = None,
    json_output: bool = False,
    quiet: bool = False,
) -> int:
    """
    Handle --link-only mode: extract download links without downloading.
    
    Returns exit code (0 for success, 1 for failures).
    """
    results: List[Dict[str, Any]] = []
    links: List[str] = []
    success_count = 0
    failure_count = 0
    
    def process_single(input_str: str) -> Dict[str, Any]:
        link = get_link_single(input_str, timeout=timeout, quiet=True)
        if link:
            return {"input": input_str, "link": link, "success": True}
        else:
            return {"input": input_str, "link": None, "success": False, "error": "Failed to get link"}
    
    if parallel > 1 and len(inputs) > 1:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(process_single, inp): inp for inp in inputs}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if result["success"]:
                    success_count += 1
                    links.append(result["link"])
                else:
                    failure_count += 1
    else:
        # Sequential processing
        for inp in inputs:
            result = process_single(inp)
            results.append(result)
            if result["success"]:
                success_count += 1
                links.append(result["link"])
            else:
                failure_count += 1
    
    # Output results
    if json_output:
        output = json.dumps(results, indent=2)
        if output_file:
            with open(output_file, "w") as f:
                f.write(output)
            if not quiet:
                print(f"✓ Saved {len(results)} results to {output_file}")
        else:
            print(output)
    else:
        output_lines = []
        for result in results:
            if result["success"]:
                output_lines.append(result["link"])
            elif not quiet:
                print(f"✗ {result['input']}: Failed to get link", file=sys.stderr)
        
        if output_file:
            with open(output_file, "w") as f:
                f.write("\n".join(output_lines) + "\n")
            if not quiet:
                print(f"✓ Saved {len(output_lines)} links to {output_file}")
        else:
            for link in output_lines:
                print(link)
            sys.stdout.flush()  # Ensure output is flushed before summary
    
    if not quiet and not json_output and len(inputs) > 1:
        print(f"\n✓ {success_count} succeeded, {failure_count} failed", file=sys.stderr)
    
    return 0 if failure_count == 0 else 1


# =============================================================================
# Info mode functions
# =============================================================================

def handle_info(
    inputs: List[str],
    parallel: int = 1,
    timeout: int = 30,
    json_output: bool = False,
    quiet: bool = False,
) -> int:
    """
    Handle --info mode: show file information without downloading.
    
    Returns exit code (0 for success, 1 for failures).
    """
    results: List[FileInfo] = []
    success_count = 0
    failure_count = 0
    
    def process_single(input_str: str) -> FileInfo:
        return get_file_info(input_str, timeout=timeout, fetch_size=True)
    
    if parallel > 1 and len(inputs) > 1:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(process_single, inp): inp for inp in inputs}
            for future in as_completed(futures):
                info = future.result()
                results.append(info)
                if info.is_available:
                    success_count += 1
                else:
                    failure_count += 1
    else:
        # Sequential processing
        for inp in inputs:
            info = process_single(inp)
            results.append(info)
            if info.is_available:
                success_count += 1
            else:
                failure_count += 1
    
    # Output results
    if json_output:
        output = json.dumps([info.to_dict() for info in results], indent=2)
        print(output)
    else:
        for i, info in enumerate(results):
            if i > 0:
                print("-" * 50)
            if info.is_available:
                print(str(info))
            else:
                print(f"✗ {info.file_id or info.page_url}: {info.error}")
    
    if not quiet and not json_output and len(inputs) > 1:
        print(f"\n✓ {success_count} available, {failure_count} unavailable")
    
    return 0 if failure_count == 0 else 1


# =============================================================================
# Download mode functions
# =============================================================================

def download_single(
    input_str: str,
    output_dir: Optional[str] = None,
    quiet: bool = False,
    timeout: int = 30,
) -> bool:
    """
    Download a single file.
    
    Returns True on success, False on failure.
    """
    try:
        result = download(
            input_str=input_str,
            output_dir=output_dir,
            timeout=timeout,
            quiet=quiet,
        )
        if not quiet:
            print(f"✓ Downloaded: {result}")
        return True
    except InvalidURLError as e:
        print(f"✗ Invalid URL/ID: {e}", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"✗ File not found: {e}", file=sys.stderr)
    except DownloadError as e:
        print(f"✗ Download failed: {e}", file=sys.stderr)
    except BHDownloaderError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\n✗ Download cancelled by user", file=sys.stderr)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
    
    return False


def handle_download(
    inputs: List[str],
    output_dir: Optional[str] = None,
    parallel: int = 1,
    timeout: int = 30,
    quiet: bool = False,
) -> int:
    """
    Handle download mode.
    
    Returns exit code (0 for success, 1 for failures).
    """
    success_count = 0
    failure_count = 0
    
    if parallel > 1 and len(inputs) > 1:
        # Parallel downloads
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(
                    download_single, inp, output_dir, quiet, timeout
                ): inp
                for inp in inputs
            }
            
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
                else:
                    failure_count += 1
    else:
        # Sequential downloads
        for i, inp in enumerate(inputs, 1):
            if not quiet and len(inputs) > 1:
                print(f"\n[{i}/{len(inputs)}] Processing: {inp}")
            
            if download_single(inp, output_dir, quiet, timeout):
                success_count += 1
            else:
                failure_count += 1
    
    if not quiet and len(inputs) > 1:
        print(f"\n✓ Completed: {success_count} succeeded, {failure_count} failed")
    
    return 0 if failure_count == 0 else 1


# =============================================================================
# Argument parser
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all options."""
    parser = argparse.ArgumentParser(
        prog="bhdownloader",
        description="Download files from BuzzHeavier and FuckingFast file hosting services.",
        epilog=f"""
Supported domains: {', '.join(VALID_DOMAINS)}

Examples:
  # Download a file
  bhdownloader https://fuckingfast.net/abc123xyz456
  bhdownloader abc123xyz456 -o ./downloads

  # Get download link only (no download)
  bhdownloader -l https://fuckingfast.net/abc123xyz456
  bhdownloader -l -f urls.txt -O links.txt

  # Get file info (filename, size, etc.)
  bhdownloader -i https://fuckingfast.net/abc123xyz456
  bhdownloader -i -f urls.txt --json

  # Batch operations
  bhdownloader -f urls.txt -o ./downloads -p 3
  bhdownloader -l -f urls.txt --json > links.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Positional argument
    parser.add_argument(
        "url",
        nargs="?",
        help="URL or file ID to process",
    )
    
    # Mode selection (mutually exclusive)
    mode_group = parser.add_argument_group("Mode options (default: download)")
    mode_exclusive = mode_group.add_mutually_exclusive_group()
    
    mode_exclusive.add_argument(
        "-l", "--link-only",
        action="store_true",
        help="Get direct download link(s) without downloading",
    )
    
    mode_exclusive.add_argument(
        "-i", "--info",
        action="store_true",
        help="Show file information (name, size, type) without downloading",
    )
    
    # Input options
    input_group = parser.add_argument_group("Input options")
    
    input_group.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing URLs or IDs (one per line, # for comments)",
    )
    
    # Output options
    output_group = parser.add_argument_group("Output options")
    
    output_group.add_argument(
        "-o", "--output-dir",
        metavar="DIR",
        help="Output directory for downloaded files (default: current directory)",
    )
    
    output_group.add_argument(
        "-O", "--output-file",
        metavar="FILE",
        help="Output file for links (use with -l/--link-only)",
    )
    
    output_group.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output results in JSON format (use with -l or -i)",
    )
    
    # Processing options
    proc_group = parser.add_argument_group("Processing options")
    
    proc_group.add_argument(
        "-p", "--parallel",
        type=int,
        default=1,
        metavar="N",
        help="Number of parallel operations (default: 1)",
    )
    
    proc_group.add_argument(
        "-t", "--timeout",
        type=int,
        default=30,
        metavar="SECONDS",
        help="Request timeout in seconds (default: 30)",
    )
    
    # Display options
    display_group = parser.add_argument_group("Display options")
    
    display_group.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress output except errors and requested data",
    )
    
    display_group.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose/debug output",
    )
    
    display_group.add_argument(
        "--no-banner",
        action="store_true",
        help="Don't show the banner",
    )
    
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    return parser


# =============================================================================
# Main entry point
# =============================================================================

def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose, quiet=args.quiet)
    
    # Show banner (unless quiet, json output, or link-only mode)
    show_banner = (
        not args.quiet 
        and not args.no_banner 
        and not args.json
        and not args.link_only  # Don't show banner for link-only mode (clean output)
    )
    if show_banner:
        print_banner()
    
    # Collect inputs
    inputs: List[str] = []
    
    if args.file:
        try:
            inputs.extend(read_urls_from_file(args.file))
        except Exception as e:
            print(f"✗ Error reading file: {e}", file=sys.stderr)
            return 1
    
    if args.url:
        inputs.append(args.url)
    
    # Validate inputs
    if not inputs:
        if args.file:
            print("✗ No valid URLs or IDs found in file", file=sys.stderr)
        else:
            parser.print_help()
            print("\nError: Please provide a URL, file ID, or use -f to specify a file.")
        return 1
    
    # Validate option combinations
    if args.output_file and not args.link_only:
        print("✗ -O/--output-file can only be used with -l/--link-only", file=sys.stderr)
        return 1
    
    if args.output_dir and (args.link_only or args.info):
        print("✗ -o/--output-dir cannot be used with -l/--link-only or -i/--info", file=sys.stderr)
        return 1
    
    # Handle different modes
    try:
        if args.link_only:
            return handle_link_only(
                inputs=inputs,
                parallel=args.parallel,
                timeout=args.timeout,
                output_file=args.output_file,
                json_output=args.json,
                quiet=args.quiet,
            )
        
        elif args.info:
            return handle_info(
                inputs=inputs,
                parallel=args.parallel,
                timeout=args.timeout,
                json_output=args.json,
                quiet=args.quiet,
            )
        
        else:
            # Default: download mode
            return handle_download(
                inputs=inputs,
                output_dir=args.output_dir,
                parallel=args.parallel,
                timeout=args.timeout,
                quiet=args.quiet,
            )
    
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user", file=sys.stderr)
        return 130


def cli() -> None:
    """Entry point that exits with appropriate code."""
    sys.exit(main())


if __name__ == "__main__":
    cli()
