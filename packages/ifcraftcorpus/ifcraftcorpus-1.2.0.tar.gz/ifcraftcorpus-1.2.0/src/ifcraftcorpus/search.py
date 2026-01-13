"""
Unified search API for the IF Craft Corpus.

This module provides the main :class:`Corpus` interface that combines
FTS5 keyword search with optional semantic vector search. It's the
recommended entry point for most users.

Features:
    - Automatic corpus discovery (bundled or custom)
    - Keyword search via SQLite FTS5 with BM25 ranking
    - Semantic search via sentence-transformers (optional)
    - Hybrid search combining both methods
    - Cluster filtering for scoped searches

Example:
    Basic usage with bundled corpus::

        from ifcraftcorpus import Corpus

        corpus = Corpus()
        results = corpus.search("dialogue subtext techniques")
        for r in results:
            print(f"{r.source}: {r.content[:100]}...")

    With semantic search::

        corpus = Corpus(embeddings_path=Path("embeddings/"))
        results = corpus.search("scary atmosphere", mode="semantic")

    As context manager::

        with Corpus() as corpus:
            doc = corpus.get_document("dialogue_craft")
            print(doc["title"])

Classes:
    Corpus: Main search interface for the corpus.
    CorpusResult: Unified search result from either search mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from ifcraftcorpus.index import CorpusIndex

if TYPE_CHECKING:
    from ifcraftcorpus.embeddings import EmbeddingIndex
    from ifcraftcorpus.providers import EmbeddingProvider


@dataclass
class CorpusResult:
    """A unified search result from keyword or semantic search.

    Represents a single matching section or document summary. Results
    include metadata and a relevance score from the search method used.

    Attributes:
        document_name: Name of the source document (filename without .md).
        title: Document title from frontmatter.
        cluster: Topic cluster the document belongs to.
        section_heading: Heading of the matched section, or None if
            the match is from the document summary.
        content: The matched text content.
        score: Relevance score. For keyword search, this is the BM25 score.
            For semantic search, this is cosine similarity (0-1).
        topics: List of topic keywords from the document.
        search_type: Either "keyword" (FTS5) or "semantic" (vector).

    Example:
        >>> results = corpus.search("dialogue")
        >>> for r in results:
        ...     print(f"[{r.search_type}] {r.source}: {r.score:.2f}")
    """

    document_name: str
    title: str
    cluster: str
    section_heading: str | None
    content: str
    score: float
    topics: list[str]
    search_type: Literal["keyword", "semantic"]

    @property
    def source(self) -> str:
        """Get a human-readable source reference.

        Returns:
            Formatted string like "document_name > Section Heading" or
            just "document_name" if no section heading.
        """
        if self.section_heading:
            return f"{self.document_name} > {self.section_heading}"
        return self.document_name


class Corpus:
    """Main interface for searching the IF Craft Corpus.

    Provides unified access to the corpus with support for keyword search
    (always available) and semantic search (when embeddings are provided).
    This is the recommended entry point for most users.

    The corpus automatically discovers bundled content when installed as
    a package, or can be pointed at a custom corpus directory.

    Can be used as a context manager for automatic resource cleanup.

    Attributes:
        has_semantic_search: Whether semantic search is available.

    Example:
        Basic usage::

            from ifcraftcorpus import Corpus

            corpus = Corpus()
            results = corpus.search("dialogue techniques")
            for r in results:
                print(f"{r.source}: {r.content[:100]}")

        With pre-built index for faster startup::

            corpus = Corpus(index_path=Path("corpus.db"))

        As context manager::

            with Corpus() as corpus:
                clusters = corpus.list_clusters()
                print(f"Available clusters: {clusters}")

    See Also:
        :class:`CorpusResult`: The result type returned by search.
        :class:`~ifcraftcorpus.index.CorpusIndex`: Lower-level FTS5 interface.
    """

    def __init__(
        self,
        *,
        corpus_dir: Path | None = None,
        index_path: Path | None = None,
        embeddings_path: Path | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        use_bundled: bool = True,
    ) -> None:
        """Initialize the corpus.

        Args:
            corpus_dir: Path to corpus markdown files. If None and use_bundled
                is True, attempts to find bundled corpus files.
            index_path: Path to pre-built SQLite index file. If None, builds
                an in-memory index on first search (slower startup but no
                disk storage required).
            embeddings_path: Path to pre-built embeddings directory. If None,
                semantic search will be unavailable and only keyword search
                can be used.
            embedding_provider: Optional EmbeddingProvider for building/using
                embeddings. If provided with embeddings_path, can load existing
                embeddings or build new ones with build_embeddings().
            use_bundled: If True (default) and corpus_dir is None, looks for
                bundled corpus files in the package installation or development
                directory.

        Raises:
            ValueError: If no corpus directory can be found and use_bundled
                is True.

        Example:
            With auto-detected provider::

                from ifcraftcorpus import Corpus
                from ifcraftcorpus.providers import get_embedding_provider

                provider = get_embedding_provider()
                corpus = Corpus(
                    embeddings_path=Path("embeddings/"),
                    embedding_provider=provider
                )
                # Build if not exists
                if not corpus.has_semantic_search:
                    corpus.build_embeddings()
        """
        self._corpus_dir = corpus_dir
        self._index_path = index_path
        self._embeddings_path = embeddings_path
        self._embedding_provider = embedding_provider
        self._use_bundled = use_bundled

        self._fts_index: CorpusIndex | None = None
        self._embedding_index: EmbeddingIndex | None = None  # Lazy loaded

    def _get_corpus_dir(self) -> Path:
        """Get the corpus directory path.

        Returns:
            Path to the corpus directory.

        Raises:
            ValueError: If no corpus directory can be found.
        """
        if self._corpus_dir:
            return self._corpus_dir

        if self._use_bundled:
            # Try to find bundled corpus
            try:
                import sys

                import ifcraftcorpus

                # Check for installed shared data (pip install)
                bundled = Path(sys.prefix) / "share" / "ifcraftcorpus" / "corpus"
                if bundled.exists():
                    return bundled

                # Check relative to package (development mode / editable install)
                pkg_dir = Path(ifcraftcorpus.__file__).parent
                dev_corpus = pkg_dir.parent.parent / "corpus"
                if dev_corpus.exists():
                    return dev_corpus
            except Exception:
                pass

        raise ValueError(
            "No corpus directory found. Provide corpus_dir or install package with bundled corpus."
        )

    def _get_fts_index(self) -> CorpusIndex:
        """Get or create the FTS5 index.

        Lazily initializes the index on first access. If an index_path was
        provided and exists, loads from disk. Otherwise builds in-memory.

        Returns:
            The FTS5 CorpusIndex instance.
        """
        if self._fts_index is None:
            if self._index_path and self._index_path.exists():
                self._fts_index = CorpusIndex(self._index_path)
            else:
                # Build in-memory index
                self._fts_index = CorpusIndex()
                corpus_dir = self._get_corpus_dir()
                self._fts_index.build_from_directory(corpus_dir)
        return self._fts_index

    def _get_embedding_index(self) -> EmbeddingIndex | None:
        """Get the embedding index for semantic search.

        Lazily loads the embedding index if embeddings_path was provided.
        Returns None if embeddings are not available (path not provided,
        files don't exist, or no provider available).

        Returns:
            EmbeddingIndex instance or None if unavailable.
        """
        if self._embedding_index is None and self._embeddings_path:
            try:
                from ifcraftcorpus.embeddings import EmbeddingIndex

                if (
                    self._embeddings_path.exists()
                    and (self._embeddings_path / "metadata.json").exists()
                ):
                    self._embedding_index = EmbeddingIndex.load(
                        self._embeddings_path, provider=self._embedding_provider
                    )
            except ImportError:
                pass  # embeddings not available
        return self._embedding_index

    def build_embeddings(self, *, force: bool = False) -> int:
        """Build embeddings for the corpus.

        Requires an embedding_provider to be configured. Builds embeddings
        for all documents and sections, saving to embeddings_path.

        Args:
            force: If True, rebuild even if embeddings exist.

        Returns:
            Number of items embedded.

        Raises:
            ValueError: If no embedding_provider or embeddings_path configured.

        Example:
            >>> from ifcraftcorpus import Corpus
            >>> from ifcraftcorpus.providers import OllamaEmbeddings
            >>>
            >>> corpus = Corpus(
            ...     embeddings_path=Path("embeddings/"),
            ...     embedding_provider=OllamaEmbeddings()
            ... )
            >>> count = corpus.build_embeddings()
            >>> print(f"Embedded {count} items")
        """
        if not self._embedding_provider:
            raise ValueError("No embedding_provider configured")
        if not self._embeddings_path:
            raise ValueError("No embeddings_path configured")

        # Check if already exists
        if (
            not force
            and self._embeddings_path.exists()
            and (self._embeddings_path / "metadata.json").exists()
        ):
            return 0

        from ifcraftcorpus.embeddings import EmbeddingIndex

        embedding_index = EmbeddingIndex(provider=self._embedding_provider)

        count = 0
        for doc_info in self.list_documents():
            doc = self.get_document(doc_info["name"])
            if not doc:
                continue

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
            count += 1

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
                    count += 1

        # Save
        embedding_index.save(self._embeddings_path)
        self._embedding_index = embedding_index

        return count

    def search(
        self,
        query: str,
        *,
        cluster: str | None = None,
        limit: int = 10,
        mode: Literal["keyword", "semantic", "hybrid"] = "keyword",
    ) -> list[CorpusResult]:
        """Search the corpus for matching content.

        Performs a search using the specified mode. Keyword search uses
        SQLite FTS5 with BM25 ranking. Semantic search uses vector
        similarity with sentence-transformers embeddings.

        Args:
            query: Search query text. For keyword mode, supports FTS5
                syntax (phrases, boolean operators, etc.).
            cluster: Optional cluster name to filter results. Only
                returns matches from documents in the specified cluster.
            limit: Maximum number of results to return. Default 10.
            mode: Search mode to use:

                - ``"keyword"``: FTS5 full-text search (default, always available)
                - ``"semantic"``: Vector similarity search (requires embeddings)
                - ``"hybrid"``: Both methods, deduplicated and merged

        Returns:
            List of :class:`CorpusResult` objects. Results are sorted by
            relevance score (descending). For hybrid mode, results from
            both methods are merged and deduplicated.

        Note:
            Semantic and hybrid modes require embeddings to be configured.
            If embeddings are unavailable, these modes silently fall back
            to empty results for the semantic component.

        Example:
            >>> # Keyword search
            >>> results = corpus.search("dialogue techniques")

            >>> # With cluster filter
            >>> results = corpus.search("tension", cluster="emotional-design")

            >>> # Semantic search (if embeddings available)
            >>> results = corpus.search("scary atmosphere", mode="semantic")
        """
        results: list[CorpusResult] = []

        if mode in ("keyword", "hybrid"):
            fts_results = self._get_fts_index().search(query, cluster=cluster, limit=limit)
            for r in fts_results:
                results.append(
                    CorpusResult(
                        document_name=r.document_name,
                        title=r.title,
                        cluster=r.cluster,
                        section_heading=r.section_heading,
                        content=r.content,
                        score=r.score,
                        topics=r.topics,
                        search_type="keyword",
                    )
                )

        if mode in ("semantic", "hybrid"):
            embedding_index = self._get_embedding_index()
            if embedding_index:
                semantic_results = embedding_index.search(query, top_k=limit, cluster=cluster)
                for metadata, score in semantic_results:
                    results.append(
                        CorpusResult(
                            document_name=metadata["document_name"],
                            title=metadata["title"],
                            cluster=metadata["cluster"],
                            section_heading=metadata.get("section_heading"),
                            content=metadata["content"],
                            score=score,
                            topics=metadata.get("topics", []),
                            search_type="semantic",
                        )
                    )

        # Deduplicate and sort by score
        if mode == "hybrid":
            seen: set[tuple[str, str | None]] = set()
            unique_results: list[CorpusResult] = []
            sorted_results: list[CorpusResult] = sorted(
                results, key=lambda x: x.score, reverse=True
            )
            for result in sorted_results:
                key = (result.document_name, result.section_heading)
                if key not in seen:
                    seen.add(key)
                    unique_results.append(result)
            results = unique_results[:limit]

        return results

    def get_document(self, name: str) -> dict[str, Any] | None:
        """Get a document by name with all its sections.

        Retrieves complete document data including metadata and all
        parsed sections.

        Args:
            name: Document name (filename stem without .md extension).
                Use :meth:`list_documents` to discover available names.

        Returns:
            Dict with document data or None if not found. See
            :meth:`~ifcraftcorpus.index.CorpusIndex.get_document` for
            the dict structure.

        Example:
            >>> doc = corpus.get_document("dialogue_craft")
            >>> if doc:
            ...     print(doc["title"])
            ...     print(f"{len(doc['sections'])} sections")
        """
        return self._get_fts_index().get_document(name)

    def list_documents(self) -> list[dict[str, str]]:
        """List all documents in the corpus.

        Returns:
            List of dicts with document metadata (name, title, cluster,
            topics). Documents are sorted by cluster, then by name.
        """
        return self._get_fts_index().list_documents()

    def list_clusters(self) -> list[str]:
        """List all available clusters.

        Returns:
            Alphabetically sorted list of cluster names.
        """
        return self._get_fts_index().list_clusters()

    def document_count(self) -> int:
        """Get total number of documents in the corpus.

        Returns:
            Count of indexed documents.
        """
        return self._get_fts_index().document_count()

    @property
    def has_semantic_search(self) -> bool:
        """Check if semantic search is available.

        Returns:
            True if embeddings are loaded and semantic search can be used.
        """
        return self._get_embedding_index() is not None

    def close(self) -> None:
        """Close resources and release database connections.

        Safe to call multiple times. After closing, the corpus can still
        be used (resources will be re-initialized on next access).
        """
        if self._fts_index:
            self._fts_index.close()
            self._fts_index = None

    def __enter__(self) -> Corpus:
        """Enter context manager, returning self."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager, closing resources."""
        self.close()
