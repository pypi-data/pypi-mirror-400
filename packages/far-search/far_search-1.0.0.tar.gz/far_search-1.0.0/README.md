# FAR Search - Core SDK

[![PyPI version](https://badge.fury.io/py/far-search.svg)](https://pypi.org/project/far-search/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Lightweight SDK** for semantic search over Federal Acquisition Regulations (FAR).

No LangChain dependency - just `requests`. Perfect for:
- Simple scripts and notebooks
- Serverless functions (minimal cold start)
- Projects that don't use LangChain
- Lightweight microservices

## Installation

```bash
pip install far-search
```

**Size comparison:**
- `far-search`: ~10KB + requests (~1MB total)
- `far-search-tool`: ~15KB + LangChain (~150MB total)

## Quick Start

```python
from far_search_core import FARSearchClient

# Auto-registers on first use - no API key needed!
client = FARSearchClient()

# Search
results = client.search("cybersecurity requirements", top_k=5)

for clause in results:
    print(f"{clause.id}: {clause.title}")
    print(f"  Score: {clause.similarity_score:.1%}")
    print(f"  URL: {clause.url}")
```

## Convenience Function

```python
from far_search_core import search_far

# One-liner search
results = search_far("small business set aside requirements")
```

## FARClause Object

Each result is a `FARClause` dataclass:

```python
@dataclass
class FARClause:
    id: str              # e.g., "52.204-2"
    title: str           # e.g., "Security Requirements"
    text: str            # Full clause text
    source: str          # e.g., "FAR Part 52"
    url: str             # acquisition.gov URL
    similarity_score: float  # 0.0 - 1.0
```

## Get Formatted Text (for LLMs)

```python
client = FARSearchClient()

# Get pre-formatted text for LLM context
text = client.search_text("contract termination procedures")
print(text)
```

## Get Specific Clause

```python
client = FARSearchClient()

clause = client.get_clause("52.203-1")
if clause:
    print(clause.text)
```

## Configuration

```python
# With explicit API key
client = FARSearchClient(api_key="far_live_...")

# With RapidAPI key (for higher limits)
client = FARSearchClient(rapidapi_key="your-rapidapi-key")

# Environment variables
# export FAR_API_KEY=far_live_...
# export FAR_QUIET=1  # Suppress usage warnings
```

## Pricing

| Plan | Price | Queries/Month |
|------|-------|---------------|
| **Free** | $0 | 500 |
| **Pro** | $29/mo | 5,000 |
| **Ultra** | $199/mo | 150,000 |

Auto-registers on first use. Upgrade at [RapidAPI](https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search).

## Error Handling

```python
from far_search_core import FARSearchClient, FARAPIError, FARRateLimitError

client = FARSearchClient()

try:
    results = client.search("my query")
except FARRateLimitError:
    print("Rate limit exceeded - upgrade your plan")
except FARAPIError as e:
    print(f"API error: {e}")
```

## Related Packages

| Package | Use Case |
|---------|----------|
| **far-search** (this) | Lightweight, no dependencies |
| **far-search-tool** | LangChain tool integration |
| **far-search-crewai** | CrewAI multi-agent tool |
| **far-search-autogpt** | AutoGPT plugin |
| **far-oracle** | MCP Server for Claude Desktop |

## License

MIT License - see [LICENSE](LICENSE) for details.

