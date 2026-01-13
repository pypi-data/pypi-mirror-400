"""Command-line interface for netpull"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import List

from netpull import __version__
from netpull.core import extract_webpage, extract_batch
from netpull.config import ExtractionConfig, BrowserConfig
from netpull.utils import is_valid_url, parse_url_file


def setup_logging(verbose: bool):
    """Setup logging configuration

    Args:
        verbose: Enable debug level logging if True
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def parse_args():
    """Parse command-line arguments

    Returns:
        Namespace with parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='NetPull - Web content extraction tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  netpull https://example.com
  netpull -f urls.txt --browser chrome
  netpull url1 url2 url3 --extract-all
  netpull https://example.com -o ./output --filename-pattern {domain}_{date}

Filename pattern tokens:
  {domain}     - Domain name (e.g., example_com)
  {timestamp}  - Current timestamp (YYYYMMDD_HHMMSS)
  {url_hash}   - MD5 hash of URL (first 8 chars)
  {date}       - Current date (YYYY-MM-DD)
  {time}       - Current time (HHMMSS)
        '''
    )

    # Version
    parser.add_argument('--version', action='version', version=f'netpull {__version__}')

    # URLs
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument('urls', nargs='*', default=[], help='URL(s) to extract')
    url_group.add_argument('-f', '--file', type=Path, help='File containing URLs (one per line)')

    # Browser options
    browser_group = parser.add_argument_group('Browser Options')
    browser_group.add_argument('--browser', choices=['firefox', 'chrome', 'webkit'],
                               default='firefox', help='Browser to use (default: firefox)')
    browser_group.add_argument('--headless', dest='headless', action='store_true', default=True,
                               help='Run browser in headless mode (default)')
    browser_group.add_argument('--no-headless', dest='headless', action='store_false',
                               help='Run browser with GUI')
    browser_group.add_argument('--timeout', type=int, default=30,
                               help='Navigation timeout in seconds (default: 30)')
    browser_group.add_argument('--user-agent', type=str, help='Custom user agent string')

    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('-o', '--output-dir', type=Path, default=Path('./extracted'),
                             help='Output directory (default: ./extracted)')
    output_group.add_argument('--filename-pattern', default='{domain}_{timestamp}',
                             help='Filename pattern (default: {domain}_{timestamp})')
    output_group.add_argument('--output-format', choices=['text', 'json'], default='text',
                             help='Output format for CLI (default: text)')

    # Extraction options
    extraction_group = parser.add_argument_group('Extraction Options')
    extraction_group.add_argument('--extract-images', action='store_true',
                                 help='Extract and save images')
    extraction_group.add_argument('--extract-tables', action='store_true',
                                 help='Extract tables as structured data')
    extraction_group.add_argument('--extract-forms', action='store_true',
                                 help='Extract form structures')
    extraction_group.add_argument('--extract-metadata', action='store_true',
                                 help='Extract OpenGraph and Twitter Card metadata')
    extraction_group.add_argument('--extract-all', action='store_true',
                                 help='Enable all extraction features')
    extraction_group.add_argument('--no-screenshot', dest='extract_screenshot', action='store_false', default=True,
                                 help='Disable screenshot capture')
    extraction_group.add_argument('--no-html', dest='extract_html', action='store_false', default=True,
                                 help='Disable HTML saving')

    # Navigation options
    nav_group = parser.add_argument_group('Navigation Options')
    nav_group.add_argument('--wait-for-selector', type=str,
                          help='Wait for specific CSS selector before extraction')
    nav_group.add_argument('--wait-for-timeout', type=int, default=1000,
                          help='Wait timeout in milliseconds (default: 1000)')
    nav_group.add_argument('--no-scroll', dest='scroll_to_bottom', action='store_false', default=True,
                          help='Disable scroll to bottom')
    nav_group.add_argument('--no-cookie-consent', dest='handle_cookie_consent', action='store_false', default=True,
                          help='Disable automatic cookie consent handling')

    # Retry options
    retry_group = parser.add_argument_group('Retry Options')
    retry_group.add_argument('--retry', type=int, default=0,
                            help='Number of retries on failure (default: 0)')
    retry_group.add_argument('--retry-delay', type=int, default=5,
                            help='Delay between retries in seconds (default: 5)')

    # Batch options
    batch_group = parser.add_argument_group('Batch Processing Options')
    batch_group.add_argument('--concurrency', type=int, default=3,
                            help='Max concurrent extractions (default: 3)')
    batch_group.add_argument('--delay', type=float, default=0,
                            help='Delay between requests in seconds (default: 0)')

    # Misc options
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Validate URLs argument
    if not args.file and not args.urls:
        parser.error("Either provide URLs as arguments or use -f/--file option")

    return args


def progress_callback(current: int, total: int, url: str):
    """Progress callback for batch processing

    Args:
        current: Current completion count
        total: Total URL count
        url: Current URL being processed
    """
    print(f"[{current}/{total}] {url}", file=sys.stderr)


def main():
    """Main CLI entry point

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Get URLs
    if args.file:
        try:
            urls = parse_url_file(args.file)
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error reading file {args.file}: {e}", file=sys.stderr)
            return 1
    else:
        urls = args.urls

    # Validate URLs
    invalid_urls = [url for url in urls if not is_valid_url(url)]
    if invalid_urls:
        print(f"Error: Invalid URLs: {', '.join(invalid_urls)}", file=sys.stderr)
        return 1

    if not urls:
        print("Error: No URLs to process", file=sys.stderr)
        return 1

    # Build configurations
    browser_config = BrowserConfig(
        browser_type=args.browser,
        headless=args.headless,
        timeout=args.timeout * 1000,  # Convert to milliseconds
        user_agent=args.user_agent
    )

    extraction_config = ExtractionConfig(
        output_dir=args.output_dir,
        filename_pattern=args.filename_pattern,
        extract_screenshot=args.extract_screenshot,
        extract_html=args.extract_html,
        extract_images=args.extract_all or args.extract_images,
        extract_tables=args.extract_all or args.extract_tables,
        extract_forms=args.extract_all or args.extract_forms,
        extract_metadata=args.extract_all or args.extract_metadata,
        wait_for_selector=args.wait_for_selector,
        wait_for_timeout=args.wait_for_timeout,
        scroll_to_bottom=args.scroll_to_bottom,
        handle_cookie_consent=args.handle_cookie_consent,
        retry_count=args.retry,
        retry_delay=args.retry_delay,
        batch_concurrency=args.concurrency,
        batch_delay=args.delay
    )

    # Validate configurations
    try:
        browser_config.validate()
        extraction_config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1

    # Extract
    try:
        if len(urls) == 1:
            result = extract_webpage(urls[0], extraction_config, browser_config)
            results = [result]
        else:
            results = extract_batch(urls, extraction_config, browser_config, progress_callback)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    # Output results
    if args.output_format == 'json':
        output = [r.to_dict() for r in results]
        print(json.dumps(output, indent=2))
    else:
        for result in results:
            print(result)

    # Exit code
    failed = sum(1 for r in results if not r.success)
    successful = len(results) - failed

    if len(results) > 1:
        print(f"\nSummary: {successful}/{len(results)} successful, {failed}/{len(results)} failed",
              file=sys.stderr)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
