"""
Paper summarization module using LiteLLM.

Provides functionality to generate summaries of research papers
using various LLM providers through LiteLLM.
"""

from dataclasses import dataclass
from typing import Optional

import litellm
from litellm import completion

from .arxiv import ArxivPaper


@dataclass
class Summary:
    """Represents a paper summary."""

    paper: ArxivPaper
    summary: str
    key_points: list[str]
    model: str

    def __str__(self) -> str:
        points = "\n".join(f"  • {p}" for p in self.key_points)
        return f"""
{'='*60}
{self.paper.title}
{'='*60}

Authors: {', '.join(self.paper.authors[:5])}{'...' if len(self.paper.authors) > 5 else ''}
arXiv: {self.paper.arxiv_id}
Categories: {', '.join(self.paper.categories)}

SUMMARY
-------
{self.summary}

KEY POINTS
----------
{points}

Model: {self.model}
{'='*60}
""".strip()


# Default system prompt for summarization
DEFAULT_SYSTEM_PROMPT = """You are a research paper analyst. Your task is to provide clear,
accurate summaries of academic papers based on their abstracts and metadata.

Focus on:
1. The main research question or problem being addressed
2. The methodology or approach used
3. Key findings and contributions
4. Potential implications or applications

Be concise but thorough. Use accessible language while maintaining technical accuracy."""


def summarize_paper(
    paper: ArxivPaper,
    model: str = "gpt-4o-mini",
    system_prompt: Optional[str] = None,
    detail_level: str = "medium",
    language: str = "english",
    **kwargs,
) -> Summary:
    """
    Generate a summary of an arXiv paper using LiteLLM.

    Args:
        paper: ArxivPaper object to summarize
        model: LiteLLM model identifier (default: "gpt-4o-mini")
            Examples: "gpt-4o", "claude-3-sonnet-20240229", "ollama/llama2"
        system_prompt: Custom system prompt (optional)
        detail_level: Summary detail - "brief", "medium", or "detailed"
        language: Output language (default: "english")
        **kwargs: Additional arguments passed to litellm.completion()

    Returns:
        Summary object containing the generated summary

    Raises:
        Exception: If the LLM call fails
    """
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    # Build the user prompt based on detail level
    detail_instructions = {
        "brief": "Provide a 2-3 sentence summary and 3 key points.",
        "medium": "Provide a paragraph summary (4-6 sentences) and 5 key points.",
        "detailed": "Provide a comprehensive summary (2-3 paragraphs) and 7-10 key points.",
    }

    detail_instruction = detail_instructions.get(detail_level, detail_instructions["medium"])

    user_prompt = f"""Please analyze and summarize the following research paper.

TITLE: {paper.title}

AUTHORS: {', '.join(paper.authors)}

CATEGORIES: {', '.join(paper.categories)}

ABSTRACT:
{paper.abstract}

---

{detail_instruction}

Respond in {language}.

Format your response as:
SUMMARY:
[Your summary here]

KEY POINTS:
- [Point 1]
- [Point 2]
...
"""

    # Call LiteLLM
    response = completion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )

    # Parse response
    content = response.choices[0].message.content
    summary_text, key_points = _parse_response(content)

    return Summary(
        paper=paper,
        summary=summary_text,
        key_points=key_points,
        model=model,
    )


def summarize_papers(
    papers: list[ArxivPaper],
    model: str = "gpt-4o-mini",
    **kwargs,
) -> list[Summary]:
    """
    Generate summaries for multiple papers.

    Args:
        papers: List of ArxivPaper objects to summarize
        model: LiteLLM model identifier
        **kwargs: Additional arguments passed to summarize_paper()

    Returns:
        List of Summary objects
    """
    summaries = []
    for paper in papers:
        summary = summarize_paper(paper, model=model, **kwargs)
        summaries.append(summary)
    return summaries


def compare_papers(
    papers: list[ArxivPaper],
    model: str = "gpt-4o-mini",
    **kwargs,
) -> str:
    """
    Generate a comparative analysis of multiple papers.

    Args:
        papers: List of ArxivPaper objects to compare (2-5 papers recommended)
        model: LiteLLM model identifier
        **kwargs: Additional arguments passed to litellm.completion()

    Returns:
        Comparative analysis as a string
    """
    if len(papers) < 2:
        raise ValueError("Need at least 2 papers to compare")

    papers_text = "\n\n".join([
        f"PAPER {i+1}:\nTitle: {p.title}\nAuthors: {', '.join(p.authors)}\nAbstract: {p.abstract}"
        for i, p in enumerate(papers)
    ])

    user_prompt = f"""Compare and contrast the following research papers:

{papers_text}

---

Provide:
1. A brief summary of each paper (2-3 sentences each)
2. Common themes or approaches across the papers
3. Key differences in methodology or findings
4. How these papers relate to or build upon each other
5. Overall assessment of the research landscape they represent
"""

    response = completion(
        model=model,
        messages=[
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )

    return response.choices[0].message.content


def _parse_response(content: str) -> tuple[str, list[str]]:
    """Parse the LLM response to extract summary and key points."""
    summary = ""
    key_points = []

    # Try to extract structured sections
    lines = content.strip().split("\n")
    current_section = None
    summary_lines = []

    for line in lines:
        line_stripped = line.strip()
        line_upper = line_stripped.upper()

        if line_upper.startswith("SUMMARY:") or line_upper == "SUMMARY":
            current_section = "summary"
            # Check if summary is on the same line
            if ":" in line_stripped:
                rest = line_stripped.split(":", 1)[1].strip()
                if rest:
                    summary_lines.append(rest)
        elif line_upper.startswith("KEY POINTS:") or line_upper == "KEY POINTS":
            current_section = "points"
        elif current_section == "summary" and line_stripped:
            summary_lines.append(line_stripped)
        elif current_section == "points" and line_stripped:
            # Extract bullet points
            if line_stripped.startswith(("-", "•", "*", "·")):
                point = line_stripped.lstrip("-•*· ").strip()
                if point:
                    key_points.append(point)
            elif line_stripped[0].isdigit() and "." in line_stripped[:3]:
                # Numbered list
                point = line_stripped.split(".", 1)[1].strip()
                if point:
                    key_points.append(point)

    summary = " ".join(summary_lines)

    # Fallback: if parsing failed, use the whole content
    if not summary:
        summary = content
    if not key_points:
        key_points = ["See summary above for details"]

    return summary, key_points


def set_api_key(provider: str, api_key: str) -> None:
    """
    Set API key for a specific provider.

    Args:
        provider: Provider name ("openai", "anthropic", "cohere", etc.)
        api_key: API key string
    """
    import os

    key_mapping = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "cohere": "COHERE_API_KEY",
        "huggingface": "HUGGINGFACE_API_KEY",
        "replicate": "REPLICATE_API_KEY",
        "together": "TOGETHER_API_KEY",
        "azure": "AZURE_API_KEY",
    }

    env_var = key_mapping.get(provider.lower())
    if env_var:
        os.environ[env_var] = api_key
    else:
        # Try generic format
        os.environ[f"{provider.upper()}_API_KEY"] = api_key


def list_supported_models() -> dict[str, list[str]]:
    """
    List commonly used models supported by LiteLLM.

    Returns:
        Dictionary mapping provider names to lists of model identifiers
    """
    return {
        "openai": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ],
        "anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        "google": [
            "gemini/gemini-1.5-pro",
            "gemini/gemini-1.5-flash",
        ],
        "ollama": [
            "ollama/llama3",
            "ollama/llama2",
            "ollama/mistral",
            "ollama/mixtral",
        ],
        "cohere": [
            "command-r-plus",
            "command-r",
        ],
        "together": [
            "together_ai/meta-llama/Llama-3-70b-chat-hf",
            "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
        ],
    }
