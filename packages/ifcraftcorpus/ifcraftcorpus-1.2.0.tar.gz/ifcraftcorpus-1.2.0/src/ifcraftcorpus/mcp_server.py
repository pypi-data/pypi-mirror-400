"""
MCP server for IF Craft Corpus.

This module provides a Model Context Protocol (MCP) server that exposes
the corpus search functionality as tools for LLM clients. It uses FastMCP 2
for easy integration with Claude and other MCP-compatible clients.

Features:
    - Search the corpus for craft guidance
    - Retrieve specific documents
    - List available documents and clusters
    - Get corpus statistics
    - Subagent prompts for IF authoring workflows

Installation:
    The MCP server requires the ``mcp`` extra::

        pip install ifcraftcorpus[mcp]

Usage:
    Run the server using the CLI entry point::

        uvx ifcraftcorpus-mcp

    Or directly with Python::

        python -m ifcraftcorpus.mcp_server

    Configure in Claude Desktop's config file::

        {
            "mcpServers": {
                "if-craft-corpus": {
                    "command": "uvx",
                    "args": ["ifcraftcorpus-mcp"]
                }
            }
        }

Attributes:
    mcp: The FastMCP server instance.

Functions:
    run_server: Run the MCP server with specified transport.
    get_corpus: Get or create the global Corpus instance.

Tools:
    search_corpus: Search for craft guidance by query.
    get_document: Retrieve a specific document by name.
    list_documents: List all available documents.
    list_clusters: List all topic clusters.
    corpus_stats: Get corpus statistics.
    embeddings_status: Check embedding provider and index status.
    build_embeddings: Build or rebuild semantic search embeddings.

Prompts:
    if_story_architect: System prompt for an IF Story Architect agent.
    if_prose_writer: System prompt for an IF Prose Writer agent.
    if_quality_reviewer: System prompt for an IF Quality Reviewer agent.
    if_genre_consultant: System prompt for an IF Genre Consultant agent.
    if_world_curator: System prompt for an IF World Curator agent.
    if_platform_advisor: System prompt for an IF Platform Advisor agent.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP
from fastmcp.prompts import Message
from mcp.types import PromptMessage

from ifcraftcorpus.search import Corpus


def _get_subagents_dir() -> Path:
    """Get the path to the subagents directory.

    Returns the subagents directory from either:
    1. The installed package location (share/ifcraftcorpus/subagents)
    2. The development location (project root/subagents)
    """
    # Try installed location first
    if sys.prefix != sys.base_prefix:
        # We're in a virtual environment
        installed_path = Path(sys.prefix) / "share" / "ifcraftcorpus" / "subagents"
        if installed_path.exists():
            return installed_path

    # Try development location (relative to this file)
    dev_path = Path(__file__).parent.parent.parent.parent / "subagents"
    if dev_path.exists():
        return dev_path

    # Fallback to current directory
    return Path("subagents")


def _load_subagent_template(name: str) -> str:
    """Load a subagent template by name.

    Args:
        name: Template name (without .md extension)

    Returns:
        The template content as a string.

    Raises:
        FileNotFoundError: If the template doesn't exist.
    """
    subagents_dir = _get_subagents_dir()
    template_path = subagents_dir / f"{name}.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Subagent template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


# Initialize FastMCP server
mcp = FastMCP(
    name="IF Craft Corpus",
    instructions="""
    This server provides access to the Interactive Fiction Craft Corpus,
    a curated knowledge base for writing interactive fiction. Use the tools
    to search for craft guidance on topics like narrative structure, dialogue,
    branching, prose style, and genre conventions.
    """,
)

# Global corpus instance (initialized on first use)
_corpus: Corpus | None = None


def get_corpus() -> Corpus:
    """Get or create the global Corpus instance.

    Lazily initializes a single Corpus instance that is reused across
    all tool invocations for the lifetime of the server.

    Returns:
        The shared Corpus instance.
    """
    global _corpus
    if _corpus is None:
        _corpus = Corpus()
    return _corpus


@mcp.tool
def search_corpus(
    query: str,
    cluster: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Search the IF Craft Corpus for writing guidance.

    Use this tool to find craft advice for interactive fiction writing,
    including narrative structure, dialogue, branching, prose style,
    worldbuilding, and genre conventions.

    Args:
        query: Search query describing what craft guidance you need.
               Examples: "dialogue subtext", "branching narrative",
               "pacing action scenes", "horror atmosphere".
        cluster: Optional topic cluster to filter by. Valid clusters:
                 narrative-structure, prose-and-language, genre-conventions,
                 audience-and-access, world-and-setting, emotional-design,
                 scope-and-planning, craft-foundations, agent-design, game-design.
        limit: Maximum number of results (1-20, default 5).

    Returns:
        List of relevant corpus passages with source references.
    """
    limit = max(1, min(20, limit))

    corpus = get_corpus()
    results = corpus.search(query, cluster=cluster, limit=limit)

    return [
        {
            "source": r.source,
            "title": r.title,
            "cluster": r.cluster,
            "content": r.content[:2000],  # Truncate for token efficiency
            "topics": r.topics,
        }
        for r in results
    ]


@mcp.tool
def get_document(name: str) -> dict[str, Any] | None:
    """Get a specific document from the IF Craft Corpus.

    Use this tool when you need the full content of a known document,
    rather than searching for relevant passages.

    Args:
        name: Document name (e.g., "dialogue_craft", "branching_narrative_construction").
              Use list_documents to discover available documents.

    Returns:
        Full document with title, summary, cluster, topics, and all sections.
    """
    corpus = get_corpus()
    return corpus.get_document(name)


@mcp.tool
def list_documents(cluster: str | None = None) -> list[dict[str, Any]]:
    """List all documents in the IF Craft Corpus.

    Use this tool to discover what craft guidance is available.

    Args:
        cluster: Optional cluster to filter by.

    Returns:
        List of documents with name, title, cluster, and topics.
    """
    corpus = get_corpus()
    docs = corpus.list_documents()

    if cluster:
        docs = [d for d in docs if d["cluster"] == cluster]

    return docs


@mcp.tool
def list_clusters() -> list[dict[str, Any]]:
    """List all topic clusters in the IF Craft Corpus.

    Each cluster groups related craft documents. Use this to understand
    the organization of the corpus.

    Returns:
        List of clusters with names and document counts.
    """
    corpus = get_corpus()
    clusters = corpus.list_clusters()
    docs = corpus.list_documents()

    # Count documents per cluster
    counts: dict[str, int] = {}
    for d in docs:
        c = d["cluster"]
        counts[c] = counts.get(c, 0) + 1

    return [{"name": c, "document_count": counts.get(c, 0)} for c in clusters]


@mcp.tool
def corpus_stats() -> dict[str, Any]:
    """Get statistics about the IF Craft Corpus.

    Returns:
        Statistics including document count, cluster count, and availability.
    """
    corpus = get_corpus()
    return {
        "document_count": corpus.document_count(),
        "cluster_count": len(corpus.list_clusters()),
        "clusters": corpus.list_clusters(),
        "semantic_search_available": corpus.has_semantic_search,
    }


@mcp.tool
def embeddings_status() -> dict[str, Any]:
    """Get status of embedding providers and index.

    Returns information about available embedding providers (Ollama, OpenAI,
    SentenceTransformers) and whether embeddings are currently loaded.

    Returns:
        Dict with provider availability and embedding index status.
    """
    result: dict[str, Any] = {
        "semantic_search_available": get_corpus().has_semantic_search,
        "providers": {},
        "saved_embeddings": None,
    }

    # Check provider availability
    try:
        from ifcraftcorpus.providers import (
            OllamaEmbeddings,
            OpenAIEmbeddings,
            SentenceTransformersEmbeddings,
            get_embedding_provider,
        )

        for name, cls in [
            ("ollama", OllamaEmbeddings),
            ("openai", OpenAIEmbeddings),
            ("sentence_transformers", SentenceTransformersEmbeddings),
        ]:
            try:
                provider = cls()
                available = provider.check_availability()
                result["providers"][name] = {
                    "available": available,
                    "model": provider.model if available else None,
                    "dimension": provider.dimension if available else None,
                }
            except Exception:
                result["providers"][name] = {"available": False, "error": "import_failed"}

        # Auto-detect best provider
        auto = get_embedding_provider()
        result["auto_detected_provider"] = auto.provider_name if auto else None
    except ImportError:
        result["providers_error"] = "providers module not available"

    # Check for saved embeddings
    embeddings_path = Path(os.environ.get("EMBEDDINGS_PATH", "embeddings"))
    if embeddings_path.exists() and (embeddings_path / "metadata.json").exists():
        import json

        with open(embeddings_path / "metadata.json") as f:
            meta = json.load(f)
        result["saved_embeddings"] = {
            "path": str(embeddings_path),
            "provider": meta.get("provider_name"),
            "model": meta.get("model_name"),
            "count": len(meta.get("metadata", [])),
        }

    return result


@mcp.tool
def build_embeddings(
    provider: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Build or rebuild the embedding index for semantic search.

    Builds embeddings for all corpus documents using the specified provider.
    This enables semantic search mode which finds conceptually similar content.

    Args:
        provider: Embedding provider to use: "ollama", "openai", or
                 "sentence_transformers". If None, auto-detects the best
                 available provider.
        force: If True, rebuild even if embeddings already exist.

    Returns:
        Dict with build results including item count and provider used.

    Note:
        Ollama requires a running Ollama server (configure with OLLAMA_HOST env).
        OpenAI requires OPENAI_API_KEY environment variable.
        SentenceTransformers requires the sentence-transformers package.
    """
    global _corpus

    try:
        from ifcraftcorpus.providers import (
            OllamaEmbeddings,
            OpenAIEmbeddings,
            SentenceTransformersEmbeddings,
            get_embedding_provider,
        )
    except ImportError:
        return {
            "error": "Embedding providers not available. "
            "Install with [embeddings-api] or [embeddings] extras."
        }

    # Get provider
    embedding_provider = None
    if provider:
        provider_map = {
            "ollama": OllamaEmbeddings,
            "openai": OpenAIEmbeddings,
            "sentence_transformers": SentenceTransformersEmbeddings,
        }
        if provider not in provider_map:
            return {
                "error": f"Unknown provider: {provider}. Use: ollama, openai, sentence_transformers"
            }
        embedding_provider = provider_map[provider]()
    else:
        embedding_provider = get_embedding_provider()

    if not embedding_provider:
        return {
            "error": "No embedding provider available. "
            "Configure Ollama, set OPENAI_API_KEY, or install sentence-transformers."
        }

    if not embedding_provider.check_availability():
        return {"error": f"Provider {embedding_provider.provider_name} is not available."}

    # Configure paths
    embeddings_path = Path(os.environ.get("EMBEDDINGS_PATH", "embeddings"))

    # Check if already exists
    if not force and embeddings_path.exists() and (embeddings_path / "metadata.json").exists():
        return {
            "status": "skipped",
            "message": "Embeddings already exist. Use force=True to rebuild.",
            "path": str(embeddings_path),
        }

    # Create new corpus with embedding support
    corpus = Corpus(
        embeddings_path=embeddings_path,
        embedding_provider=embedding_provider,
    )

    # Build embeddings
    count = corpus.build_embeddings(force=force)

    # Update global corpus to use new embeddings
    _corpus = Corpus(embeddings_path=embeddings_path)

    return {
        "status": "success",
        "items_embedded": count,
        "provider": embedding_provider.provider_name,
        "model": embedding_provider.model,
        "path": str(embeddings_path),
    }


# =============================================================================
# Subagent Prompts
# =============================================================================
#
# These prompts provide system prompts for specialized IF authoring agents.
# Each agent has a specific role in the IF creation workflow.


@mcp.prompt(
    name="if_story_architect",
    description="System prompt for an IF Story Architect - an orchestrator agent that "
    "plans narrative structure, decomposes IF projects, and coordinates creation.",
)
def if_story_architect_prompt(
    project_name: str | None = None,
    genre: str | None = None,
) -> list[PromptMessage]:
    """Get the IF Story Architect system prompt.

    Args:
        project_name: Optional project name to include in the prompt context.
        genre: Optional genre to emphasize (fantasy, horror, mystery, etc.).

    Returns:
        System prompt messages for the Story Architect agent.
    """
    template = _load_subagent_template("if_story_architect")

    # Add optional context
    context_parts = []
    if project_name:
        context_parts.append(f"Project: {project_name}")
    if genre:
        context_parts.append(f"Genre: {genre}")

    if context_parts:
        context = "\n\n---\n\n## Current Project Context\n\n" + "\n".join(context_parts)
        template = template + context

    return [Message(template, role="user")]


@mcp.prompt(
    name="if_prose_writer",
    description="System prompt for an IF Prose Writer - a specialist agent that "
    "creates narrative content including prose, dialogue, and scene text.",
)
def if_prose_writer_prompt(
    genre: str | None = None,
    pov: str | None = None,
) -> list[PromptMessage]:
    """Get the IF Prose Writer system prompt.

    Args:
        genre: Optional genre to emphasize (fantasy, horror, mystery, etc.).
        pov: Optional point of view (first, second, third).

    Returns:
        System prompt messages for the Prose Writer agent.
    """
    template = _load_subagent_template("if_prose_writer")

    # Add optional context
    context_parts = []
    if genre:
        context_parts.append(f"Genre: {genre}")
    if pov:
        context_parts.append(f"Point of View: {pov}")

    if context_parts:
        context = "\n\n---\n\n## Current Project Context\n\n" + "\n".join(context_parts)
        template = template + context

    return [Message(template, role="user")]


@mcp.prompt(
    name="if_quality_reviewer",
    description="System prompt for an IF Quality Reviewer - a validator agent that "
    "reviews IF content for craft quality, consistency, and standards compliance.",
)
def if_quality_reviewer_prompt(
    focus_areas: str | None = None,
) -> list[PromptMessage]:
    """Get the IF Quality Reviewer system prompt.

    Args:
        focus_areas: Optional comma-separated list of areas to focus on
                    (e.g., "voice,pacing,continuity").

    Returns:
        System prompt messages for the Quality Reviewer agent.
    """
    template = _load_subagent_template("if_quality_reviewer")

    if focus_areas:
        context = f"\n\n---\n\n## Review Focus\n\nPrioritize these areas: {focus_areas}"
        template = template + context

    return [Message(template, role="user")]


@mcp.prompt(
    name="if_genre_consultant",
    description="System prompt for an IF Genre Consultant - a researcher agent that "
    "provides genre-specific guidance on conventions, tropes, and reader expectations.",
)
def if_genre_consultant_prompt(
    primary_genre: str | None = None,
    secondary_genre: str | None = None,
) -> list[PromptMessage]:
    """Get the IF Genre Consultant system prompt.

    Args:
        primary_genre: Optional primary genre to focus on.
        secondary_genre: Optional secondary genre for blending advice.

    Returns:
        System prompt messages for the Genre Consultant agent.
    """
    template = _load_subagent_template("if_genre_consultant")

    context_parts = []
    if primary_genre:
        context_parts.append(f"Primary Genre: {primary_genre}")
    if secondary_genre:
        context_parts.append(f"Secondary Genre: {secondary_genre}")

    if context_parts:
        context = "\n\n---\n\n## Genre Focus\n\n" + "\n".join(context_parts)
        template = template + context

    return [Message(template, role="user")]


@mcp.prompt(
    name="if_world_curator",
    description="System prompt for an IF World Curator - a curator agent that "
    "maintains world consistency, manages canon, and ensures setting coherence.",
)
def if_world_curator_prompt(
    world_name: str | None = None,
    setting_type: str | None = None,
) -> list[PromptMessage]:
    """Get the IF World Curator system prompt.

    Args:
        world_name: Optional name of the world/setting.
        setting_type: Optional setting type (e.g., "fantasy medieval", "sci-fi space").

    Returns:
        System prompt messages for the World Curator agent.
    """
    template = _load_subagent_template("if_world_curator")

    context_parts = []
    if world_name:
        context_parts.append(f"World: {world_name}")
    if setting_type:
        context_parts.append(f"Setting Type: {setting_type}")

    if context_parts:
        context = "\n\n---\n\n## World Context\n\n" + "\n".join(context_parts)
        template = template + context

    return [Message(template, role="user")]


@mcp.prompt(
    name="if_platform_advisor",
    description="System prompt for an IF Platform Advisor - a researcher agent that "
    "provides guidance on tools, platforms, and technical implementation.",
)
def if_platform_advisor_prompt(
    target_platform: str | None = None,
    team_size: str | None = None,
) -> list[PromptMessage]:
    """Get the IF Platform Advisor system prompt.

    Args:
        target_platform: Optional target platform if already decided.
        team_size: Optional team size (solo, small, large).

    Returns:
        System prompt messages for the Platform Advisor agent.
    """
    template = _load_subagent_template("if_platform_advisor")

    context_parts = []
    if target_platform:
        context_parts.append(f"Target Platform: {target_platform}")
    if team_size:
        context_parts.append(f"Team Size: {team_size}")

    if context_parts:
        context = "\n\n---\n\n## Project Context\n\n" + "\n".join(context_parts)
        template = template + context

    return [Message(template, role="user")]


@mcp.tool
def list_subagents() -> list[dict[str, Any]]:
    """List all available IF subagent prompts.

    Returns a list of subagent templates that can be used as system prompts
    for specialized IF authoring agents.

    Returns:
        List of subagents with name, description, and parameters.
    """
    return [
        {
            "name": "if_story_architect",
            "description": "Orchestrator that plans narrative structure and coordinates creation",
            "archetype": "orchestrator",
            "parameters": ["project_name", "genre"],
        },
        {
            "name": "if_prose_writer",
            "description": "Specialist that creates narrative prose, dialogue, and scene text",
            "archetype": "creator",
            "parameters": ["genre", "pov"],
        },
        {
            "name": "if_quality_reviewer",
            "description": "Validator agent that reviews content for quality and consistency",
            "archetype": "validator",
            "parameters": ["focus_areas"],
        },
        {
            "name": "if_genre_consultant",
            "description": "Researcher agent for genre conventions, tropes, and expectations",
            "archetype": "researcher",
            "parameters": ["primary_genre", "secondary_genre"],
        },
        {
            "name": "if_world_curator",
            "description": "Curator agent that maintains world consistency and canon",
            "archetype": "curator",
            "parameters": ["world_name", "setting_type"],
        },
        {
            "name": "if_platform_advisor",
            "description": "Researcher agent for tools, platforms, and technical implementation",
            "archetype": "researcher",
            "parameters": ["target_platform", "team_size"],
        },
    ]


def run_server(
    transport: Literal["stdio", "http"] = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """Run the MCP server with the specified transport.

    Starts the FastMCP server and blocks until shutdown.

    Args:
        transport: Transport protocol to use:

            - ``"stdio"``: Standard input/output (default, for CLI clients)
            - ``"http"``: HTTP server (for web-based clients)

        host: Host address to bind to for HTTP transport. Default "127.0.0.1".
            Use "0.0.0.0" to allow external connections.
        port: Port number for HTTP transport. Default 8000.

    Example:
        >>> # Run with stdio (default)
        >>> run_server()

        >>> # Run as HTTP server
        >>> run_server(transport="http", host="0.0.0.0", port=8080)
    """
    if transport == "http":
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run()


# Entry point for `uvx ifcraftcorpus-mcp` or `python -m ifcraftcorpus.mcp_server`
if __name__ == "__main__":
    mcp.run()
