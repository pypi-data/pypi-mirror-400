"""
IF Craft Corpus - A curated knowledge base for interactive fiction writing craft.

This package provides tools for searching and accessing the IF Craft Corpus,
a collection of craft guidance documents for writing interactive fiction.

Features:
    - Full-text keyword search with BM25 ranking
    - Optional semantic search with sentence-transformers
    - Document parsing with YAML frontmatter extraction
    - MCP server for LLM tool integration

Quick Start:
    >>> from ifcraftcorpus import Corpus
    >>> corpus = Corpus()
    >>> results = corpus.search("dialogue subtext techniques")
    >>> for r in results:
    ...     print(f"{r.source}: {r.content[:100]}...")

Installation Extras:
    - ``pip install ifcraftcorpus`` - Core package with keyword search
    - ``pip install ifcraftcorpus[mcp]`` - Add MCP server support
    - ``pip install ifcraftcorpus[embeddings-api]`` - Lightweight embeddings (Ollama/OpenAI)
    - ``pip install ifcraftcorpus[embeddings]`` - Heavyweight embeddings (sentence-transformers)
    - ``pip install ifcraftcorpus[all]`` - MCP + lightweight embeddings (Docker-friendly)
    - ``pip install ifcraftcorpus[all-local]`` - MCP + sentence-transformers

Modules:
    - :mod:`ifcraftcorpus.search` - Main Corpus API
    - :mod:`ifcraftcorpus.parser` - Markdown/YAML parsing
    - :mod:`ifcraftcorpus.index` - SQLite FTS5 indexing
    - :mod:`ifcraftcorpus.embeddings` - Semantic embeddings (optional)
    - :mod:`ifcraftcorpus.providers` - Embedding providers (Ollama, OpenAI, SentenceTransformers)
    - :mod:`ifcraftcorpus.mcp_server` - MCP server (optional)
"""

from ifcraftcorpus.index import CorpusIndex, SearchResult, build_index
from ifcraftcorpus.parser import Document, Section, parse_directory, parse_file
from ifcraftcorpus.search import Corpus, CorpusResult

__version__ = "0.1.1"

__all__ = [
    # Main API
    "Corpus",
    "CorpusResult",
    # Parser
    "Document",
    "Section",
    "parse_file",
    "parse_directory",
    # Index
    "CorpusIndex",
    "SearchResult",
    "build_index",
    # Version
    "__version__",
]
