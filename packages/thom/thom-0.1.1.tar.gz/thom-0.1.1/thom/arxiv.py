"""
arXiv paper fetching module.

Provides functionality to fetch and parse research papers from arXiv.
"""

import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional


@dataclass
class ArxivPaper:
    """Represents an arXiv paper with its metadata and content."""

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published: str
    updated: str
    pdf_url: str
    arxiv_url: str

    def __str__(self) -> str:
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += f" et al. ({len(self.authors)} authors)"
        return f"{self.title}\nby {authors_str}\narXiv:{self.arxiv_id}"


# arXiv API namespace
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


def extract_arxiv_id(identifier: str) -> str:
    """
    Extract arXiv ID from various input formats.

    Accepts:
    - Plain ID: "2301.00001" or "2301.00001v1"
    - URL: "https://arxiv.org/abs/2301.00001"
    - PDF URL: "https://arxiv.org/pdf/2301.00001.pdf"
    - Old format: "hep-th/9901001"

    Args:
        identifier: arXiv paper identifier in any supported format

    Returns:
        Normalized arXiv ID

    Raises:
        ValueError: If the identifier format is not recognized
    """
    identifier = identifier.strip()

    # Handle URLs
    url_patterns = [
        r"arxiv\.org/abs/([^\s/]+)",
        r"arxiv\.org/pdf/([^\s/]+?)(?:\.pdf)?$",
    ]
    for pattern in url_patterns:
        match = re.search(pattern, identifier)
        if match:
            return match.group(1)

    # Handle plain IDs (new format: YYMM.NNNNN or old format: category/YYMMNNN)
    id_patterns = [
        r"^(\d{4}\.\d{4,5}(?:v\d+)?)$",  # New format
        r"^([a-z-]+/\d{7}(?:v\d+)?)$",    # Old format
    ]
    for pattern in id_patterns:
        match = re.match(pattern, identifier, re.IGNORECASE)
        if match:
            return match.group(1)

    raise ValueError(
        f"Could not extract arXiv ID from: {identifier}. "
        "Expected formats: '2301.00001', 'https://arxiv.org/abs/2301.00001', "
        "or 'hep-th/9901001'"
    )


def fetch_paper(identifier: str) -> ArxivPaper:
    """
    Fetch a paper from arXiv by its identifier.

    Args:
        identifier: arXiv paper ID or URL

    Returns:
        ArxivPaper object with paper metadata

    Raises:
        ValueError: If the identifier is invalid or paper not found
    """
    arxiv_id = extract_arxiv_id(identifier)

    # Build API URL
    api_url = f"http://export.arxiv.org/api/query?id_list={urllib.parse.quote(arxiv_id)}"

    # Fetch from API
    try:
        with urllib.request.urlopen(api_url, timeout=30) as response:
            xml_data = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        raise ValueError(f"Failed to fetch paper from arXiv: {e}")

    # Parse XML response
    root = ET.fromstring(xml_data)

    # Find entry
    entry = root.find("atom:entry", ARXIV_NS)
    if entry is None:
        raise ValueError(f"Paper not found: {arxiv_id}")

    # Check for error
    title_elem = entry.find("atom:title", ARXIV_NS)
    if title_elem is not None and title_elem.text and "Error" in title_elem.text:
        raise ValueError(f"arXiv API error: {title_elem.text}")

    # Extract metadata
    title = _get_text(entry, "atom:title")
    if not title:
        raise ValueError(f"Paper not found or invalid response for: {arxiv_id}")

    # Clean up title (remove newlines and extra spaces)
    title = " ".join(title.split())

    abstract = _get_text(entry, "atom:summary")
    abstract = " ".join(abstract.split()) if abstract else ""

    published = _get_text(entry, "atom:published") or ""
    updated = _get_text(entry, "atom:updated") or ""

    # Get authors
    authors = []
    for author_elem in entry.findall("atom:author", ARXIV_NS):
        name = _get_text(author_elem, "atom:name")
        if name:
            authors.append(name)

    # Get categories
    categories = []
    for cat_elem in entry.findall("atom:category", ARXIV_NS):
        term = cat_elem.get("term")
        if term:
            categories.append(term)

    # Get links
    pdf_url = ""
    arxiv_url = ""
    for link_elem in entry.findall("atom:link", ARXIV_NS):
        href = link_elem.get("href", "")
        link_type = link_elem.get("type", "")
        if link_type == "application/pdf":
            pdf_url = href
        elif link_elem.get("rel") == "alternate":
            arxiv_url = href

    # Fallback URLs
    if not pdf_url:
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    if not arxiv_url:
        arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"

    return ArxivPaper(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors,
        abstract=abstract,
        categories=categories,
        published=published,
        updated=updated,
        pdf_url=pdf_url,
        arxiv_url=arxiv_url,
    )


def search_papers(
    query: str,
    max_results: int = 10,
    sort_by: str = "relevance",
    sort_order: str = "descending",
) -> list[ArxivPaper]:
    """
    Search for papers on arXiv.

    Args:
        query: Search query (supports arXiv search syntax)
        max_results: Maximum number of results to return (default: 10)
        sort_by: Sort criterion - "relevance", "lastUpdatedDate", or "submittedDate"
        sort_order: Sort order - "ascending" or "descending"

    Returns:
        List of ArxivPaper objects matching the query
    """
    # Build API URL
    params = {
        "search_query": query,
        "max_results": str(max_results),
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    api_url = f"http://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}"

    # Fetch from API
    try:
        with urllib.request.urlopen(api_url, timeout=30) as response:
            xml_data = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        raise ValueError(f"Failed to search arXiv: {e}")

    # Parse XML response
    root = ET.fromstring(xml_data)

    papers = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        try:
            # Extract ID from entry id URL
            id_elem = entry.find("atom:id", ARXIV_NS)
            if id_elem is None or not id_elem.text:
                continue

            arxiv_id = id_elem.text.split("/abs/")[-1]

            title = _get_text(entry, "atom:title")
            if not title:
                continue
            title = " ".join(title.split())

            abstract = _get_text(entry, "atom:summary")
            abstract = " ".join(abstract.split()) if abstract else ""

            published = _get_text(entry, "atom:published") or ""
            updated = _get_text(entry, "atom:updated") or ""

            authors = []
            for author_elem in entry.findall("atom:author", ARXIV_NS):
                name = _get_text(author_elem, "atom:name")
                if name:
                    authors.append(name)

            categories = []
            for cat_elem in entry.findall("atom:category", ARXIV_NS):
                term = cat_elem.get("term")
                if term:
                    categories.append(term)

            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"

            papers.append(ArxivPaper(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                abstract=abstract,
                categories=categories,
                published=published,
                updated=updated,
                pdf_url=pdf_url,
                arxiv_url=arxiv_url,
            ))
        except Exception:
            # Skip malformed entries
            continue

    return papers


def _get_text(element: ET.Element, path: str) -> Optional[str]:
    """Helper to get text content from an XML element."""
    child = element.find(path, ARXIV_NS)
    if child is not None and child.text:
        return child.text
    return None
