"""
Semantic embeddings for vector search.

This module provides vector embedding support for semantic (meaning-based)
search. It supports multiple embedding providers:

- **Ollama** (local, lightweight) - recommended for Docker
- **OpenAI** (cloud) - requires API key
- **SentenceTransformers** (local, heavyweight) - requires torch

Installation extras:
    - ``pip install ifcraftcorpus[embeddings-api]`` - Ollama/OpenAI (lightweight)
    - ``pip install ifcraftcorpus[embeddings]`` - SentenceTransformers (heavyweight)

Features:
    - Dense vector embeddings for semantic matching
    - Cosine similarity search
    - Persistence to disk for fast loading
    - Integration with CorpusIndex

Example:
    Using Ollama (lightweight, Docker-friendly)::

        from ifcraftcorpus.embeddings import EmbeddingIndex
        from ifcraftcorpus.providers import OllamaEmbeddings

        provider = OllamaEmbeddings()  # Uses nomic-embed-text
        index = EmbeddingIndex(provider=provider)
        index.add_texts(["Creating tension"], [{"doc": "dialogue"}])
        results = index.search("building suspense")

    Using auto-detection::

        from ifcraftcorpus.embeddings import EmbeddingIndex
        from ifcraftcorpus.providers import get_embedding_provider

        provider = get_embedding_provider()  # Auto-detect available
        if provider:
            index = EmbeddingIndex(provider=provider)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

if TYPE_CHECKING:
    from ifcraftcorpus.index import CorpusIndex
    from ifcraftcorpus.providers import EmbeddingProvider

logger = logging.getLogger(__name__)

# Default model for backward compatibility (sentence-transformers)
DEFAULT_MODEL = "all-MiniLM-L6-v2"


class EmbeddingIndex:
    """Vector embedding index for semantic search.

    Provides semantic search using dense vector embeddings. Supports
    multiple providers (Ollama, OpenAI, SentenceTransformers) via the
    provider parameter, or falls back to sentence-transformers for
    backward compatibility.

    Attributes:
        model_name: Name of the embedding model being used.
        provider_name: Name of the provider (ollama, openai, sentence-transformers).

    Example:
        Using a provider::

            >>> from ifcraftcorpus.providers import OllamaEmbeddings
            >>> provider = OllamaEmbeddings()
            >>> index = EmbeddingIndex(provider=provider)
            >>> index.add_texts(["text"], [{"doc": "name"}])
            >>> results = index.search("query")

        Legacy usage (sentence-transformers)::

            >>> index = EmbeddingIndex(model_name="all-MiniLM-L6-v2")
            >>> index.add_texts(["text"], [{"doc": "name"}])
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        *,
        provider: EmbeddingProvider | None = None,
        lazy_load: bool = True,
    ) -> None:
        """Initialize the embedding index.

        Args:
            model_name: Model name (used for sentence-transformers fallback
                or when loading from disk). Ignored if provider is given.
            provider: Embedding provider to use. If None, falls back to
                sentence-transformers for backward compatibility.
            lazy_load: If True (default), model loads on first use.

        Raises:
            ImportError: If no provider given and sentence-transformers
                is not installed.
        """
        self._provider = provider
        self._embeddings: np.ndarray | None = None
        self._metadata: list[dict[str, Any]] = []
        self._st_model: SentenceTransformer | None = None

        # For backward compatibility / persistence
        if provider:
            self.model_name = provider.model
            self._provider_name = provider.provider_name
        else:
            self.model_name = model_name
            self._provider_name = "sentence-transformers"
            # Lazy-load sentence-transformers model
            if not lazy_load:
                self._load_st_model()

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return self._provider_name

    def _load_st_model(self) -> SentenceTransformer:
        """Load sentence-transformers model (fallback)."""
        if self._st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as e:
                raise ImportError(
                    "No embedding provider available. Either:\n"
                    "  - Pass a provider (OllamaEmbeddings, OpenAIEmbeddings)\n"
                    "  - Install sentence-transformers: pip install ifcraftcorpus[embeddings]"
                ) from e
            self._st_model = SentenceTransformer(self.model_name)
        return self._st_model

    def _embed(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings using provider or fallback."""
        if self._provider:
            result = self._provider.embed(texts)
            return np.array(result.embeddings)
        else:
            # Fallback to sentence-transformers
            model = self._load_st_model()
            embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
            return np.asarray(embeddings)

    def add_texts(
        self,
        texts: list[str],
        metadata: list[dict[str, Any]],
    ) -> None:
        """Add texts with metadata to the index.

        Generates embeddings for the provided texts and stores them
        along with their metadata.

        Args:
            texts: List of text strings to embed.
            metadata: List of metadata dicts, one per text.

        Raises:
            ValueError: If texts and metadata have different lengths.
        """
        if len(texts) != len(metadata):
            raise ValueError("texts and metadata must have same length")

        new_embeddings = self._embed(texts)

        if self._embeddings is None:
            self._embeddings = new_embeddings
        else:
            self._embeddings = np.vstack([self._embeddings, new_embeddings])

        self._metadata.extend(metadata)

    def search(
        self,
        query: str,
        *,
        top_k: int = 10,
        cluster: str | None = None,
    ) -> list[tuple[dict[str, Any], float]]:
        """Search for semantically similar texts.

        Args:
            query: Search query text.
            top_k: Maximum number of results to return.
            cluster: Optional cluster name to filter results.

        Returns:
            List of (metadata, similarity_score) tuples, sorted by
            similarity in descending order.
        """
        if self._embeddings is None or len(self._metadata) == 0:
            return []

        query_embedding = self._embed([query])[0]

        # Compute cosine similarities
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = self._embeddings / np.linalg.norm(self._embeddings, axis=1, keepdims=True)

        similarities = np.dot(embeddings_norm, query_norm)

        # Get top-k indices
        if cluster:
            mask = np.array([m.get("cluster") == cluster for m in self._metadata])
            filtered_similarities = np.where(mask, similarities, -np.inf)
            top_indices = np.argsort(filtered_similarities)[-top_k:][::-1]
        else:
            top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                results.append((self._metadata[idx], float(similarities[idx])))

        return results

    def save(self, path: Path) -> None:
        """Save the embedding index to disk.

        Args:
            path: Directory path to save the index.
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        if self._embeddings is not None:
            np.save(path / "embeddings.npy", self._embeddings)

        with open(path / "metadata.json", "w") as f:
            json.dump(
                {
                    "model_name": self.model_name,
                    "provider_name": self._provider_name,
                    "metadata": self._metadata,
                },
                f,
            )

    @classmethod
    def load(
        cls,
        path: Path,
        *,
        provider: EmbeddingProvider | None = None,
    ) -> EmbeddingIndex:
        """Load an embedding index from disk.

        Args:
            path: Directory path containing the saved index.
            provider: Optional provider for search queries. If not given,
                will attempt to auto-detect or use sentence-transformers.

        Returns:
            Loaded EmbeddingIndex ready for searching.
        """
        path = Path(path)

        with open(path / "metadata.json") as f:
            data = json.load(f)

        # Try to get a matching provider if none given
        if provider is None:
            saved_provider = data.get("provider_name", "sentence-transformers")
            saved_model = data["model_name"]

            # Try to get matching provider
            try:
                from ifcraftcorpus.providers import get_embedding_provider

                provider = get_embedding_provider(provider_name=saved_provider, model=saved_model)
            except ImportError:
                logger.warning(
                    "Could not import providers (missing [embeddings-api]?). "
                    "Falling back to sentence-transformers."
                )

        index = cls(model_name=data["model_name"], provider=provider)
        index._metadata = data["metadata"]
        index._provider_name = data.get("provider_name", "sentence-transformers")

        embeddings_path = path / "embeddings.npy"
        if embeddings_path.exists():
            index._embeddings = np.load(embeddings_path)

            # Validate dimension if provider is available
            if provider is not None and index._embeddings is not None:
                saved_dim = index._embeddings.shape[1]
                provider_dim = provider.dimension
                if saved_dim != provider_dim:
                    logger.warning(
                        f"Dimension mismatch: saved embeddings have {saved_dim}d, "
                        f"but provider {provider.provider_name} uses {provider_dim}d. "
                        "Searches may fail or produce incorrect results."
                    )

        return index

    def __len__(self) -> int:
        """Return the number of indexed items."""
        return len(self._metadata)


def build_embeddings_from_index(
    corpus_index: CorpusIndex,
    model_name: str = DEFAULT_MODEL,
    *,
    provider: EmbeddingProvider | None = None,
) -> EmbeddingIndex:
    """Build an embedding index from an existing CorpusIndex.

    Args:
        corpus_index: A populated CorpusIndex.
        model_name: Model name (for sentence-transformers fallback).
        provider: Embedding provider to use. If None, uses sentence-transformers.

    Returns:
        A new EmbeddingIndex containing embeddings for all documents.

    Example:
        Using Ollama::

            from ifcraftcorpus.providers import OllamaEmbeddings
            provider = OllamaEmbeddings()
            embeddings = build_embeddings_from_index(index, provider=provider)
    """
    embedding_index = EmbeddingIndex(model_name, provider=provider)

    for doc_info in corpus_index.list_documents():
        doc = corpus_index.get_document(doc_info["name"])
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
                    "topics": doc["topics"],
                }
            ],
        )

        # Add sections
        for section in doc["sections"]:
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
                            "topics": doc["topics"],
                        }
                    ],
                )

    return embedding_index
