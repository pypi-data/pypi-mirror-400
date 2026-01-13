"""Utility functions for netpull"""

import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import urlparse


def generate_filename(url: str, pattern: str) -> str:
    """Generate filename from URL and pattern

    Supports the following tokens:
    - {domain}: Domain name with dots and colons replaced by underscores
    - {timestamp}: Current timestamp (YYYYMMDD_HHMMSS)
    - {url_hash}: MD5 hash of URL (first 8 characters)
    - {date}: Current date (YYYY-MM-DD)
    - {time}: Current time (HHMMSS)

    Args:
        url: URL to extract domain from
        pattern: Filename pattern with tokens

    Returns:
        Generated filename (sanitized)

    Example:
        >>> generate_filename('https://example.com/page', '{domain}_{timestamp}')
        'example_com_20260104_143022'
    """
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '_').replace(':', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H%M%S')

    filename = pattern.format(
        domain=domain,
        timestamp=timestamp,
        url_hash=url_hash,
        date=date,
        time=time
    )

    # Sanitize filename - replace invalid characters with underscore
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    return filename


def is_valid_url(url: str) -> bool:
    """Validate URL format

    Args:
        url: URL to validate

    Returns:
        True if URL is valid (http/https with netloc), False otherwise

    Example:
        >>> is_valid_url('https://example.com')
        True
        >>> is_valid_url('not-a-url')
        False
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False


def parse_url_file(filepath: Path) -> List[str]:
    """Read URLs from file (one per line)

    Lines starting with # are treated as comments and ignored.
    Empty lines are ignored.

    Args:
        filepath: Path to file containing URLs

    Returns:
        List of URLs

    Example:
        >>> parse_url_file(Path('urls.txt'))
        ['https://example.com', 'https://github.com']
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return urls
