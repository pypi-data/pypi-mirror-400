"""evo_docs tool - Search CUDA/PyTorch documentation."""

import json
import os
from collections.abc import Generator
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec

DOCS_DIR = Path(__file__).parent.parent / "docs"
CHUNKS_FILE = DOCS_DIR / "chunks.jsonl"
EMBEDDINGS_FILE = DOCS_DIR / "embeddings.npy"

CONFIG_DIR = Path.home() / ".config" / "evokernel"
ENV_FILE = CONFIG_DIR / ".env"

MODEL = "openai/text-embedding-3-small"
TOP_K = 5

# Lazy-loaded globals
_client = None
_chunks = None
_embeddings = None


def _get_client() -> OpenAI:
    """Get OpenRouter client."""
    global _client
    if _client is None:
        load_dotenv(ENV_FILE)
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not set. Run 'evokernel setup' first.")
        _client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/gptme/gptme",
                "X-Title": "evokernel",
            },
        )
    return _client


def _load_docs():
    """Lazy-load chunks and embeddings."""
    global _chunks, _embeddings
    if _chunks is None:
        _chunks = []
        with open(CHUNKS_FILE) as f:
            for line in f:
                _chunks.append(json.loads(line))
        _embeddings = np.load(EMBEDDINGS_FILE).astype(np.float32)
    return _chunks, _embeddings


def _embed_query(query: str) -> np.ndarray:
    """Embed query using OpenRouter."""
    client = _get_client()
    response = client.embeddings.create(model=MODEL, input=[query])
    return np.array(response.data[0].embedding, dtype=np.float32)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between query vector and all doc vectors."""
    a_norm = a / np.linalg.norm(a)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(b_norm, a_norm)


def search_docs(query: str, top_k: int = TOP_K) -> list[dict]:
    """Search documentation for relevant chunks."""
    chunks, embeddings = _load_docs()

    # Embed query via OpenRouter
    query_embedding = _embed_query(query)

    # Compute similarities
    similarities = _cosine_similarity(query_embedding, embeddings)

    # Get top-k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    results = []
    for idx in top_indices:
        chunk = chunks[idx]
        results.append(
            {
                "title": chunk["title"],
                "source": chunk["source_lib"],
                "url": chunk.get("source_url", ""),
                "content": chunk["content"][:1500],
                "score": float(similarities[idx]),
            }
        )

    return results


def execute_docs(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Execute documentation search."""
    query = None
    if kwargs and "query" in kwargs:
        query = kwargs["query"]
    elif args:
        query = " ".join(args)
    elif code and code.strip():
        query = code.strip()

    if not query:
        yield Message("system", "Error: No query provided. Use: evo_docs <query>")
        return

    if not CHUNKS_FILE.exists() or not EMBEDDINGS_FILE.exists():
        yield Message("system", "Documentation files not found in evokernel/docs/")
        return

    try:
        results = search_docs(query)
    except ValueError as e:
        # API key not configured
        yield Message("system", str(e))
        return
    except Exception as e:
        err_str = str(e).lower()
        if "authentication" in err_str or "unauthorized" in err_str or "api key" in err_str or "invalid" in err_str:
            yield Message("system", "OpenRouter authentication failed. Check your API key with 'evokernel setup'.")
        else:
            yield Message("system", f"Error searching docs: {e}")
        return

    output = f"## Documentation Search: {query}\n\n"
    for i, r in enumerate(results, 1):
        output += f"### {i}. {r['title']}\n"
        output += f"**Source:** {r['source']} | **Score:** {r['score']:.3f}\n"
        if r["url"]:
            output += f"**URL:** {r['url']}\n"
        output += f"\n{r['content']}\n\n---\n\n"

    yield Message("system", output, quiet=True)


evo_docs = ToolSpec(
    name="evo_docs",
    desc="Search CUDA and PyTorch documentation for optimization techniques",
    instructions="""Use this tool to search documentation for CUDA optimization techniques, 
PyTorch C++ API usage, and GPU programming best practices.

The tool performs semantic search over:
- CUDA Programming Guide
- CUDA Toolkit documentation
- PyTorch C++ extension API

Use it when:
- You need to explain an optimization technique
- Before suggesting advanced CUDA features (shared memory, warp shuffles, etc.)
- When user asks how something works""",
    examples="""
### Search for shared memory optimization

```evo_docs
shared memory bank conflicts coalescing
```

### Search for PyTorch tensor operations

```evo_docs
PyTorch C++ tensor accessor
```
""",
    execute=execute_docs,
    block_types=["evo_docs"],
    parameters=[
        Parameter(
            name="query",
            type="string",
            description="Search query for documentation",
            required=True,
        ),
    ],
)
