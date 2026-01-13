# IF Craft Corpus Subagents

Specialized agent templates for Interactive Fiction authoring workflows. These templates provide system prompts for LLM agents that can assist with different aspects of IF creation.

## Overview

The subagents follow a **hub-and-spoke orchestration pattern** where specialized agents handle specific tasks:

| Agent | Archetype | Role |
|-------|-----------|------|
| **Story Architect** | Orchestrator | Plans narrative structure, decomposes projects, coordinates creation |
| **Prose Writer** | Creator | Writes narrative prose, dialogue, and scene text |
| **Quality Reviewer** | Validator | Reviews content for quality, consistency, and standards |
| **Genre Consultant** | Researcher | Provides genre-specific guidance on conventions and tropes |
| **World Curator** | Curator | Maintains world consistency, manages canon |
| **Platform Advisor** | Researcher | Guides tool/platform selection and technical implementation |

## Usage

### Via MCP Prompts (Recommended)

When using the IF Craft Corpus MCP server, subagents are exposed as **prompts** that can be retrieved and used as system prompts for agents:

```python
# Using FastMCP client
from fastmcp import Client

async with Client("ifcraftcorpus-mcp") as client:
    # List available subagents
    prompts = await client.list_prompts()

    # Get a specific prompt
    result = await client.get_prompt(
        "if_story_architect",
        arguments={"project_name": "My IF Game", "genre": "mystery"}
    )

    # Use the prompt content as a system prompt
    system_prompt = result.messages[0].content.text
```

### Via MCP Tool

You can also use the `list_subagents` tool to discover available agents:

```python
subagents = await client.call_tool("list_subagents")
# Returns list of agents with name, description, archetype, and parameters
```

### Direct File Access

The markdown templates can also be read directly:

```python
from pathlib import Path

# In development
template = Path("subagents/if_prose_writer.md").read_text()

# In installed package
import sys
template_path = Path(sys.prefix) / "share" / "ifcraftcorpus" / "subagents" / "if_prose_writer.md"
template = template_path.read_text()
```

## Agent Details

### IF Story Architect

**Archetype:** Orchestrator
**Parameters:** `project_name`, `genre`

Plans and coordinates IF projects without writing content itself. Responsibilities:
- Design narrative topology (time cave, branch-and-bottleneck, QBN, etc.)
- Decompose projects into scenes and branches
- Plan emotional arcs across branches
- Create scene briefs for content creators

**When to use:** At project start to plan structure, or when restructuring.

---

### IF Prose Writer

**Archetype:** Creator
**Parameters:** `genre`, `pov`

Creates narrative content from briefs. Responsibilities:
- Write scene prose and dialogue
- Maintain character voice consistency
- Handle POV and exposition
- Create choice text

**When to use:** For actual content creation from scene briefs.

---

### IF Quality Reviewer

**Archetype:** Validator
**Parameters:** `focus_areas`

Reviews content for quality issues. Responsibilities:
- Check structural integrity (orphaned content, dead ends)
- Verify voice and style consistency
- Validate canon and continuity
- Audit accessibility compliance

**When to use:** After content creation, before publishing.

---

### IF Genre Consultant

**Archetype:** Researcher
**Parameters:** `primary_genre`, `secondary_genre`

Provides genre-specific guidance. Responsibilities:
- Explain genre conventions and expectations
- Suggest appropriate tropes and subversions
- Advise on cross-genre blending
- Guide tone and style

**When to use:** During planning, or when genre questions arise.

---

### IF World Curator

**Archetype:** Curator
**Parameters:** `world_name`, `setting_type`

Maintains world consistency. Responsibilities:
- Track canon facts across branches
- Manage timeline and character states
- Flag contradictions
- Maintain world bible

**When to use:** Throughout project to maintain consistency.

---

### IF Platform Advisor

**Archetype:** Researcher
**Parameters:** `target_platform`, `team_size`

Guides technical decisions. Responsibilities:
- Compare IF platforms (Twine, Ink, ChoiceScript, etc.)
- Recommend tools based on project needs
- Advise on workflow and collaboration
- Guide integration strategies

**When to use:** At project start for platform selection, or when evaluating tools.

## Corpus Integration

All subagents are designed to use the IF Craft Corpus MCP tools:

- `search_corpus(query, cluster?, limit?)` - Find relevant guidance
- `get_document(name)` - Retrieve full document
- `list_documents(cluster?)` - Discover available guidance

Each template includes guidance on which corpus clusters are most relevant for that agent's work.

## Web Research

Subagents are also encouraged to use web search for:
- Historical/factual accuracy
- Current platform documentation
- Published IF examples
- Domain-specific knowledge

## Design Principles

These templates follow patterns from the corpus's own agent design documents:

1. **Sandwich Pattern** - Critical constraints at start AND end of prompt
2. **Menu + Consult** - Summary in prompt, retrieve details on demand
3. **Clear Archetypes** - Each agent has a defined role and boundaries
4. **Neutral Tool Descriptions** - Descriptive, not prescriptive

## Extending

To create custom subagents:

1. Copy an existing template as a starting point
2. Modify the role, responsibilities, and workflow sections
3. Update the corpus cluster references for your agent's domain
4. Add any custom output formats needed
5. Register as an MCP prompt if desired

## License

These templates are part of the IF Craft Corpus package:
- **Code**: MIT License
- **Content**: CC-BY-4.0
