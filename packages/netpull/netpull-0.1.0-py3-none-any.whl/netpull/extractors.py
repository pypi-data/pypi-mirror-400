"""Content extraction functions for netpull

All functions in this module are synchronous and shared by both
sync and async extraction engines to avoid code duplication.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def extract_structured_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract structured content (title, headings, paragraphs, links)

    This function is synchronous and shared by both sync and async implementations.

    Args:
        soup: BeautifulSoup object of parsed HTML

    Returns:
        Dictionary with title, main_content (list of headings/paragraphs), and links

    Example:
        >>> html = '<html><title>Example</title><h1>Header</h1><p>Text</p></html>'
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> data = extract_structured_data(soup)
        >>> data['title']
        'Example'
        >>> len(data['main_content'])
        2
    """
    data = {}

    # Title
    if soup.title and soup.title.string:
        data['title'] = soup.title.string.strip()
    else:
        data['title'] = ''

    # Main content (headings and paragraphs)
    main_content = []
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p']):
        text = tag.get_text().strip()
        if text:
            main_content.append({
                'type': tag.name,
                'text': text
            })
    data['main_content'] = main_content

    # Links
    links = []
    for a_tag in soup.find_all('a', href=True):
        text = a_tag.get_text().strip()
        href = a_tag['href']
        if text and href:
            links.append({'text': text, 'href': href})
    data['links'] = links

    logger.debug(f"Extracted {len(main_content)} content items and {len(links)} links")
    return data


def clean_html(soup: BeautifulSoup,
               remove_scripts: bool = True,
               remove_styles: bool = True,
               remove_meta: bool = True,
               remove_links: bool = False) -> BeautifulSoup:
    """Clean HTML by removing unwanted tags

    This function modifies the soup in place.
    This is synchronous and shared by both sync and async implementations.

    Args:
        soup: BeautifulSoup object to clean
        remove_scripts: Remove <script> tags
        remove_styles: Remove <style> tags
        remove_meta: Remove <meta> tags
        remove_links: Remove <link> tags

    Returns:
        Modified BeautifulSoup object (same as input)

    Example:
        >>> html = '<html><script>alert(1)</script><p>Text</p></html>'
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> cleaned = clean_html(soup, remove_scripts=True)
        >>> 'script' in str(cleaned)
        False
    """
    removed_count = 0

    if remove_scripts:
        for script in soup.find_all('script'):
            script.decompose()
            removed_count += 1

    if remove_styles:
        for style in soup.find_all('style'):
            style.decompose()
            removed_count += 1

    if remove_meta:
        for meta in soup.find_all('meta'):
            meta.decompose()
            removed_count += 1

    if remove_links:
        for link in soup.find_all('link'):
            link.decompose()
            removed_count += 1

    logger.debug(f"Removed {removed_count} unwanted tags from HTML")
    return soup


def extract_images(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract image information

    Args:
        soup: BeautifulSoup object

    Returns:
        List of dictionaries with image data (src, alt, title)

    Example:
        >>> html = '<img src="image.jpg" alt="Description">'
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> images = extract_images(soup)
        >>> images[0]['src']
        'image.jpg'
    """
    images = []
    for img in soup.find_all('img'):
        img_data = {}
        if img.get('src'):
            img_data['src'] = img['src']
        if img.get('alt'):
            img_data['alt'] = img['alt']
        if img.get('title'):
            img_data['title'] = img['title']
        if img_data:
            images.append(img_data)

    logger.debug(f"Extracted {len(images)} images")
    return images


def extract_tables(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract tables as structured data

    Args:
        soup: BeautifulSoup object

    Returns:
        List of dictionaries with headers and rows

    Example:
        >>> html = '<table><tr><th>Name</th></tr><tr><td>John</td></tr></table>'
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> tables = extract_tables(soup)
        >>> tables[0]['headers']
        ['Name']
    """
    tables = []
    for table in soup.find_all('table'):
        table_data = {'headers': [], 'rows': []}

        # Extract headers
        headers = table.find_all('th')
        table_data['headers'] = [h.get_text().strip() for h in headers]

        # Extract rows
        for tr in table.find_all('tr'):
            cells = tr.find_all(['td', 'th'])
            if cells:
                row = [cell.get_text().strip() for cell in cells]
                table_data['rows'].append(row)

        tables.append(table_data)

    logger.debug(f"Extracted {len(tables)} tables")
    return tables


def extract_forms(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract form structures

    Args:
        soup: BeautifulSoup object

    Returns:
        List of dictionaries with form data (action, method, inputs)

    Example:
        >>> html = '<form action="/submit" method="post"><input name="email" type="text"></form>'
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> forms = extract_forms(soup)
        >>> forms[0]['action']
        '/submit'
    """
    forms = []
    for form in soup.find_all('form'):
        form_data = {
            'action': form.get('action', ''),
            'method': form.get('method', 'get'),
            'inputs': []
        }

        # Extract inputs
        for input_tag in form.find_all(['input', 'textarea', 'select']):
            input_data = {
                'tag': input_tag.name,
                'type': input_tag.get('type', ''),
                'name': input_tag.get('name', ''),
                'value': input_tag.get('value', ''),
                'placeholder': input_tag.get('placeholder', '')
            }
            form_data['inputs'].append(input_data)

        forms.append(form_data)

    logger.debug(f"Extracted {len(forms)} forms")
    return forms


def extract_metadata(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract OpenGraph, Twitter Cards, and JSON-LD metadata

    Args:
        soup: BeautifulSoup object

    Returns:
        Dictionary with opengraph, twitter, and json_ld data

    Example:
        >>> html = '<meta property="og:title" content="Example Page">'
        >>> soup = BeautifulSoup(html, 'html.parser')
        >>> metadata = extract_metadata(soup)
        >>> metadata['opengraph']['og:title']
        'Example Page'
    """
    metadata = {}

    # OpenGraph tags (property starts with "og:")
    og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
    metadata['opengraph'] = {tag['property']: tag.get('content', '') for tag in og_tags}

    # Twitter Card tags (name starts with "twitter:")
    twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
    metadata['twitter'] = {tag['name']: tag.get('content', '') for tag in twitter_tags}

    # JSON-LD structured data
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    metadata['json_ld'] = [script.string for script in json_ld_scripts if script.string]

    logger.debug(f"Extracted metadata: {len(metadata['opengraph'])} OG tags, "
                f"{len(metadata['twitter'])} Twitter tags, {len(metadata['json_ld'])} JSON-LD")
    return metadata
