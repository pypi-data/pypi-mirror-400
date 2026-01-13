"""
Embedding providers for corpus vector search.

Supports multiple backends:
- Ollama (local, recommended for Docker/dev)
- OpenAI (cloud, requires API key)
- SentenceTransformers (local, requires torch - heavyweight)

Provider selection via environment:
- EMBEDDING_PROVIDER: "ollama", "openai", or "sentence-transformers"
- OLLAMA_HOST: Ollama server URL (default: http://localhost:11434)
- OPENAI_API_KEY: OpenAI API key (required for openai provider)
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


# Default embedding models per provider
DEFAULT_MODELS = {
    "ollama": "nomic-embed-text",
    "openai": "text-embedding-3-small",
    "sentence-transformers": "all-MiniLM-L6-v2",
}

# Embedding dimensions per model
MODEL_DIMENSIONS = {
    # Ollama models
    "nomic-embed-text": 768,
    "mxbai-embed-large": 1024,
    "all-minilm": 384,
    # OpenAI models
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
    # Sentence-transformers models
    "all-MiniLM-L6-v2": 384,
    "all-mpnet-base-v2": 768,
    "multi-qa-mpnet-base-dot-v1": 768,
}


@dataclass
class EmbeddingResult:
    """Result from embedding operation."""

    embeddings: list[list[float]]
    model: str
    dimension: int
    token_count: int | None = None


class EmbeddingProvider(ABC):
    """Abstract embedding provider interface."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Model name being used."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector dimension."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier (ollama, openai, sentence-transformers)."""
        ...

    @abstractmethod
    def embed(self, texts: list[str]) -> EmbeddingResult:
        """
        Embed multiple texts synchronously.

        Args:
            texts: List of text strings to embed

        Returns:
            EmbeddingResult with vectors and metadata
        """
        ...

    def embed_single(self, text: str) -> list[float]:
        """Embed a single text string."""
        result = self.embed([text])
        return result.embeddings[0]

    @abstractmethod
    def check_availability(self) -> bool:
        """Check if the provider is available."""
        ...


class OllamaEmbeddings(EmbeddingProvider):
    """
    Ollama embedding provider.

    Uses local Ollama instance for embeddings.
    Recommended model: nomic-embed-text (768 dimensions)

    Requires: httpx (pip install httpx)
    """

    def __init__(
        self,
        model: str | None = None,
        host: str | None = None,
    ):
        """
        Initialize Ollama embeddings.

        Args:
            model: Embedding model name (default: nomic-embed-text)
            host: Ollama host URL (default: http://localhost:11434)
        """
        self._model = model or DEFAULT_MODELS["ollama"]
        self._host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self._dimension = MODEL_DIMENSIONS.get(self._model, 768)

    @property
    def model(self) -> str:
        return self._model

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def provider_name(self) -> str:
        return "ollama"

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """Embed texts using Ollama."""
        import httpx

        embeddings: list[list[float]] = []

        with httpx.Client(timeout=60.0) as client:
            for text in texts:
                response = client.post(
                    f"{self._host}/api/embeddings",
                    json={
                        "model": self._model,
                        "prompt": text,
                    },
                )
                response.raise_for_status()
                data = response.json()
                embeddings.append(data["embedding"])

        return EmbeddingResult(
            embeddings=embeddings,
            model=self._model,
            dimension=self._dimension,
        )

    def check_availability(self) -> bool:
        """Check if Ollama is available with the embedding model."""
        try:
            import httpx
        except ImportError:
            logger.debug("httpx not installed, Ollama provider unavailable")
            return False

        try:
            with httpx.Client(timeout=5.0) as client:
                # Check if Ollama is running
                response = client.get(f"{self._host}/api/tags")
                if response.status_code != 200:
                    return False

                # Check if model is available
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]

                # Model names may include :latest suffix
                model_base = self._model.split(":")[0]
                return any(m.startswith(model_base) for m in models)

        except httpx.RequestError as e:
            logger.debug(f"Ollama availability check failed: {e}")
            return False


class OpenAIEmbeddings(EmbeddingProvider):
    """
    OpenAI embedding provider.

    Requires OPENAI_API_KEY environment variable.
    Default model: text-embedding-3-small (1536 dimensions)

    Requires: httpx (pip install httpx)
    """

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ):
        """
        Initialize OpenAI embeddings.

        Args:
            model: Embedding model name (default: text-embedding-3-small)
            api_key: OpenAI API key (default: from OPENAI_API_KEY env)
        """
        self._model = model or DEFAULT_MODELS["openai"]
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._dimension = MODEL_DIMENSIONS.get(self._model, 1536)

    @property
    def model(self) -> str:
        return self._model

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def provider_name(self) -> str:
        return "openai"

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """Embed texts using OpenAI API."""
        import httpx

        if not self._api_key:
            raise ValueError("OpenAI API key not configured")

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "input": texts,
                },
            )
            response.raise_for_status()
            data = response.json()

        embeddings = [item["embedding"] for item in data["data"]]
        token_count = data.get("usage", {}).get("total_tokens")

        return EmbeddingResult(
            embeddings=embeddings,
            model=self._model,
            dimension=self._dimension,
            token_count=token_count,
        )

    def check_availability(self) -> bool:
        """Check if OpenAI API is available."""
        if not self._api_key:
            return False

        try:
            import httpx
        except ImportError:
            logger.debug("httpx not installed, OpenAI provider unavailable")
            return False

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                return response.status_code == 200

        except httpx.RequestError as e:
            logger.debug(f"OpenAI availability check failed: {e}")
            return False


class SentenceTransformersEmbeddings(EmbeddingProvider):
    """
    Sentence-transformers embedding provider.

    Uses local sentence-transformers models. Heavyweight but no external service needed.
    Default model: all-MiniLM-L6-v2 (384 dimensions)

    Requires: sentence-transformers (pip install sentence-transformers)
    """

    def __init__(
        self,
        model: str | None = None,
        lazy_load: bool = True,
    ):
        """
        Initialize sentence-transformers embeddings.

        Args:
            model: Model name (default: all-MiniLM-L6-v2)
            lazy_load: If True, load model on first use
        """
        self._model_name = model or DEFAULT_MODELS["sentence-transformers"]
        self._dimension = MODEL_DIMENSIONS.get(self._model_name, 384)
        self._model_instance: SentenceTransformer | None = None

        if not lazy_load:
            self._load_model()

    def _load_model(self) -> SentenceTransformer:
        """Load the sentence transformer model."""
        if self._model_instance is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as e:
                raise ImportError(
                    "sentence-transformers is required for this provider. "
                    "Install with: pip install sentence-transformers"
                ) from e
            self._model_instance = SentenceTransformer(self._model_name)
        return self._model_instance

    @property
    def model(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def provider_name(self) -> str:
        return "sentence-transformers"

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """Embed texts using sentence-transformers."""
        model = self._load_model()
        embeddings = model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        return EmbeddingResult(
            embeddings=[emb.tolist() for emb in embeddings],
            model=self._model_name,
            dimension=self._dimension,
        )

    def check_availability(self) -> bool:
        """Check if sentence-transformers is available."""
        try:
            import sentence_transformers  # noqa: F401

            return True
        except ImportError:
            return False


def get_embedding_provider(
    provider_name: str | None = None,
    model: str | None = None,
) -> EmbeddingProvider | None:
    """
    Get an embedding provider based on configuration.

    Selection order:
    1. Explicit provider_name parameter
    2. EMBEDDING_PROVIDER environment variable
    3. Auto-detect available provider (Ollama -> OpenAI -> SentenceTransformers)

    Args:
        provider_name: Explicit provider name ("ollama", "openai", "sentence-transformers")
        model: Optional model override

    Returns:
        Configured EmbeddingProvider or None if none available
    """
    # Determine provider
    name = provider_name or os.getenv("EMBEDDING_PROVIDER")

    if name:
        name = name.lower()
        provider: EmbeddingProvider
        if name == "ollama":
            provider = OllamaEmbeddings(model=model)
        elif name == "openai":
            provider = OpenAIEmbeddings(model=model)
        elif name in ("sentence-transformers", "st", "local"):
            provider = SentenceTransformersEmbeddings(model=model)
        else:
            logger.warning(f"Unknown embedding provider: {name}")
            return None

        if provider.check_availability():
            return provider
        logger.warning(f"Embedding provider {name} not available")
        return None

    # Auto-detect: try Ollama first, then OpenAI, then SentenceTransformers
    ollama = OllamaEmbeddings(model=model)
    if ollama.check_availability():
        logger.info(f"Using Ollama embeddings ({ollama.model})")
        return ollama

    openai = OpenAIEmbeddings(model=model)
    if openai.check_availability():
        logger.info(f"Using OpenAI embeddings ({openai.model})")
        return openai

    st = SentenceTransformersEmbeddings(model=model)
    if st.check_availability():
        logger.info(f"Using SentenceTransformers embeddings ({st.model})")
        return st

    logger.warning("No embedding provider available")
    return None
