"""
thom - Summarize research papers from arXiv using LLMs.

Named after René Thom (1923-2002), the French mathematician who founded
catastrophe theory and won the Fields Medal in 1958.

Example usage:
    >>> import thom
    >>> paper = thom.fetch_paper("2301.00001")
    >>> summary = thom.summarize(paper)
    >>> print(summary)

CLI usage:
    $ thom summarize 2301.00001
    $ thom search "machine learning"
    $ thom compare 2301.00001 2301.00002
"""

__version__ = "0.1.0"
__author__ = "thom contributors"

from .arxiv import (
    ArxivPaper,
    fetch_paper,
    search_papers,
    extract_arxiv_id,
)

from .summarizer import (
    Summary,
    summarize_paper,
    summarize_papers,
    compare_papers,
    set_api_key,
    list_supported_models,
)


# Convenient aliases for the main functions
def summarize(
    paper: ArxivPaper,
    model: str = "gpt-4o-mini",
    detail_level: str = "medium",
    language: str = "english",
    **kwargs,
) -> Summary:
    """
    Summarize an arXiv paper.

    Args:
        paper: ArxivPaper object (from fetch_paper or search)
        model: LiteLLM model identifier (default: "gpt-4o-mini")
            Examples: "gpt-4o", "claude-3-sonnet-20240229", "ollama/llama2"
        detail_level: "brief", "medium", or "detailed"
        language: Output language (default: "english")
        **kwargs: Additional arguments for LiteLLM

    Returns:
        Summary object with summary text and key points

    Example:
        >>> paper = thom.fetch_paper("2301.00001")
        >>> summary = thom.summarize(paper, model="gpt-4o")
        >>> print(summary.summary)
        >>> print(summary.key_points)
    """
    return summarize_paper(
        paper,
        model=model,
        detail_level=detail_level,
        language=language,
        **kwargs,
    )


def search(
    query: str,
    max_results: int = 10,
    sort_by: str = "relevance",
) -> list[ArxivPaper]:
    """
    Search for papers on arXiv.

    Args:
        query: Search query (supports arXiv search syntax)
            Examples: "machine learning", "au:hinton", "cat:cs.LG"
        max_results: Maximum number of results (default: 10)
        sort_by: "relevance", "lastUpdatedDate", or "submittedDate"

    Returns:
        List of ArxivPaper objects

    Example:
        >>> papers = thom.search("transformer attention mechanism", max_results=5)
        >>> for p in papers:
        ...     print(p.title)
    """
    return search_papers(query, max_results=max_results, sort_by=sort_by)


def compare(
    papers: list[ArxivPaper],
    model: str = "gpt-4o-mini",
    **kwargs,
) -> str:
    """
    Generate a comparative analysis of multiple papers.

    Args:
        papers: List of ArxivPaper objects (2-5 recommended)
        model: LiteLLM model identifier
        **kwargs: Additional arguments for LiteLLM

    Returns:
        Comparative analysis as a string

    Example:
        >>> papers = [thom.fetch_paper(id) for id in ["2301.00001", "2301.00002"]]
        >>> analysis = thom.compare(papers)
        >>> print(analysis)
    """
    return compare_papers(papers, model=model, **kwargs)


def fetch(identifier: str) -> ArxivPaper:
    """
    Fetch a paper from arXiv by ID or URL.

    Alias for fetch_paper().

    Args:
        identifier: arXiv ID or URL
            Examples: "2301.00001", "https://arxiv.org/abs/2301.00001"

    Returns:
        ArxivPaper object with paper metadata

    Example:
        >>> paper = thom.fetch("2301.00001")
        >>> print(paper.title)
        >>> print(paper.abstract)
    """
    return fetch_paper(identifier)


# Public API
__all__ = [
    # Version
    "__version__",
    # Core functions
    "fetch_paper",
    "fetch",
    "summarize",
    "summarize_paper",
    "summarize_papers",
    "search",
    "search_papers",
    "compare",
    "compare_papers",
    # Data classes
    "ArxivPaper",
    "Summary",
    # Utilities
    "extract_arxiv_id",
    "set_api_key",
    "list_supported_models",
]
