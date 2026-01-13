"""
SQLite FTS5 full-text search index.

This module provides a SQLite-based full-text search index for the corpus
using FTS5 with BM25 ranking. It supports:

- Fast keyword-based search with relevance ranking
- Boolean operators (AND, OR, NOT)
- Phrase search with exact matching
- Prefix matching for autocomplete
- Column-specific queries (title:, cluster:, etc.)
- Cluster filtering for scoped searches

The index uses Porter stemming and Unicode tokenization for
language-aware search.

Example:
    Build and search an index::

        from pathlib import Path
        from ifcraftcorpus.index import CorpusIndex

        # Build index from corpus files
        index = CorpusIndex("corpus.db")
        index.build_from_directory(Path("corpus"))

        # Search with FTS5 syntax
        results = index.search("dialogue AND subtext")
        for r in results:
            print(f"{r.source}: {r.score:.2f}")

    Use as context manager::

        with CorpusIndex() as index:
            index.build_from_directory(Path("corpus"))
            results = index.search("pacing")

Classes:
    CorpusIndex: Main SQLite FTS5 index class.
    SearchResult: Dataclass representing a search result.

Functions:
    build_index: Convenience function to build and save an index.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ifcraftcorpus.parser import Document, parse_directory


@dataclass
class SearchResult:
    """A search result from the corpus FTS5 index.

    Represents a single matching section or document summary from a search.
    Results are ranked by BM25 relevance score.

    Attributes:
        document_name: Name of the source document (filename without .md).
        title: Document title from frontmatter.
        cluster: Topic cluster the document belongs to.
        section_heading: Heading of the matched section, or None if
            the match is from the document summary.
        content: The matched text content (section body or summary).
        score: BM25 relevance score. Higher values indicate better matches.
            Typical range is 0-20, but can vary based on query complexity.
        topics: List of topic keywords from the document.

    Example:
        >>> results = index.search("dialogue")
        >>> for r in results:
        ...     print(f"{r.source} (score: {r.score:.2f})")
        ...     print(f"  Topics: {', '.join(r.topics)}")
    """

    document_name: str
    title: str
    cluster: str
    section_heading: str | None
    content: str
    score: float
    topics: list[str]

    @property
    def source(self) -> str:
        """Get a human-readable source reference.

        Returns:
            A formatted string like "document_name > Section Heading" or
            just "document_name" if no section heading.
        """
        if self.section_heading:
            return f"{self.document_name} > {self.section_heading}"
        return self.document_name


class CorpusIndex:
    """SQLite FTS5 full-text search index for the corpus.

    Provides fast keyword-based search using SQLite's FTS5 extension with
    BM25 relevance ranking. The index stores documents and their sections
    separately, enabling both document-level and section-level search.

    The index supports FTS5 query syntax including:
        - Simple keywords: ``dialogue``
        - Phrases: ``"character voice"``
        - Boolean: ``tension AND suspense``, ``horror NOT comedy``
        - Prefix: ``narrat*``
        - Column-specific: ``title:craft``, ``cluster:genre-conventions``

    Can be used as a context manager for automatic resource cleanup.

    Attributes:
        db_path: Path to the SQLite database file, or ":memory:" for in-memory.
        SCHEMA: SQL schema definition for the three tables (documents,
            sections, corpus_fts).

    Example:
        >>> # In-memory index for testing
        >>> with CorpusIndex() as index:
        ...     index.build_from_directory(Path("corpus"))
        ...     results = index.search("dialogue subtext")
        ...     print(f"Found {len(results)} results")

        >>> # Persistent index on disk
        >>> index = CorpusIndex("corpus.db")
        >>> index.build_from_directory(Path("corpus"))
        >>> index.close()

    See Also:
        :class:`SearchResult`: The result type returned by search.
        :func:`build_index`: Convenience function for building and saving.
    """

    SCHEMA = """
    -- Documents table
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        path TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        cluster TEXT NOT NULL,
        topics TEXT NOT NULL,
        content_hash TEXT NOT NULL
    );

    -- Sections table
    CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY,
        document_id INTEGER NOT NULL,
        heading TEXT NOT NULL,
        level INTEGER NOT NULL,
        content TEXT NOT NULL,
        line_start INTEGER NOT NULL,
        FOREIGN KEY (document_id) REFERENCES documents(id)
    );

    -- FTS5 virtual table for full-text search
    CREATE VIRTUAL TABLE IF NOT EXISTS corpus_fts USING fts5(
        document_name,
        title,
        cluster,
        topics,
        section_heading,
        content,
        tokenize='porter unicode61'
    );
    """

    def __init__(self, db_path: Path | str = ":memory:") -> None:
        """Initialize the corpus index.

        Args:
            db_path: Path to SQLite database file, or ':memory:' for in-memory.
        """
        self.db_path = Path(db_path) if db_path != ":memory:" else db_path
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        """Get or create the database connection.

        Lazily initializes the SQLite connection on first access and
        sets up the database schema if needed.

        Returns:
            Active SQLite connection with Row factory enabled.
        """
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self.db_path) if isinstance(self.db_path, Path) else self.db_path
            )
            self._conn.row_factory = sqlite3.Row
            self._init_schema()
        return self._conn

    def _init_schema(self) -> None:
        """Initialize the database schema.

        Creates the documents, sections, and corpus_fts tables if they
        don't already exist.
        """
        self.conn.executescript(self.SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        """Close the database connection and release resources.

        Safe to call multiple times. After closing, the connection will
        be re-established on next access to :attr:`conn`.
        """
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> CorpusIndex:
        """Enter context manager, returning self."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager, closing the database connection."""
        self.close()

    def add_document(self, doc: Document) -> int:
        """Add a parsed document to the index.

        Inserts the document metadata and all its sections into the database.
        If a document with the same name already exists, it is replaced.
        Each section is also added to the FTS5 virtual table for search.

        Args:
            doc: Parsed :class:`~ifcraftcorpus.parser.Document` to add.

        Returns:
            The database ID assigned to the document.

        Note:
            The document summary is also indexed separately to enable
            searching by summary content.
        """
        cursor = self.conn.cursor()

        # Insert or replace document
        cursor.execute(
            """
            INSERT OR REPLACE INTO documents
            (name, path, title, summary, cluster, topics, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc.name,
                str(doc.path),
                doc.title,
                doc.summary,
                doc.cluster,
                ",".join(doc.topics),
                doc.content_hash,
            ),
        )
        doc_id = cursor.lastrowid
        assert doc_id is not None

        # Delete old sections
        cursor.execute("DELETE FROM sections WHERE document_id = ?", (doc_id,))

        # Insert sections
        for section in doc.sections:
            cursor.execute(
                """
                INSERT INTO sections (document_id, heading, level, content, line_start)
                VALUES (?, ?, ?, ?, ?)
                """,
                (doc_id, section.heading, section.level, section.content, section.line_start),
            )

            # Add to FTS index
            cursor.execute(
                """
                INSERT INTO corpus_fts
                (document_name, title, cluster, topics, section_heading, content)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    doc.name,
                    doc.title,
                    doc.cluster,
                    " ".join(doc.topics),
                    section.heading,
                    section.content,
                ),
            )

        # Also index the document summary
        cursor.execute(
            """
            INSERT INTO corpus_fts
            (document_name, title, cluster, topics, section_heading, content)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                doc.name,
                doc.title,
                doc.cluster,
                " ".join(doc.topics),
                None,
                doc.summary,
            ),
        )

        self.conn.commit()
        return doc_id

    def build_from_directory(self, corpus_dir: Path) -> int:
        """Build the index from all documents in a corpus directory.

        Recursively parses all markdown files in the directory and adds
        them to the index. This is the primary way to populate a new index.

        Args:
            corpus_dir: Path to the corpus root directory. All .md files
                in subdirectories will be parsed and indexed.

        Returns:
            Number of documents successfully indexed.

        Example:
            >>> index = CorpusIndex("corpus.db")
            >>> count = index.build_from_directory(Path("corpus"))
            >>> print(f"Indexed {count} documents")
        """
        documents = parse_directory(corpus_dir)
        for doc in documents:
            self.add_document(doc)
        return len(documents)

    def search(
        self,
        query: str,
        *,
        cluster: str | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Search the corpus using FTS5 full-text search.

        Performs a keyword search using SQLite FTS5 with BM25 ranking.
        Supports the full FTS5 query syntax for advanced searches.

        Args:
            query: Search query. Supports FTS5 syntax:

                - Simple keywords: ``dialogue``
                - Phrases: ``"character voice"``
                - Boolean: ``tension AND suspense``, ``horror NOT comedy``
                - Prefix: ``narrat*``
                - Column-specific: ``title:craft``

            cluster: Optional cluster name to filter results. Only returns
                matches from the specified cluster.
            limit: Maximum number of results to return. Default 10.

        Returns:
            List of :class:`SearchResult` objects, sorted by BM25 relevance
            score in descending order (best matches first).

        Example:
            >>> # Simple search
            >>> results = index.search("dialogue")

            >>> # Phrase search
            >>> results = index.search('"character voice"')

            >>> # Boolean with cluster filter
            >>> results = index.search("tension OR suspense",
            ...                        cluster="emotional-design",
            ...                        limit=5)
        """
        # Build FTS5 query
        fts_query = query

        # Add cluster filter if specified
        where_clause = ""
        params: list[str | int] = [fts_query]
        if cluster:
            where_clause = "AND cluster = ?"
            params.append(cluster)
        params.append(limit)

        cursor = self.conn.execute(
            f"""
            SELECT
                document_name,
                title,
                cluster,
                topics,
                section_heading,
                content,
                bm25(corpus_fts) as score
            FROM corpus_fts
            WHERE corpus_fts MATCH ?
            {where_clause}
            ORDER BY score
            LIMIT ?
            """,
            params,
        )

        results = []
        for row in cursor:
            topics = row["topics"].split() if row["topics"] else []
            results.append(
                SearchResult(
                    document_name=row["document_name"],
                    title=row["title"],
                    cluster=row["cluster"],
                    section_heading=row["section_heading"],
                    content=row["content"],
                    score=abs(row["score"]),  # bm25 returns negative scores
                    topics=topics,
                )
            )

        return results

    def list_documents(self) -> list[dict[str, str]]:
        """List all indexed documents with their metadata.

        Returns:
            List of dicts containing document metadata. Each dict has keys:

                - ``name``: Document name (filename stem)
                - ``title``: Document title
                - ``cluster``: Topic cluster
                - ``topics``: List of topic keywords

            Documents are sorted by cluster, then by name.
        """
        cursor = self.conn.execute(
            "SELECT name, title, cluster, topics FROM documents ORDER BY cluster, name"
        )
        return [
            {
                "name": row["name"],
                "title": row["title"],
                "cluster": row["cluster"],
                "topics": row["topics"].split(","),
            }
            for row in cursor
        ]

    def list_clusters(self) -> list[str]:
        """List all unique clusters in the index.

        Returns:
            Alphabetically sorted list of cluster names that have at least
            one indexed document.
        """
        cursor = self.conn.execute("SELECT DISTINCT cluster FROM documents ORDER BY cluster")
        return [row["cluster"] for row in cursor]

    def get_document(self, name: str) -> dict[str, Any] | None:
        """Get a document by name with all its sections.

        Retrieves complete document data including metadata and all
        parsed sections.

        Args:
            name: Document name (filename stem without .md extension).

        Returns:
            Dict with document data or None if not found. Dict contains:

                - ``name``: Document name
                - ``path``: Original file path
                - ``title``: Document title
                - ``summary``: Document summary
                - ``cluster``: Topic cluster
                - ``topics``: List of topic keywords
                - ``sections``: List of section dicts with heading, level,
                  content, and line_start

        Example:
            >>> doc = index.get_document("dialogue_craft")
            >>> if doc:
            ...     print(doc["title"])
            ...     for s in doc["sections"]:
            ...         print(f"  {s['heading']}")
        """
        cursor = self.conn.execute(
            """
            SELECT id, name, path, title, summary, cluster, topics
            FROM documents WHERE name = ?
            """,
            (name,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        sections_cursor = self.conn.execute(
            """
            SELECT heading, level, content, line_start
            FROM sections WHERE document_id = ?
            ORDER BY line_start
            """,
            (row["id"],),
        )

        return {
            "name": row["name"],
            "path": row["path"],
            "title": row["title"],
            "summary": row["summary"],
            "cluster": row["cluster"],
            "topics": row["topics"].split(","),
            "sections": [
                {
                    "heading": s["heading"],
                    "level": s["level"],
                    "content": s["content"],
                    "line_start": s["line_start"],
                }
                for s in sections_cursor
            ],
        }

    def document_count(self) -> int:
        """Get the total number of indexed documents.

        Returns:
            Count of documents in the index.
        """
        cursor = self.conn.execute("SELECT COUNT(*) FROM documents")
        result = cursor.fetchone()
        return int(result[0]) if result else 0


def build_index(corpus_dir: Path, output_path: Path) -> CorpusIndex:
    """Build a corpus index and save to a file.

    Convenience function that creates a new :class:`CorpusIndex`, populates
    it from a corpus directory, and returns it. The index is automatically
    persisted to the specified path.

    Args:
        corpus_dir: Path to the corpus root directory containing markdown
            files organized in cluster subdirectories.
        output_path: Path where the SQLite database file will be created.
            Parent directories must exist.

    Returns:
        The populated :class:`CorpusIndex` instance. The caller is
        responsible for calling :meth:`~CorpusIndex.close` when done.

    Example:
        >>> from pathlib import Path
        >>> from ifcraftcorpus.index import build_index
        >>>
        >>> index = build_index(
        ...     corpus_dir=Path("corpus"),
        ...     output_path=Path("dist/corpus.db")
        ... )
        >>> print(f"Built index with {index.document_count()} documents")
        >>> index.close()
    """
    index = CorpusIndex(output_path)
    index.build_from_directory(corpus_dir)
    return index
