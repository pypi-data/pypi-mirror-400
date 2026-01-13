# NetPull

**Web content extraction with screenshots and structured data**

NetPull is a Python package for extracting web content including full-page screenshots, HTML, and structured data (headings, paragraphs, links, tables, forms, metadata). Built on Playwright for reliable cross-browser automation.

## Features

- 📸 **Full-page screenshots** - Capture entire webpages including lazy-loaded content
- 📄 **HTML extraction** - Save cleaned HTML without scripts/styles
- 🔍 **Structured data** - Extract titles, headings, paragraphs, and links
- 📊 **Advanced extraction** - Tables, forms, images, and metadata (OpenGraph, Twitter Cards)
- 🌐 **Multi-browser** - Firefox, Chrome, and WebKit support
- 🍪 **Cookie consent** - Automatic handling of cookie popups
- ⚡ **Async support** - Both synchronous and asynchronous APIs
- 🔄 **Batch processing** - Extract multiple URLs with concurrency control
- 🎯 **CLI & Library** - Use as command-line tool or Python library

## Installation

```bash
pip install netpull
```

After installation, install Playwright browsers:

```bash
playwright install firefox
# or
playwright install chrome webkit
```

## Quick Start

### Command Line

```bash
# Extract single URL
netpull https://example.com

# Extract with all features
netpull https://example.com --extract-all

# Batch extraction from file
netpull -f urls.txt --browser chrome --concurrency 5

# Custom output directory
netpull https://example.com -o ./my-output --filename-pattern {domain}_{date}
```

### Python Library

```python
from netpull import extract_webpage

# Basic extraction
result = extract_webpage('https://example.com')
print(result.screenshot_path)  # ./extracted/example_com_20260104_143022.png
print(result.structured_data['title'])  # Page title
```

### Async Usage

```python
import asyncio
from netpull import extract_webpage_async

async def main():
    result = await extract_webpage_async('https://example.com')
    print(result.structured_data)

asyncio.run(main())
```

## Usage Examples

### Advanced Configuration

```python
from netpull import extract_webpage, ExtractionConfig, BrowserConfig
from pathlib import Path

# Configure browser
browser_config = BrowserConfig(
    browser_type='chrome',
    headless=True,
    timeout=60000  # 60 seconds
)

# Configure extraction
extraction_config = ExtractionConfig(
    output_dir=Path('./output'),
    filename_pattern='{domain}_{timestamp}',
    extract_images=True,
    extract_tables=True,
    extract_forms=True,
    extract_metadata=True,
    scroll_to_bottom=True,
    handle_cookie_consent=True
)

result = extract_webpage(
    'https://example.com',
    extraction_config=extraction_config,
    browser_config=browser_config
)
```

### Batch Processing

```python
from netpull import extract_batch

urls = [
    'https://example.com',
    'https://github.com',
    'https://python.org'
]

def progress(current, total, url):
    print(f"[{current}/{total}] Processing {url}")

results = extract_batch(urls, progress_callback=progress)

# Check results
for result in results:
    if result.success:
        print(f"✓ {result.url}: {result.screenshot_path}")
    else:
        print(f"✗ {result.url}: {result.error}")
```

### Extract Specific Content

```python
from netpull import extract_webpage, ExtractionConfig

config = ExtractionConfig(
    extract_images=True,
    extract_tables=True,
    extract_metadata=True
)

result = extract_webpage('https://example.com', extraction_config=config)

# Access extracted data
print(f"Found {len(result.images)} images")
print(f"Found {len(result.tables)} tables")
print(f"OpenGraph title: {result.metadata['opengraph'].get('og:title', 'N/A')}")
```

## CLI Reference

### Basic Usage

```bash
netpull URL [URL ...]
netpull -f FILE
```

### Browser Options

- `--browser {firefox,chrome,webkit}` - Browser to use (default: firefox)
- `--headless` / `--no-headless` - Headless mode (default: headless)
- `--timeout SECONDS` - Navigation timeout (default: 30)
- `--user-agent STRING` - Custom user agent

### Output Options

- `-o DIR` / `--output-dir DIR` - Output directory (default: ./extracted)
- `--filename-pattern PATTERN` - Filename pattern (default: {domain}_{timestamp})
- `--output-format {text,json}` - CLI output format

### Extraction Options

- `--extract-images` - Extract images
- `--extract-tables` - Extract tables
- `--extract-forms` - Extract forms
- `--extract-metadata` - Extract metadata
- `--extract-all` - Enable all extraction features
- `--no-screenshot` - Disable screenshot
- `--no-html` - Disable HTML saving

### Navigation Options

- `--wait-for-selector SELECTOR` - Wait for CSS selector
- `--wait-for-timeout MS` - Wait timeout (default: 1000)
- `--no-scroll` - Disable scroll to bottom
- `--no-cookie-consent` - Disable cookie consent handling

### Batch Options

- `--concurrency N` - Max concurrent extractions (default: 3)
- `--delay SECONDS` - Delay between requests (default: 0)

### Other Options

- `--retry N` - Retry count on failure (default: 0)
- `--retry-delay SECONDS` - Delay between retries (default: 5)
- `-v` / `--verbose` - Verbose output
- `--version` - Show version

## Filename Patterns

Use tokens in `--filename-pattern`:

- `{domain}` - Domain name (example_com)
- `{timestamp}` - Current timestamp (20260104_143022)
- `{url_hash}` - MD5 hash of URL (first 8 chars)
- `{date}` - Current date (2026-01-04)
- `{time}` - Current time (143022)

Example:
```bash
netpull https://example.com --filename-pattern "{domain}_{date}"
# Output: example_com_2026-01-04.png
```

## Configuration Classes

### BrowserConfig

```python
from netpull import BrowserConfig

config = BrowserConfig(
    browser_type='firefox',  # 'firefox', 'chrome', or 'webkit'
    headless=True,           # Run without GUI
    timeout=30000,           # Navigation timeout (ms)
    viewport_width=1920,     # Browser width
    viewport_height=1080,    # Browser height
    user_agent=None          # Custom user agent
)
```

### ExtractionConfig

```python
from netpull import ExtractionConfig
from pathlib import Path

config = ExtractionConfig(
    # Output
    output_dir=Path('./extracted'),
    filename_pattern='{domain}_{timestamp}',

    # Extraction toggles
    extract_screenshot=True,
    extract_html=True,
    extract_images=False,
    extract_tables=False,
    extract_forms=False,
    extract_metadata=False,

    # Navigation
    wait_for_networkidle=True,
    wait_for_timeout=1000,
    wait_for_selector=None,
    scroll_to_bottom=True,

    # Cookie consent
    handle_cookie_consent=True,
    cookie_consent_timeout=2000,

    # Batch
    batch_concurrency=3,
    batch_delay=0
)
```

## Result Object

The `ExtractionResult` object contains:

```python
result = extract_webpage('https://example.com')

result.url                  # URL that was extracted
result.success             # True if successful, False otherwise
result.error               # Error message if failed
result.screenshot_path     # Path to screenshot (Path object)
result.html_path          # Path to HTML file (Path object)
result.structured_data    # Dict with title, main_content, links
result.images             # List of image data
result.tables             # List of table data
result.forms              # List of form data
result.metadata           # Dict with opengraph, twitter, json_ld

# Convert to dictionary for JSON
result.to_dict()

# String representation
print(result)
# ✓ https://example.com
#   Screenshot: ./extracted/example_com_20260104_143022.png
#   HTML: ./extracted/example_com_20260104_143022.html
```

## Troubleshooting

### Playwright browsers not installed

```bash
playwright install firefox
# or install all browsers
playwright install
```

### Timeout errors

Increase timeout in browser config:

```python
browser_config = BrowserConfig(timeout=60000)  # 60 seconds
```

Or via CLI:

```bash
netpull https://example.com --timeout 60
```

### Cookie consent not handled

The package tries 11 common selectors. For sites with unusual cookie popups, disable auto-handling:

```bash
netpull https://example.com --no-cookie-consent
```

### Memory issues with large batches

Reduce concurrency:

```bash
netpull -f urls.txt --concurrency 1
```

## Development

### Install for development

```bash
git clone https://github.com/netpull/netpull.git
cd netpull
pip install -e ".[dev]"
playwright install firefox
```

### Run tests

```bash
pytest tests/ -v
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

Built with:
- [Playwright](https://playwright.dev/) - Browser automation
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

---

**NetPull** - Simple, powerful web content extraction
