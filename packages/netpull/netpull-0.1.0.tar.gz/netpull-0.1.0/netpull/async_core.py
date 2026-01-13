"""Asynchronous webpage extraction engine for netpull"""

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Optional, Callable
import asyncio
import logging

from netpull.config import ExtractionConfig, BrowserConfig
from netpull.result import ExtractionResult
from netpull.exceptions import NavigationError, ExtractionError
from netpull.cookie_handler import handle_cookie_consent_async
from netpull.extractors import (
    extract_structured_data, clean_html, extract_images,
    extract_tables, extract_forms, extract_metadata
)
from netpull.utils import generate_filename

logger = logging.getLogger(__name__)


async def extract_webpage_async(
    url: str,
    extraction_config: Optional[ExtractionConfig] = None,
    browser_config: Optional[BrowserConfig] = None
) -> ExtractionResult:
    """Extract webpage content asynchronously

    Workflow:
    1. Launch browser
    2. Navigate to URL
    3. Wait for network idle
    4. Handle cookie consent
    5. Scroll to bottom for lazy-loaded content
    6. Take screenshot
    7. Extract HTML content
    8. Parse and extract structured data
    9. Save files
    10. Close browser

    Args:
        url: URL to extract
        extraction_config: Extraction configuration (uses default if None)
        browser_config: Browser configuration (uses default if None)

    Returns:
        ExtractionResult with paths and structured data

    Example:
        >>> import asyncio
        >>> result = asyncio.run(extract_webpage_async('https://example.com'))
        >>> print(result.screenshot_path)
        ./extracted/example_com_20260104_143022.png
    """
    # Use defaults if not provided
    if extraction_config is None:
        extraction_config = ExtractionConfig()
    if browser_config is None:
        browser_config = BrowserConfig()

    # Validate configs
    extraction_config.validate()
    browser_config.validate()

    result = ExtractionResult(url=url, success=False)

    try:
        async with async_playwright() as p:
            # Launch browser
            browser_type = getattr(p, browser_config.browser_type)
            browser = await browser_type.launch(headless=browser_config.headless)

            try:
                # Create page with viewport
                page = await browser.new_page(
                    viewport={
                        'width': browser_config.viewport_width,
                        'height': browser_config.viewport_height
                    },
                    user_agent=browser_config.user_agent
                )

                # Navigate
                logger.info(f"Navigating to {url}")
                await page.goto(url, timeout=browser_config.timeout)

                # Wait for network idle
                if extraction_config.wait_for_networkidle:
                    await page.wait_for_load_state('networkidle', timeout=browser_config.timeout)

                # Handle cookie consent
                if extraction_config.handle_cookie_consent:
                    await handle_cookie_consent_async(page, extraction_config.cookie_consent_timeout)

                # Scroll to bottom for lazy-loaded content
                if extraction_config.scroll_to_bottom:
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(extraction_config.wait_for_timeout)

                # Wait for specific selector if provided
                if extraction_config.wait_for_selector:
                    await page.wait_for_selector(extraction_config.wait_for_selector, timeout=browser_config.timeout)

                # Generate base filename
                base_filename = generate_filename(url, extraction_config.filename_pattern)

                # Take screenshot
                if extraction_config.extract_screenshot:
                    screenshot_path = extraction_config.output_dir / f"{base_filename}.png"
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    result.screenshot_path = screenshot_path
                    logger.info(f"Screenshot saved: {screenshot_path}")

                # Get HTML content
                html_content = await page.content()

                # Parse with BeautifulSoup (synchronous, no await needed)
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract structured data (synchronous, shared with sync version)
                result.structured_data = extract_structured_data(soup)

                # Extract images if requested
                if extraction_config.extract_images:
                    result.images = extract_images(soup)

                # Extract tables if requested
                if extraction_config.extract_tables:
                    result.tables = extract_tables(soup)

                # Extract forms if requested
                if extraction_config.extract_forms:
                    result.forms = extract_forms(soup)

                # Extract metadata if requested
                if extraction_config.extract_metadata:
                    result.metadata = extract_metadata(soup)

                # Save HTML if requested
                if extraction_config.extract_html:
                    # Clean HTML (synchronous)
                    cleaned_soup = clean_html(
                        soup,
                        remove_scripts=extraction_config.remove_scripts,
                        remove_styles=extraction_config.remove_styles,
                        remove_meta=extraction_config.remove_meta,
                        remove_links=extraction_config.remove_links
                    )

                    html_path = extraction_config.output_dir / f"{base_filename}.html"
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(str(cleaned_soup))
                    result.html_path = html_path
                    logger.info(f"HTML saved: {html_path}")

                result.success = True
                logger.info(f"Successfully extracted {url}")

            finally:
                await browser.close()

    except PlaywrightTimeout as e:
        result.error = f"Navigation timeout: {e}"
        logger.error(result.error)
    except Exception as e:
        result.error = f"Extraction failed: {e}"
        logger.error(result.error)

    return result


async def extract_batch_async(
    urls: List[str],
    extraction_config: Optional[ExtractionConfig] = None,
    browser_config: Optional[BrowserConfig] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> List[ExtractionResult]:
    """Extract multiple webpages asynchronously with concurrency control

    Uses asyncio.gather() with Semaphore for concurrent extraction
    with controlled concurrency.

    Args:
        urls: List of URLs to extract
        extraction_config: Extraction configuration (uses default if None)
        browser_config: Browser configuration (uses default if None)
        progress_callback: Optional callback function(current, total, url)

    Returns:
        List of ExtractionResult objects (one per URL)

    Example:
        >>> import asyncio
        >>> urls = ['https://example.com', 'https://github.com']
        >>> def progress(current, total, url):
        >>>     print(f"[{current}/{total}] {url}")
        >>> results = asyncio.run(extract_batch_async(urls, progress_callback=progress))
        >>> successful = sum(1 for r in results if r.success)
        >>> print(f"{successful}/{len(results)} succeeded")
    """
    if extraction_config is None:
        extraction_config = ExtractionConfig()

    semaphore = asyncio.Semaphore(extraction_config.batch_concurrency)
    total = len(urls)
    completed = 0

    async def extract_with_semaphore(url: str) -> ExtractionResult:
        """Extract single URL with semaphore control"""
        nonlocal completed
        async with semaphore:
            result = await extract_webpage_async(url, extraction_config, browser_config)
            completed += 1

            if progress_callback:
                progress_callback(completed, total, url)

            # Delay between requests
            if extraction_config.batch_delay > 0 and completed < total:
                await asyncio.sleep(extraction_config.batch_delay)

            return result

    # Execute all extractions concurrently (with semaphore limit)
    results = await asyncio.gather(
        *[extract_with_semaphore(url) for url in urls],
        return_exceptions=True
    )

    # Convert exceptions to failed results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append(ExtractionResult(url=urls[i], success=False, error=str(result)))
        else:
            processed_results.append(result)

    return processed_results
