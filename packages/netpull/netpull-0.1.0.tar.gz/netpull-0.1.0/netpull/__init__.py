"""NetPull - Web content extraction with screenshots and structured data"""

__version__ = "0.1.0"
__author__ = "NetPull Contributors"
__license__ = "MIT"

from netpull.config import ExtractionConfig, BrowserConfig
from netpull.result import ExtractionResult
from netpull.core import extract_webpage, extract_batch
from netpull.async_core import extract_webpage_async, extract_batch_async

__all__ = [
    'ExtractionConfig',
    'BrowserConfig',
    'ExtractionResult',
    'extract_webpage',
    'extract_batch',
    'extract_webpage_async',
    'extract_batch_async',
]
