"""
Corpus file parser.

This module provides functionality to parse corpus markdown files, extracting
YAML frontmatter metadata and markdown sections. It supports:

- YAML frontmatter extraction (title, summary, topics, cluster)
- Markdown section parsing with heading hierarchy
- Document validation against schema requirements
- Batch parsing of corpus directories

Example:
    Parse a single file::

        from pathlib import Path
        from ifcraftcorpus.parser import parse_file

        doc = parse_file(Path("corpus/prose-and-language/dialogue_craft.md"))
        print(f"Title: {doc.title}")
        print(f"Sections: {len(doc.sections)}")

    Parse an entire corpus::

        docs = parse_directory(Path("corpus"))
        for doc in docs:
            errors = doc.validate()
            if errors:
                print(f"{doc.name}: {errors}")

Attributes:
    FRONTMATTER_PATTERN: Regex pattern for YAML frontmatter extraction.
    HEADING_PATTERN: Regex pattern for markdown headings (H1-H3).
    VALID_CLUSTERS: Frozenset of valid cluster names for validation.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Regex patterns
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HEADING_PATTERN = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)

# Valid cluster names
VALID_CLUSTERS = frozenset(
    {
        "narrative-structure",
        "prose-and-language",
        "genre-conventions",
        "audience-and-access",
        "world-and-setting",
        "emotional-design",
        "scope-and-planning",
        "craft-foundations",
        "agent-design",
        "game-design",
    }
)


@dataclass
class Section:
    """A section extracted from a corpus markdown file.

    Represents a single heading and its associated content from a markdown
    document. Sections are extracted based on heading hierarchy (H1-H3).

    Attributes:
        heading: The text of the section heading (without the # prefix).
        level: Heading level where 1=H1, 2=H2, 3=H3. Only H1-H3 are extracted.
        content: The markdown content between this heading and the next
            heading of equal or higher level. Whitespace is stripped.
        line_start: 1-indexed line number where the section begins in the
            source file. Useful for source mapping and error reporting.

    Example:
        >>> section = Section(heading="Introduction", level=1, content="...", line_start=10)
        >>> section.heading
        'Introduction'
    """

    heading: str
    level: int
    content: str
    line_start: int = 0

    def __post_init__(self) -> None:
        """Strip whitespace from content after initialization."""
        self.content = self.content.strip()


@dataclass
class Document:
    """A parsed corpus document with frontmatter metadata and sections.

    Represents a complete corpus markdown file after parsing. Contains all
    metadata from YAML frontmatter plus extracted markdown sections.

    Documents can be validated against the corpus schema using the
    :meth:`validate` method to check for required fields and constraints.

    Attributes:
        path: Absolute or relative path to the source markdown file.
        title: Document title from frontmatter. Required, minimum 5 characters.
        summary: Brief description from frontmatter. Required, 20-300 characters.
        topics: List of topic keywords from frontmatter. Required, minimum 3.
        cluster: Topic cluster name from frontmatter. Must be a valid cluster.
        sections: List of extracted :class:`Section` objects from the document body.
        content_hash: First 16 characters of SHA-256 hash of file contents.
            Useful for detecting changes without re-parsing.
        raw_content: Original file content as a string, preserved for reference.

    Example:
        >>> doc = parse_file(Path("corpus/dialogue.md"))
        >>> print(doc.name, doc.title)
        dialogue Writing Effective Dialogue
        >>> errors = doc.validate()
        >>> if not errors:
        ...     print("Document is valid")
    """

    path: Path
    title: str
    summary: str
    topics: list[str]
    cluster: str
    sections: list[Section] = field(default_factory=list)
    content_hash: str = ""
    raw_content: str = ""

    @property
    def name(self) -> str:
        """Get the document name without file extension.

        Returns:
            The filename stem (e.g., 'dialogue_craft' from 'dialogue_craft.md').
        """
        return self.path.stem

    def validate(self) -> list[str]:
        """Validate the document against corpus schema requirements.

        Checks all required fields and their constraints. This method does
        not raise exceptions; instead it returns a list of error messages.

        Returns:
            List of validation error messages. Empty list if document is valid.

        Validation Rules:
            - title: Required, minimum 5 characters
            - summary: Required, 20-300 characters
            - topics: Required, minimum 3 topics
            - cluster: Required, must be in VALID_CLUSTERS
        """
        errors = []

        if not self.title:
            errors.append("Missing required field: title")
        elif len(self.title) < 5:
            errors.append(f"Title too short (min 5 chars): {len(self.title)}")

        if not self.summary:
            errors.append("Missing required field: summary")
        elif len(self.summary) < 20:
            errors.append(f"Summary too short (min 20 chars): {len(self.summary)}")
        elif len(self.summary) > 300:
            errors.append(f"Summary too long (max 300 chars): {len(self.summary)}")

        if not self.topics:
            errors.append("Missing required field: topics")
        elif len(self.topics) < 3:
            errors.append(f"Too few topics (min 3): {len(self.topics)}")

        if not self.cluster:
            errors.append("Missing required field: cluster")
        elif self.cluster not in VALID_CLUSTERS:
            errors.append(f"Invalid cluster '{self.cluster}', must be one of: {VALID_CLUSTERS}")

        return errors


def parse_file(path: Path) -> Document:
    """Parse a corpus markdown file.

    Args:
        path: Path to the markdown file.

    Returns:
        Parsed Document with frontmatter and sections.

    Raises:
        ValueError: If file cannot be parsed.
    """
    content = path.read_text(encoding="utf-8")
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

    # Extract frontmatter
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        raise ValueError(f"No valid frontmatter found in {path}")

    try:
        frontmatter_data: dict[str, Any] = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in frontmatter of {path}: {e}") from e

    # Body content after frontmatter
    body = content[match.end() :]

    # Extract sections
    sections = _extract_sections(body)

    return Document(
        path=path,
        title=frontmatter_data.get("title", ""),
        summary=frontmatter_data.get("summary", ""),
        topics=frontmatter_data.get("topics", []),
        cluster=frontmatter_data.get("cluster", ""),
        sections=sections,
        content_hash=content_hash,
        raw_content=content,
    )


def _extract_sections(content: str) -> list[Section]:
    """Extract heading-based sections from markdown content.

    Parses markdown content to find all H1-H3 headings and extracts the
    content between them. Each section includes the heading text, level,
    content, and source line number.

    Args:
        content: Markdown content (without frontmatter) to parse.

    Returns:
        List of Section objects for each heading found. Sections are
        ordered by their appearance in the document.

    Note:
        - Only H1-H3 headings are extracted (# to ###)
        - Section content extends to the next heading of equal or higher level
        - Headings deeper than H3 are included in parent section content
    """
    sections: list[Section] = []
    lines = content.split("\n")

    # Find all heading positions
    heading_positions: list[tuple[int, int, str]] = []  # (line_num, level, heading)

    for i, line in enumerate(lines):
        match = HEADING_PATTERN.match(line)
        if match:
            level = len(match.group(1))
            heading = match.group(2).strip()
            heading_positions.append((i, level, heading))

    # Extract content between headings
    for idx, (line_num, level, heading) in enumerate(heading_positions):
        # Find end of this section (next heading of same or higher level, or end)
        end_line = len(lines)
        for next_line, next_level, _ in heading_positions[idx + 1 :]:
            if next_level <= level:
                end_line = next_line
                break
        else:
            # No higher-level heading found, check for any heading
            if idx + 1 < len(heading_positions):
                end_line = heading_positions[idx + 1][0]

        # Extract section content (excluding the heading line itself)
        section_lines = lines[line_num + 1 : end_line]
        section_content = "\n".join(section_lines).strip()

        sections.append(
            Section(
                heading=heading,
                level=level,
                content=section_content,
                line_start=line_num + 1,  # 1-indexed
            )
        )

    return sections


def parse_directory(corpus_dir: Path) -> list[Document]:
    """Parse all markdown files in a corpus directory recursively.

    Walks through the directory tree and parses all .md files. Files that
    fail to parse (missing frontmatter, invalid YAML) are silently skipped.

    Args:
        corpus_dir: Path to the corpus root directory. All subdirectories
            are searched recursively for .md files.

    Returns:
        List of successfully parsed Document objects, sorted alphabetically
        by file path.

    Example:
        >>> docs = parse_directory(Path("corpus"))
        >>> print(f"Parsed {len(docs)} documents")
        >>> for doc in docs:
        ...     if doc.validate():
        ...         print(f"Warning: {doc.name} has validation errors")

    Note:
        Files without valid YAML frontmatter are skipped without error.
        Use :func:`parse_file` directly if you need error details.
    """
    documents = []
    for md_path in sorted(corpus_dir.rglob("*.md")):
        try:
            doc = parse_file(md_path)
            documents.append(doc)
        except ValueError:
            # Skip files that can't be parsed
            continue
    return documents
