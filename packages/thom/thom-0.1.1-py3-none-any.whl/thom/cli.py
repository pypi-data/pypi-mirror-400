"""
Command-line interface for thom.

Provides CLI commands for fetching and summarizing arXiv papers.
"""

import argparse
import sys
from typing import Optional

from . import fetch_paper, summarize, search, compare
from .summarizer import list_supported_models


def main(args: Optional[list[str]] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="thom",
        description="Summarize research papers from arXiv using LLMs",
        epilog="Named after René Thom, French mathematician and Fields Medal winner.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.1",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Summarize command
    summarize_parser = subparsers.add_parser(
        "summarize",
        aliases=["sum", "s"],
        help="Summarize an arXiv paper",
    )
    summarize_parser.add_argument(
        "paper",
        help="arXiv paper ID or URL (e.g., '2301.00001' or 'https://arxiv.org/abs/2301.00001')",
    )
    summarize_parser.add_argument(
        "-m", "--model",
        default="gpt-4o-mini",
        help="LLM model to use (default: gpt-4o-mini)",
    )
    summarize_parser.add_argument(
        "-d", "--detail",
        choices=["brief", "medium", "detailed"],
        default="medium",
        help="Summary detail level (default: medium)",
    )
    summarize_parser.add_argument(
        "-l", "--language",
        default="english",
        help="Output language (default: english)",
    )
    summarize_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    # Fetch command (just get paper info)
    fetch_parser = subparsers.add_parser(
        "fetch",
        aliases=["f"],
        help="Fetch paper metadata without summarizing",
    )
    fetch_parser.add_argument(
        "paper",
        help="arXiv paper ID or URL",
    )
    fetch_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search for papers on arXiv",
    )
    search_parser.add_argument(
        "query",
        help="Search query",
    )
    search_parser.add_argument(
        "-n", "--max-results",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)",
    )
    search_parser.add_argument(
        "--sort",
        choices=["relevance", "lastUpdatedDate", "submittedDate"],
        default="relevance",
        help="Sort by (default: relevance)",
    )
    search_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    # Compare command
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare multiple papers",
    )
    compare_parser.add_argument(
        "papers",
        nargs="+",
        help="arXiv paper IDs or URLs (2-5 papers)",
    )
    compare_parser.add_argument(
        "-m", "--model",
        default="gpt-4o-mini",
        help="LLM model to use (default: gpt-4o-mini)",
    )

    # Models command
    subparsers.add_parser(
        "models",
        help="List supported LLM models",
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.command is None:
        parser.print_help()
        return 0

    try:
        if parsed_args.command in ("summarize", "sum", "s"):
            return _cmd_summarize(parsed_args)
        elif parsed_args.command in ("fetch", "f"):
            return _cmd_fetch(parsed_args)
        elif parsed_args.command == "search":
            return _cmd_search(parsed_args)
        elif parsed_args.command == "compare":
            return _cmd_compare(parsed_args)
        elif parsed_args.command == "models":
            return _cmd_models(parsed_args)
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\nAborted.")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _cmd_summarize(args: argparse.Namespace) -> int:
    """Handle summarize command."""
    print(f"Fetching paper: {args.paper}...")
    paper = fetch_paper(args.paper)

    print(f"Summarizing with {args.model}...")
    summary = summarize(
        paper,
        model=args.model,
        detail_level=args.detail,
        language=args.language,
    )

    if args.json:
        import json
        output = {
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract,
            "categories": paper.categories,
            "published": paper.published,
            "pdf_url": paper.pdf_url,
            "arxiv_url": paper.arxiv_url,
            "summary": summary.summary,
            "key_points": summary.key_points,
            "model": summary.model,
        }
        print(json.dumps(output, indent=2))
    else:
        print(summary)

    return 0


def _cmd_fetch(args: argparse.Namespace) -> int:
    """Handle fetch command."""
    paper = fetch_paper(args.paper)

    if args.json:
        import json
        output = {
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract,
            "categories": paper.categories,
            "published": paper.published,
            "updated": paper.updated,
            "pdf_url": paper.pdf_url,
            "arxiv_url": paper.arxiv_url,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Title: {paper.title}")
        print(f"{'='*60}")
        print(f"\nAuthors: {', '.join(paper.authors)}")
        print(f"arXiv ID: {paper.arxiv_id}")
        print(f"Categories: {', '.join(paper.categories)}")
        print(f"Published: {paper.published[:10]}")
        print(f"\nAbstract:")
        print(paper.abstract)
        print(f"\nPDF: {paper.pdf_url}")
        print(f"URL: {paper.arxiv_url}")

    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    """Handle search command."""
    papers = search(
        args.query,
        max_results=args.max_results,
        sort_by=args.sort,
    )

    if not papers:
        print("No papers found.")
        return 0

    if args.json:
        import json
        output = [
            {
                "arxiv_id": p.arxiv_id,
                "title": p.title,
                "authors": p.authors,
                "categories": p.categories,
                "published": p.published,
                "arxiv_url": p.arxiv_url,
            }
            for p in papers
        ]
        print(json.dumps(output, indent=2))
    else:
        print(f"\nFound {len(papers)} papers:\n")
        for i, paper in enumerate(papers, 1):
            authors = ", ".join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors += " et al."
            print(f"{i}. [{paper.arxiv_id}] {paper.title}")
            print(f"   {authors}")
            print(f"   Categories: {', '.join(paper.categories[:3])}")
            print()

    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    """Handle compare command."""
    if len(args.papers) < 2:
        print("Error: Need at least 2 papers to compare", file=sys.stderr)
        return 1

    print("Fetching papers...")
    papers = [fetch_paper(p) for p in args.papers]

    print(f"Comparing with {args.model}...")
    analysis = compare(papers, model=args.model)

    print(f"\n{'='*60}")
    print("COMPARATIVE ANALYSIS")
    print(f"{'='*60}\n")
    print(analysis)

    return 0


def _cmd_models(args: argparse.Namespace) -> int:
    """Handle models command."""
    models = list_supported_models()

    print("\nSupported LLM Models:")
    print("=" * 40)

    for provider, model_list in models.items():
        print(f"\n{provider.upper()}:")
        for model in model_list:
            print(f"  • {model}")

    print("\nNote: You need to set the appropriate API key for each provider.")
    print("Set via environment variables (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY)")
    print("\nFor local models, use Ollama: ollama/model-name")

    return 0


if __name__ == "__main__":
    sys.exit(main())
