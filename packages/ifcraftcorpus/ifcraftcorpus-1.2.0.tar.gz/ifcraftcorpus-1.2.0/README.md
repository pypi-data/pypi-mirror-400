# IF Craft Corpus

A curated knowledge base for interactive fiction writing craft, with a Python library for search and RAG applications.

## Features

- **43 documents** covering narrative structure, prose craft, genre conventions, and more
- **1300+ searchable sections** with detailed craft guidance
- **Python library** for programmatic access with FTS and optional semantic search
- **Pre-built index** for instant search without setup

## Installation

```bash
pip install ifcraftcorpus
```

For semantic search with embeddings:

```bash
pip install ifcraftcorpus[embeddings]
```

## Quick Start

```python
from ifcraftcorpus import Corpus

# Initialize corpus (uses bundled content and pre-built index)
corpus = Corpus()

# Full-text search
results = corpus.search("dialogue subtext techniques")
for r in results:
    print(f"{r.document}: {r.heading}")
    print(f"  {r.snippet}...")

# Browse by cluster
docs = corpus.list_documents(cluster="prose-and-language")

# Get full document
doc = corpus.get_document("dialogue_craft")
print(doc.title, doc.summary)
```

### Semantic Search (Optional)

```python
# Enable semantic search with sentence-transformers
corpus = Corpus(embeddings="all-MiniLM-L6-v2")

# Hybrid search combines FTS + semantic
results = corpus.search(
    "how to write realistic conversations",
    mode="hybrid"
)
```

## Corpus Clusters

| Cluster | Documents | Focus |
|---------|-----------|-------|
| narrative-structure | 10 | Pacing, beats, branching, scene structure |
| prose-and-language | 8 | Dialogue, voice, style, prose patterns |
| craft-foundations | 10 | Quality standards, testing, workflow, tools |
| world-and-setting | 5 | Worldbuilding, canon, setting |
| genre-conventions | 4 | Mystery, horror, fantasy, romance |
| audience-and-access | 3 | Accessibility, localization, targeting |
| emotional-design | 2 | Emotional beats, catharsis |
| scope-and-planning | 2 | Scope, length, planning |
| agent-design | 2 | Multi-agent patterns, prompt engineering |
| game-design | 1 | Mechanics design patterns |

## Documentation

Full documentation: https://pvliesdonk.github.io/if-craft-corpus

## License

- **Code**: MIT License (see [LICENSE](LICENSE))
- **Content**: CC-BY-4.0 (see [LICENSE-CONTENT](LICENSE-CONTENT))

## Contributing

Contributions welcome! Please open an issue or PR.
