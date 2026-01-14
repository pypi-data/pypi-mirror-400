# thom

Summarize research papers from arXiv using LLMs.

Named after [René Thom](https://en.wikipedia.org/wiki/Ren%C3%A9_Thom) (1923-2002), the French mathematician who founded catastrophe theory and won the Fields Medal in 1958.

## Installation

```bash
pip install thom
```

Or install from source:

```bash
git clone https://github.com/thom-project/thom.git
cd thom
pip install -e .
```

## Quick Start

### Python Library

```python
import thom

# Fetch a paper from arXiv
paper = thom.fetch_paper("2301.00001")
print(paper.title)
print(paper.abstract)

# Summarize the paper
summary = thom.summarize(paper)
print(summary.summary)
print(summary.key_points)

# Search for papers
papers = thom.search("transformer attention mechanism", max_results=5)
for p in papers:
    print(f"{p.arxiv_id}: {p.title}")

# Compare multiple papers
papers = [thom.fetch_paper(id) for id in ["2301.00001", "2301.00002"]]
analysis = thom.compare(papers)
print(analysis)
```

### Command Line

```bash
# Summarize a paper
thom summarize 2301.00001

# Or use a URL
thom summarize https://arxiv.org/abs/2301.00001

# Fetch paper metadata only
thom fetch 2301.00001

# Search for papers
thom search "machine learning"

# Compare papers
thom compare 2301.00001 2301.00002

# Use different models
thom summarize 2301.00001 --model gpt-4o
thom summarize 2301.00001 --model claude-3-5-sonnet-20241022
thom summarize 2301.00001 --model ollama/llama3

# Adjust detail level
thom summarize 2301.00001 --detail brief
thom summarize 2301.00001 --detail detailed

# Output in different languages
thom summarize 2301.00001 --language french

# JSON output
thom summarize 2301.00001 --json

# List supported models
thom models
```

## Configuration

### API Keys

Set your API key via environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Or set programmatically
import thom
thom.set_api_key("openai", "sk-...")
```

### Using Local Models with Ollama

```bash
# First, install and run Ollama
ollama run llama3

# Then use with thom
thom summarize 2301.00001 --model ollama/llama3
```

```python
import thom

paper = thom.fetch_paper("2301.00001")
summary = thom.summarize(paper, model="ollama/llama3")
```

## API Reference

### Core Functions

#### `thom.fetch_paper(identifier)`

Fetch a paper from arXiv by ID or URL.

```python
paper = thom.fetch_paper("2301.00001")
paper = thom.fetch_paper("https://arxiv.org/abs/2301.00001")
paper = thom.fetch_paper("https://arxiv.org/pdf/2301.00001.pdf")
```

Returns an `ArxivPaper` object with:
- `arxiv_id`: The arXiv identifier
- `title`: Paper title
- `authors`: List of author names
- `abstract`: Paper abstract
- `categories`: arXiv categories
- `published`: Publication date
- `pdf_url`: URL to PDF
- `arxiv_url`: URL to arXiv page

#### `thom.summarize(paper, model="gpt-4o-mini", detail_level="medium", language="english")`

Generate a summary of a paper.

```python
summary = thom.summarize(paper)
summary = thom.summarize(paper, model="gpt-4o", detail_level="detailed")
summary = thom.summarize(paper, language="spanish")
```

Returns a `Summary` object with:
- `paper`: The original ArxivPaper
- `summary`: Generated summary text
- `key_points`: List of key points
- `model`: Model used for summarization

#### `thom.search(query, max_results=10, sort_by="relevance")`

Search for papers on arXiv.

```python
papers = thom.search("machine learning")
papers = thom.search("au:hinton", max_results=20)
papers = thom.search("cat:cs.LG", sort_by="submittedDate")
```

#### `thom.compare(papers, model="gpt-4o-mini")`

Generate a comparative analysis of multiple papers.

```python
papers = [thom.fetch_paper(id) for id in ids]
analysis = thom.compare(papers)
```

### Supported Models

thom uses [LiteLLM](https://github.com/BerriAI/litellm) for LLM support, which means you can use models from:

- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- **Google**: `gemini/gemini-1.5-pro`, `gemini/gemini-1.5-flash`
- **Cohere**: `command-r-plus`, `command-r`
- **Ollama** (local): `ollama/llama3`, `ollama/mistral`, `ollama/mixtral`
- **Together AI**: `together_ai/meta-llama/Llama-3-70b-chat-hf`
- And [many more](https://docs.litellm.ai/docs/providers)

List available models:

```python
models = thom.list_supported_models()
```

## License

MIT License
