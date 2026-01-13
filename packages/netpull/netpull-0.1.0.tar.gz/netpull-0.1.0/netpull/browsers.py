"""Browser lifecycle management for netpull"""

from playwright.sync_api import sync_playwright, Browser, Playwright
from typing import Optional
import logging

from netpull.config import BrowserConfig
from netpull.exceptions import BrowserLaunchError

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages browser lifecycle (sync)

    Supports context manager protocol for automatic cleanup.

    Example:
        >>> config = BrowserConfig(browser_type='firefox', headless=True)
        >>> with BrowserManager(config) as browser:
        >>>     page = browser.new_page()
        >>>     page.goto('https://example.com')
    """

    def __init__(self, config: BrowserConfig):
        """Initialize browser manager

        Args:
            config: Browser configuration
        """
        self.config = config
        self.config.validate()
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    def __enter__(self):
        """Context manager entry - launch browser"""
        return self.launch()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close browser"""
        self.close()

    def launch(self) -> Browser:
        """Launch browser

        Returns:
            Browser instance

        Raises:
            BrowserLaunchError: If browser fails to launch
        """
        try:
            self._playwright = sync_playwright().start()

            browser_type = getattr(self._playwright, self.config.browser_type)
            self._browser = browser_type.launch(
                headless=self.config.headless,
                args=self.config.args
            )

            logger.info(f"Launched {self.config.browser_type} browser (headless={self.config.headless})")
            return self._browser

        except Exception as e:
            raise BrowserLaunchError(f"Failed to launch {self.config.browser_type} browser: {e}")

    def close(self):
        """Close browser and cleanup Playwright

        Handles exceptions gracefully to ensure cleanup proceeds.
        """
        try:
            if self._browser:
                self._browser.close()
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

        try:
            if self._playwright:
                self._playwright.stop()
        except Exception as e:
            logger.error(f"Error stopping Playwright: {e}")
