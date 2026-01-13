"""Configuration dataclasses for netpull"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional, List


@dataclass
class BrowserConfig:
    """Browser configuration for Playwright

    Attributes:
        browser_type: Browser to use (firefox, chrome, or webkit)
        headless: Run browser in headless mode
        timeout: Navigation timeout in milliseconds
        viewport_width: Browser viewport width
        viewport_height: Browser viewport height
        user_agent: Custom user agent string (None = default)
        args: Additional browser launch arguments
    """
    browser_type: Literal['firefox', 'chrome', 'webkit'] = 'firefox'
    headless: bool = True
    timeout: int = 30000  # milliseconds
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    args: List[str] = field(default_factory=list)

    def validate(self):
        """Validate configuration

        Raises:
            ValueError: If configuration is invalid
        """
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.viewport_width <= 0 or self.viewport_height <= 0:
            raise ValueError("Viewport dimensions must be positive")
        if self.browser_type not in ['firefox', 'chrome', 'webkit']:
            raise ValueError(f"Invalid browser: {self.browser_type}. Must be firefox, chrome, or webkit")


@dataclass
class ExtractionConfig:
    """Extraction configuration

    Attributes:
        output_dir: Directory for output files
        filename_pattern: Pattern for generated filenames (supports {domain}, {timestamp}, {url_hash}, {date}, {time})
        extract_screenshot: Capture screenshot
        extract_html: Save HTML content
        extract_images: Extract and save images
        extract_tables: Extract tables as structured data
        extract_forms: Extract form structures
        extract_metadata: Extract OpenGraph and Twitter Card metadata
        wait_for_networkidle: Wait for network to be idle
        wait_for_timeout: Additional wait timeout in milliseconds
        wait_for_selector: Wait for specific CSS selector
        scroll_to_bottom: Scroll to bottom for lazy-loaded content
        handle_cookie_consent: Try to handle cookie consent popups
        cookie_consent_timeout: Timeout for cookie consent handling in milliseconds
        remove_scripts: Remove script tags from HTML
        remove_styles: Remove style tags from HTML
        remove_meta: Remove meta tags from HTML
        remove_links: Remove link tags from HTML
        retry_count: Number of retries on failure
        retry_delay: Delay between retries in seconds
        batch_concurrency: Maximum concurrent extractions in batch mode
        batch_delay: Delay between batch requests in seconds
    """
    # Output
    output_dir: Path = Path('./extracted')
    filename_pattern: str = '{domain}_{timestamp}'

    # Extraction toggles
    extract_screenshot: bool = True
    extract_html: bool = True
    extract_images: bool = False
    extract_tables: bool = False
    extract_forms: bool = False
    extract_metadata: bool = False

    # Navigation
    wait_for_networkidle: bool = True
    wait_for_timeout: int = 1000  # ms
    wait_for_selector: Optional[str] = None
    scroll_to_bottom: bool = True

    # Cookie consent
    handle_cookie_consent: bool = True
    cookie_consent_timeout: int = 2000

    # Content cleaning
    remove_scripts: bool = True
    remove_styles: bool = True
    remove_meta: bool = True
    remove_links: bool = False

    # Retry
    retry_count: int = 0
    retry_delay: int = 5  # seconds

    # Batch
    batch_concurrency: int = 3
    batch_delay: float = 0  # seconds

    def validate(self):
        """Validate configuration and create output directory

        Raises:
            ValueError: If configuration is invalid
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if self.wait_for_timeout < 0:
            raise ValueError("wait_for_timeout must be non-negative")
        if self.cookie_consent_timeout < 0:
            raise ValueError("cookie_consent_timeout must be non-negative")
        if self.retry_count < 0:
            raise ValueError("retry_count must be non-negative")
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")
        if self.batch_concurrency < 1:
            raise ValueError("batch_concurrency must be at least 1")
        if self.batch_delay < 0:
            raise ValueError("batch_delay must be non-negative")
