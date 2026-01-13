"""
Command-line interface for IF Craft Corpus.

Provides commands for:
- Corpus information and search
- Building and managing embedding indexes
- Provider status and configuration

Usage:
    ifcraftcorpus info          # Show corpus info
    ifcraftcorpus search QUERY  # Search the corpus
    ifcraftcorpus embeddings build   # Build embeddings
    ifcraftcorpus embeddings status  # Show embedding status
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ifcraftcorpus.providers import EmbeddingProvider


def cmd_info(args: argparse.Namespace) -> int:
    """Show corpus information."""
    from ifcraftcorpus import Corpus, __version__

    corpus = Corpus()

    print(f"\nIF Craft Corpus v{__version__}")
    print(f"Documents: {corpus.document_count()}")
    print(f"Clusters: {len(corpus.list_clusters())}")
    print("\nClusters:")
    for cluster in corpus.list_clusters():
        docs = [d for d in corpus.list_documents() if d["cluster"] == cluster]
        print(f"  {cluster}: {len(docs)} file(s)")

    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Search the corpus."""
    from ifcraftcorpus import Corpus

    corpus = Corpus()
    results = corpus.search(
        args.query,
        limit=args.limit,
        cluster=args.cluster,
        mode="keyword",  # CLI uses keyword by default
    )

    if not results:
        print("No results found.")
        return 0

    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r.title} ({r.cluster})")
        if r.section_heading:
            print(f"    Section: {r.section_heading}")
        print(f"    Score: {r.score:.3f}")
        # Truncate content
        content = r.content[:200].replace("\n", " ")
        if len(r.content) > 200:
            content += "..."
        print(f"    {content}")

    return 0


def cmd_embeddings_status(args: argparse.Namespace) -> int:
    """Show embedding provider and index status."""
    from ifcraftcorpus.providers import (
        OllamaEmbeddings,
        OpenAIEmbeddings,
        SentenceTransformersEmbeddings,
        get_embedding_provider,
    )

    print("\n=== Embedding Providers ===\n")

    # Check each provider
    providers = [
        ("Ollama", OllamaEmbeddings()),
        ("OpenAI", OpenAIEmbeddings()),
        ("SentenceTransformers", SentenceTransformersEmbeddings()),
    ]

    for name, provider in providers:
        available = provider.check_availability()
        status = "✓ Available" if available else "✗ Not available"
        print(f"{name:20} {status}")
        if available:
            print(f"{'':20} Model: {provider.model} ({provider.dimension}d)")

    # Auto-detect
    print("\n=== Auto-Detection ===\n")
    auto = get_embedding_provider()
    if auto:
        print(f"Selected: {auto.provider_name} ({auto.model})")
    else:
        print("No provider available")

    # Check for saved embeddings
    print("\n=== Saved Embeddings ===\n")
    embeddings_path = Path("embeddings")
    if embeddings_path.exists() and (embeddings_path / "metadata.json").exists():
        with open(embeddings_path / "metadata.json") as f:
            meta = json.load(f)
        print(f"Path: {embeddings_path}")
        print(f"Provider: {meta.get('provider_name', 'unknown')}")
        print(f"Model: {meta.get('model_name', 'unknown')}")
        print(f"Documents: {len(meta.get('metadata', []))}")
    else:
        print("No saved embeddings found at ./embeddings/")

    return 0


def cmd_embeddings_build(args: argparse.Namespace) -> int:
    """Build embedding index."""
    from ifcraftcorpus import Corpus
    from ifcraftcorpus.embeddings import EmbeddingIndex
    from ifcraftcorpus.providers import (
        OllamaEmbeddings,
        OpenAIEmbeddings,
        SentenceTransformersEmbeddings,
        get_embedding_provider,
    )

    # Get provider
    provider: EmbeddingProvider | None = None
    if args.provider:
        if args.provider == "ollama":
            provider = OllamaEmbeddings(model=args.model, host=args.ollama_host)
        elif args.provider == "openai":
            provider = OpenAIEmbeddings(model=args.model, api_key=args.openai_key)
        elif args.provider in ("sentence-transformers", "st", "local"):
            provider = SentenceTransformersEmbeddings(model=args.model)
        else:
            print(f"Unknown provider: {args.provider}", file=sys.stderr)
            return 1
    else:
        provider = get_embedding_provider(model=args.model)

    if not provider:
        print("No embedding provider available.", file=sys.stderr)
        print("Configure Ollama, set OPENAI_API_KEY, or install sentence-transformers.")
        return 1

    if not provider.check_availability():
        print(f"Provider {provider.provider_name} is not available.", file=sys.stderr)
        return 1

    print(f"Using provider: {provider.provider_name}")
    print(f"Model: {provider.model} ({provider.dimension}d)")

    # Build embeddings
    corpus = Corpus()
    print(f"\nBuilding embeddings for {corpus.document_count()} documents...")

    # Use the corpus's internal index
    embedding_index = EmbeddingIndex(provider=provider)

    # Iterate through documents
    doc_count = 0
    section_count = 0

    for doc_info in corpus.list_documents():
        doc = corpus.get_document(doc_info["name"])
        if not doc:
            continue

        doc_count += 1

        # Add document summary
        embedding_index.add_texts(
            [doc["summary"]],
            [
                {
                    "document_name": doc["name"],
                    "title": doc["title"],
                    "cluster": doc["cluster"],
                    "section_heading": None,
                    "content": doc["summary"],
                    "topics": doc.get("topics", []),
                }
            ],
        )
        section_count += 1

        # Add sections
        for section in doc.get("sections", []):
            if section["content"].strip():
                embedding_index.add_texts(
                    [section["content"]],
                    [
                        {
                            "document_name": doc["name"],
                            "title": doc["title"],
                            "cluster": doc["cluster"],
                            "section_heading": section["heading"],
                            "content": section["content"],
                            "topics": doc.get("topics", []),
                        }
                    ],
                )
                section_count += 1

        if doc_count % 10 == 0:
            print(f"  Processed {doc_count} documents...")

    # Save
    output_path = Path(args.output)
    embedding_index.save(output_path)

    print(f"\nDone! Embedded {section_count} sections from {doc_count} documents.")
    print(f"Saved to: {output_path}")

    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ifcraftcorpus",
        description="IF Craft Corpus - Interactive fiction writing craft knowledge base",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # info command
    info_parser = subparsers.add_parser("info", help="Show corpus information")
    info_parser.set_defaults(func=cmd_info)

    # search command
    search_parser = subparsers.add_parser("search", help="Search the corpus")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-n", "--limit", type=int, default=5, help="Max results")
    search_parser.add_argument("-c", "--cluster", help="Filter by cluster")
    search_parser.set_defaults(func=cmd_search)

    # embeddings subcommand
    emb_parser = subparsers.add_parser("embeddings", help="Manage embeddings")
    emb_subparsers = emb_parser.add_subparsers(dest="emb_command", help="Embedding commands")

    # embeddings status
    emb_status = emb_subparsers.add_parser("status", help="Show provider and index status")
    emb_status.set_defaults(func=cmd_embeddings_status)

    # embeddings build
    emb_build = emb_subparsers.add_parser("build", help="Build embedding index")
    emb_build.add_argument(
        "-p",
        "--provider",
        choices=["ollama", "openai", "sentence-transformers", "st", "local"],
        help="Embedding provider (default: auto-detect)",
    )
    emb_build.add_argument("-m", "--model", help="Model name override")
    emb_build.add_argument(
        "-o", "--output", default="embeddings", help="Output directory (default: ./embeddings)"
    )
    emb_build.add_argument("--ollama-host", help="Ollama host URL")
    emb_build.add_argument("--openai-key", help="OpenAI API key")
    emb_build.set_defaults(func=cmd_embeddings_build)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "embeddings" and not getattr(args, "emb_command", None):
        emb_parser.print_help()
        return 0

    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
