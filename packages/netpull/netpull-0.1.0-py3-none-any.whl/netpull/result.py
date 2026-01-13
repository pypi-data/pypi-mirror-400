"""Result encapsulation for netpull extractions"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Dict, List, Any


@dataclass
class ExtractionResult:
    """Encapsulates webpage extraction results

    Attributes:
        url: URL that was extracted
        success: True if extraction succeeded, False otherwise
        screenshot_path: Path to screenshot file (if extracted)
        html_path: Path to HTML file (if extracted)
        structured_data: Structured content (title, headings, paragraphs, links)
        images: List of image data (if extracted)
        tables: List of table data (if extracted)
        forms: List of form data (if extracted)
        metadata: OpenGraph and Twitter Card metadata (if extracted)
        error: Error message if extraction failed

    Example:
        >>> result = ExtractionResult(url='https://example.com', success=True)
        >>> result.screenshot_path = Path('./screenshot.png')
        >>> print(result)
        ✓ https://example.com
          Screenshot: ./screenshot.png
    """
    url: str
    success: bool
    screenshot_path: Optional[Path] = None
    html_path: Optional[Path] = None
    structured_data: Dict[str, Any] = field(default_factory=dict)
    images: List[Dict[str, str]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization

        Converts Path objects to strings for JSON compatibility.

        Returns:
            Dictionary representation of the result

        Example:
            >>> result = ExtractionResult(url='https://example.com', success=True)
            >>> result.screenshot_path = Path('./screenshot.png')
            >>> d = result.to_dict()
            >>> d['screenshot_path']
            './screenshot.png'
        """
        result = asdict(self)

        # Convert Path objects to strings
        if self.screenshot_path:
            result['screenshot_path'] = str(self.screenshot_path)
        if self.html_path:
            result['html_path'] = str(self.html_path)

        return result

    def __str__(self) -> str:
        """Human-readable string representation

        Returns:
            Multi-line string with key information

        Example:
            >>> result = ExtractionResult(url='https://example.com', success=True)
            >>> print(str(result))
            ✓ https://example.com
              Screenshot: None
              HTML: None
        """
        if self.success:
            lines = [f"✓ {self.url}"]
            if self.screenshot_path:
                lines.append(f"  Screenshot: {self.screenshot_path}")
            if self.html_path:
                lines.append(f"  HTML: {self.html_path}")
            if self.images:
                lines.append(f"  Images: {len(self.images)}")
            if self.tables:
                lines.append(f"  Tables: {len(self.tables)}")
            if self.forms:
                lines.append(f"  Forms: {len(self.forms)}")
            return "\n".join(lines)
        else:
            return f"✗ {self.url}\n  Error: {self.error}"
