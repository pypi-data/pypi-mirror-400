"""Cookie consent handling for netpull

Implements automatic cookie consent detection and handling
based on common patterns found on websites.
"""

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from playwright.async_api import Page as AsyncPage
import logging

logger = logging.getLogger(__name__)

# Cookie consent selectors from extract_cleaner_webpage_sync.py
# Try these in order until one works
COOKIE_SELECTORS = [
    'button[id*="accept"]',          # ID containing "accept"
    'button[class*="accept"]',        # Class containing "accept"
    'button[aria-label*="Accept"]',   # Aria-label containing "Accept"
    'button:has-text("Accept")',      # Button with "Accept" text
    'button:has-text("I agree")',     # Button with "I agree" text
    'button:has-text("Allow all")',   # Button with "Allow all" text
    'a[id*="accept"]',               # Link with "accept" ID
    'a[class*="accept"]',             # Link with "accept" class
    'div[id*="accept"]',             # Div with "accept" ID
    'div[class*="accept"]',           # Div with "accept" class
    'button:has-text("OK")',          # Button with "OK" text
]


def handle_cookie_consent(page: Page, timeout: int = 2000) -> bool:
    """Try to click cookie consent button (sync version)

    Attempts to find and click a cookie consent button using common patterns.
    Tries each selector sequentially with a short timeout.

    Args:
        page: Playwright page object
        timeout: Timeout for each selector attempt in milliseconds (default: 2000)

    Returns:
        True if consent was handled (button found and clicked), False otherwise

    Example:
        >>> from playwright.sync_api import sync_playwright
        >>> with sync_playwright() as p:
        >>>     browser = p.firefox.launch()
        >>>     page = browser.new_page()
        >>>     page.goto('https://example.com')
        >>>     if handle_cookie_consent(page):
        >>>         print("Cookie consent handled")
    """
    for selector in COOKIE_SELECTORS:
        try:
            page.click(selector, timeout=timeout)
            logger.info(f"Cookie consent handled with selector: {selector}")
            return True
        except PlaywrightTimeout:
            # This selector didn't match, try next
            continue
        except Exception as e:
            # Other errors (element not clickable, etc.)
            logger.debug(f"Selector {selector} failed: {e}")
            continue

    logger.debug("No cookie consent button found")
    return False


async def handle_cookie_consent_async(page: AsyncPage, timeout: int = 2000) -> bool:
    """Try to click cookie consent button (async version)

    Attempts to find and click a cookie consent button using common patterns.
    Tries each selector sequentially with a short timeout.

    Args:
        page: Playwright async page object
        timeout: Timeout for each selector attempt in milliseconds (default: 2000)

    Returns:
        True if consent was handled (button found and clicked), False otherwise

    Example:
        >>> from playwright.async_api import async_playwright
        >>> async with async_playwright() as p:
        >>>     browser = await p.firefox.launch()
        >>>     page = await browser.new_page()
        >>>     await page.goto('https://example.com')
        >>>     if await handle_cookie_consent_async(page):
        >>>         print("Cookie consent handled")
    """
    for selector in COOKIE_SELECTORS:
        try:
            await page.click(selector, timeout=timeout)
            logger.info(f"Cookie consent handled with selector: {selector}")
            return True
        except PlaywrightTimeout:
            # This selector didn't match, try next
            continue
        except Exception as e:
            # Other errors (element not clickable, etc.)
            logger.debug(f"Selector {selector} failed: {e}")
            continue

    logger.debug("No cookie consent button found")
    return False
