"""
Command-line interface for BHDownloader.

Provides a user-friendly CLI for downloading files from BuzzHeavier/FuckingFast.
"""

import argparse
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from . import __version__
from .core import (
    download,
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


def download_from_file(
    file_path: str,
    output_dir: Optional[str] = None,
    parallel: int = 1,
    quiet: bool = False,
    timeout: int = 30,
) -> tuple[int, int]:
    """
    Download files from a list file.
    
    Returns (success_count, failure_count).
    """
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}", file=sys.stderr)
        return (0, 1)
    
    # Read and parse the file
    with open(file_path, "r") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    if not lines:
        print("✗ No valid URLs or IDs found in file", file=sys.stderr)
        return (0, 0)
    
    if not quiet:
        print(f"Found {len(lines)} items to download")
    
    success_count = 0
    failure_count = 0
    
    if parallel > 1:
        # Parallel downloads
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(
                    download_single, line, output_dir, quiet, timeout
                ): line
                for line in lines
            }
            
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
                else:
                    failure_count += 1
    else:
        # Sequential downloads
        for i, line in enumerate(lines, 1):
            if not quiet:
                print(f"\n[{i}/{len(lines)}] Processing: {line}")
            
            if download_single(line, output_dir, quiet, timeout):
                success_count += 1
            else:
                failure_count += 1
    
    return (success_count, failure_count)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="bhdownloader",
        description="Download files from BuzzHeavier and FuckingFast file hosting services.",
        epilog=f"""
Supported domains: {', '.join(VALID_DOMAINS)}

Examples:
  bhdownloader https://fuckingfast.net/abc123xyz456
  bhdownloader abc123xyz456
  bhdownloader -f urls.txt -o ./downloads
  bhdownloader -f urls.txt -p 3 -o ./downloads
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "url",
        nargs="?",
        help="URL or file ID to download",
    )
    
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing URLs or IDs (one per line)",
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        metavar="DIR",
        help="Output directory for downloaded files (default: current directory)",
    )
    
    parser.add_argument(
        "-p", "--parallel",
        type=int,
        default=1,
        metavar="N",
        help="Number of parallel downloads (default: 1)",
    )
    
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=30,
        metavar="SECONDS",
        help="Request timeout in seconds (default: 30)",
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress output except errors",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose/debug output",
    )
    
    parser.add_argument(
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


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose, quiet=args.quiet)
    
    # Show banner
    if not args.quiet and not args.no_banner:
        print_banner()
    
    # Validate arguments
    if not args.url and not args.file:
        parser.print_help()
        print("\nError: Please provide a URL, file ID, or use -f to specify a file.")
        return 1
    
    if args.url and args.file:
        print("Error: Cannot use both URL argument and -f option together.", file=sys.stderr)
        return 1
    
    # Download from file
    if args.file:
        success, failure = download_from_file(
            file_path=args.file,
            output_dir=args.output_dir,
            parallel=args.parallel,
            quiet=args.quiet,
            timeout=args.timeout,
        )
        
        if not args.quiet:
            print(f"\nCompleted: {success} succeeded, {failure} failed")
        
        return 0 if failure == 0 else 1
    
    # Download single URL/ID
    if download_single(
        input_str=args.url,
        output_dir=args.output_dir,
        quiet=args.quiet,
        timeout=args.timeout,
    ):
        return 0
    else:
        return 1


def cli() -> None:
    """Entry point that exits with appropriate code."""
    sys.exit(main())


if __name__ == "__main__":
    cli()
