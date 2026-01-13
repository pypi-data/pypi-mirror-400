---
title: Agent Prompt Engineering
summary: Techniques for crafting effective LLM agent prompts—attention patterns, tool design, context layering, model size considerations, and testing strategies.
topics:
  - prompt-engineering
  - llm-agents
  - attention-patterns
  - tool-design
  - context-management
  - small-models
  - chain-of-thought
  - few-shot-learning
cluster: agent-design
---

# Agent Prompt Engineering

Techniques for crafting effective prompts for LLM agents—attention patterns, tool design, context layering, and strategies for different model sizes.

This document is useful both for agents creating content AND for humans designing agents.

---

## Attention Patterns

### Lost in the Middle

LLMs exhibit a U-shaped attention curve: information at the **beginning** and **end** of prompts receives stronger attention than content in the middle.

```
Position in prompt:  [START] -------- [MIDDLE] -------- [END]
Attention strength:   HIGH            LOW               HIGH
```

Critical instructions placed in the middle of a long prompt may be ignored, even by otherwise capable models.

### The Sandwich Pattern

For critical instructions, repeat them at the **start AND end** of the prompt:

```markdown
## CRITICAL: You are an orchestrator. NEVER write prose yourself.

[... 500+ lines of context ...]

## REMINDER: You are an orchestrator. NEVER write prose yourself.
```

### Ordering for Attention

Structure prompts strategically given the U-shaped curve:

**Recommended order:**

1. **Critical behavioral constraints** (lines 1-20)
2. **Role identity and purpose** (lines 21-50)
3. **Tool descriptions** (if using function calling)
4. **Reference material** (middle—lowest attention)
5. **Knowledge summaries** (for retrieval patterns)
6. **Critical reminder** (last 10-20 lines)

**What goes in the middle:**

Lower-priority content that can be retrieved on demand:

- Detailed procedures
- Reference tables
- Quality criteria details
- Examples (use retrieval when possible)

---

## Tool Design

### Tool Count Effects

Tool count strongly correlates with compliance, especially for smaller models:

| Tool Count | Compliance Rate (8B model) |
|------------|---------------------------|
| 6 tools    | ~100%                     |
| 12 tools   | ~85%                      |
| 20 tools   | ~70%                      |

**Recommendations:**

- **Small models (≤8B)**: Limit to 6-8 tools
- **Medium models (9B-70B)**: Up to 12 tools
- **Large models (70B+)**: Can handle 15+ but consider UX

### Tool Schema Overhead

Tool schemas sent via function calling are often larger than the system prompt itself:

| Component | Typical Size |
|-----------|--------------|
| Tool name | ~5 tokens |
| Description | 50-150 tokens |
| Parameter schema | 100-300 tokens |
| **Per tool total** | 150-450 tokens |
| **13 tools** | **2,000-5,900 tokens** |

### Optimization Strategies

**1. Model-Class Filtering**

Define reduced tool sets for small models:

```json
{
  "tools": ["delegate", "communicate", "search", "save", ...],
  "small_model_tools": ["delegate", "communicate", "save"]
}
```

**2. Two-Stage Selection**

For large tool libraries (20+):

1. Show lightweight menu (name + summary only)
2. Agent selects relevant tools
3. Load full schema only for selected tools

Research shows 50%+ token reduction with 3x accuracy improvement.

**3. Deferred Loading**

Mark specialized tools as discoverable but not pre-loaded. They appear in a search interface rather than being sent to the API upfront.

**4. Concise Descriptions**

1-2 sentences max. Move detailed usage guidance to knowledge entries.

**Before** (~80 tokens):

> "Delegate work to another agent. This hands off control until the agent completes the task. Provide task description, context, expected outputs, and quality criteria. The receiving agent executes and returns control with artifacts and assessment."

**After** (~20 tokens):

> "Hand off a task to another agent. Control returns when they complete."

**5. Minimal Parameter Schemas**

For small models, simplify schemas:

**Full** (~200 tokens): All optional parameters with descriptions

**Minimal** (~50 tokens): Only required parameters

Optional parameters can use reasonable defaults.

### Tool Description Biasing

Tool descriptions have **higher influence** than system prompt content when models decide which tool to call.

**Problem:**

If a tool description contains prescriptive language ("ALWAYS use this", "This is the primary method"), models will prefer that tool regardless of system prompt instructions.

**Solution:**

Use **neutral, descriptive** tool descriptions. Let the **system prompt** dictate when to use tools.

**Anti-pattern:**

> "ALWAYS use this tool to create story content. This is the primary way to generate text."

**Better:**

> "Creates story prose from a brief. Produces narrative text with dialogue and descriptions."

---

## Context Architecture

### The Four Layers

Organize agent prompts into distinct layers:

| Layer | Purpose | Token Priority |
|-------|---------|----------------|
| **System** | Core identity, constraints | High (always include) |
| **Task** | Current instructions | High |
| **Tool** | Tool descriptions/schemas | Medium (filter for small models) |
| **Memory** | Historical context | Variable (summarize as needed) |

### Benefits of Layer Separation

- **Debugging**: Isolate which layer caused unexpected behavior
- **Model switching**: System layer stays constant across model sizes
- **Token management**: Each layer can be independently compressed
- **Caching**: System and tool layers can be cached between turns

### Menu + Consult Pattern

For knowledge that agents need access to but not always in context:

**Structure:**

```
System prompt contains:
- Summary/menu showing what knowledge exists
- Tool to retrieve full details

System prompt does NOT contain:
- Full knowledge content
- Detailed procedures
- Reference material
```

**Benefits:**

- Smaller initial prompt
- Agent can "pull" knowledge when needed
- Works well with small models

### When to Inject vs. Consult

| Content Type | Small Model | Large Model |
|--------------|-------------|-------------|
| Role identity | Inject | Inject |
| Behavioral constraints | Inject | Inject |
| Workflow procedures | Consult | Inject or Consult |
| Quality criteria | Consult | Inject |
| Reference material | Consult | Consult |

---

## Model Size Considerations

### Token Budgets

| Model Class | Recommended System Prompt |
|-------------|---------------------------|
| Small (≤8B) | ≤2,000 tokens |
| Medium (9B-70B) | ≤6,000 tokens |
| Large (70B+) | ≤12,000 tokens |

Exceeding these budgets leads to:

- Ignored instructions (especially in the middle)
- Reduced tool compliance
- Hallucinated responses

### Instruction Density

Small models struggle with:

- Conditional logic: "If X and not Y, then Z unless W"
- Multiple competing priorities
- Nuanced edge cases

**Simplify for small models:**

- "Always call delegate" (not "call delegate unless validating")
- One instruction per topic
- Remove edge case handling (accept lower quality)

### Concise Content Pattern

Provide two versions of guidance:

```json
{
  "summary": "Orchestrators delegate tasks to specialists. Before delegating, consult the relevant playbook to understand the workflow. Pass artifact IDs between steps. Monitor completion.",
  "concise_summary": "Delegate to specialists. Consult playbook first."
}
```

Runtime selects the appropriate version based on model class.

### Semantic Ambiguity

Avoid instructions that can be interpreted multiple ways.

**Anti-pattern:**

> "Use your best judgment to determine when validation is needed."

Small models may interpret as "never validate" or "always validate."

**Better:**

> "Call validate after every save."

---

## Sampling Parameters

Sampling parameters control the randomness and diversity of LLM outputs. The two most important are **temperature** and **top_p**. These can be set per API call, enabling different settings for different phases of a workflow.

### Temperature

Temperature controls the probability distribution over tokens. Lower values make the model more deterministic; higher values increase randomness and creativity.

| Temperature | Effect | Use Cases |
|-------------|--------|-----------|
| 0.0–0.2 | Highly deterministic, consistent | Structured output, tool calling, factual responses |
| 0.3–0.5 | Balanced, slight variation | General conversation, summarization |
| 0.6–0.8 | More creative, diverse | Brainstorming, draft generation |
| 0.9–1.0+ | High randomness, exploratory | Creative writing, idea exploration, poetry |

**How it works:** Temperature scales the logits (pre-softmax scores) before sampling. At T=0, the model always picks the highest-probability token. At T>1, probability differences flatten, making unlikely tokens more probable.

**Caveats:**

- Even T=0 isn't fully deterministic—hardware concurrency and floating-point variations can introduce tiny differences
- High temperature increases hallucination risk
- Temperature interacts with top_p; tuning both simultaneously requires care

### Top_p (Nucleus Sampling)

Top_p limits sampling to the smallest set of tokens whose cumulative probability exceeds p. This provides a different control over diversity than temperature.

| Top_p | Effect |
|-------|--------|
| 0.1–0.3 | Very focused, few token choices |
| 0.5–0.7 | Moderate diversity |
| 0.9–1.0 | Wide sampling, more variation |

**Temperature vs Top_p:**

- Temperature affects *all* token probabilities uniformly
- Top_p dynamically adjusts the candidate pool based on probability mass
- For most use cases, adjust one and leave the other at default
- Common pattern: low temperature (0.0–0.3) with top_p=1.0 for structured tasks

### Provider Temperature Ranges

| Provider | Range | Default | Notes |
|----------|-------|---------|-------|
| OpenAI | 0.0–2.0 | 1.0 | Values >1.0 increase randomness significantly |
| Anthropic | 0.0–1.0 | 1.0 | Cannot exceed 1.0 |
| Gemini | 0.0–2.0 | 1.0 | Similar to OpenAI |
| Ollama | 0.0–1.0+ | 0.7–0.8 | Model-dependent defaults |

### Phase-Specific Temperature

Since temperature can be set per API call, use different values for different workflow phases:

| Phase | Temperature | Rationale |
|-------|-------------|-----------|
| Brainstorming/Discuss | 0.7–1.0 | Encourage diverse ideas, exploration |
| Planning/Freeze | 0.3–0.5 | Balance creativity with coherence |
| Serialize/Tool calls | 0.0–0.2 | Maximize format compliance |
| Validation repair | 0.0–0.2 | Deterministic corrections |

This is particularly relevant for the **Discuss → Freeze → Serialize** pattern described below—each stage benefits from different temperature settings.

---

## Structured Output Pipelines

Many agent tasks end in a **strict artifact**—JSON/YAML configs, story plans, outlines—rather than free-form prose. Trying to get both *conversation* and *perfectly formatted output* from a single response is brittle, especially for small/local models.

A more reliable approach is to separate the flow into stages:

1. **Discuss** – messy, human-friendly turns to clarify goals and constraints. No structured output yet.
2. **Freeze** – summarize final decisions into a compact, explicit list (facts & constraints).
3. **Serialize** – a dedicated call whose only job is to emit the structured artifact, constrained by a schema or tool signature.

### Discuss → Freeze → Serialize

**Discuss** (temperature 0.7–1.0): Keep prompts focused on meaning, not field names. Explicitly tell the model *not* to output JSON/YAML during this phase. Higher temperature encourages diverse ideas and creative exploration.

**Freeze** (temperature 0.3–0.5): Compress decisions into a short summary:

- 10–30 bullets, one decision per line.
- No open questions, only resolved choices.
- Structured enough that a smaller model can follow it reliably.
- Moderate temperature balances coherence with flexibility.

**Serialize** (temperature 0.0–0.2): In a separate call:

- Provide the schema (JSON Schema, typed model, or tool definition).
- Instruct: *"Output only JSON that matches this schema. No prose, no markdown fences."*
- Use constrained decoding/tool calling where available.
- Low temperature maximizes format compliance.

This separates conversational drift from serialization, which significantly improves reliability for structured outputs like story plans, world-bible slices, or configuration objects. The temperature gradient—high for exploration, low for precision—matches each phase's purpose.

### Tool-Gated Finalization

An alternative is to represent structured output as a **single tool call**:

- During normal conversation: no tools are called.
- On FINALIZE: the agent must call a tool such as `submit_plan(plan: PlanSchema)` exactly once.

Pros:

- Structured data arrives as typed arguments (no text parsing).
- The runtime can validate arguments immediately.

Cons:

- Some models occasionally skip the tool call or send partial arguments.

Pattern in practice:

- Prefer tool-gated finalization when your stack treats tools as first-class.
- Keep a fallback: if the tool call doesn’t happen, fall back to a serialize-only call using the freeze summary.

---

## Validate → Feedback → Repair Loop

Even with good prompts, structured output will sometimes be **almost** right. Instead of accepting failures or silently discarding data, use a validate-with-feedback loop:

1. Generate a candidate object (JSON/tool args/text).
2. Validate it in code (schema/type checks, domain rules).
3. If invalid, feed back the errors and ask the model to repair **only** the problems.
4. Repeat for a small, fixed number of attempts.

### Validation Channels

Typical validators:

- **Schema/type validation:** JSON Schema, Pydantic/dataclasses, or your own type checks.
- **Domain rules:** length ranges, allowed enum values, cross-field consistency (e.g., word-count vs estimated playtime).
- **Link/graph checks:** required references exist, no impossible states.

### Designing the Feedback Prompt

When a candidate fails validation, the repair prompt should:

- Include the previous candidate object verbatim.
- Include a concise list of validation errors, grouped by field.
- Give strict instructions, e.g.:

> “Return a corrected JSON object that fixes **only** these errors. Do not change fields that are not mentioned. Output only JSON.”

For small models, keep error descriptions compact and concrete rather than abstract ("string too long: 345 > max 200").

### Structured Validation Feedback

Rather than returning free-form error messages, use a structured feedback format that leverages attention patterns (status first, action last) and distinguishes error types clearly.

**Result Categories**

Use a semantic result enum rather than boolean success/failure:

| Result | Meaning | Model Action |
|--------|---------|--------------|
| `accepted` | Validation passed, artifact stored | Proceed to next step |
| `validation_failed` | Content issues the model can fix | Repair and resubmit |
| `tool_error` | Infrastructure failure | Retry unchanged or escalate |

This distinction matters: `validation_failed` tells the model its *content* was wrong (fixable), while `tool_error` indicates the tool itself failed (retry or give up).

**Error Categorization**

Group validation errors by type to help the model understand what went wrong:

```json
{
  "result": "validation_failed",
  "issues": {
    "invalid": [
      {"field": "estimated_passages", "value": 15, "requirement": "must be 1-10"}
    ],
    "missing": ["protagonist_name", "setting"],
    "unknown": ["passages"]
  },
  "issue_count": {"invalid": 1, "missing": 2, "unknown": 1},
  "action": "Fix the 4 issues above and resubmit. Use exact field names from the schema."
}
```

| Category | Meaning | Common Cause |
|----------|---------|--------------|
| `invalid` | Field present but value wrong | Constraint violation, wrong type |
| `missing` | Required field not provided | Omission, incomplete output |
| `unknown` | Field not in schema | Typo, hallucinated field name |

The `unknown` category is particularly valuable—it catches near-misses like `passages` instead of `estimated_passages` that would otherwise appear as "missing" with no hint about the typo.

**Field Ordering (Primacy/Recency)**

Structure feedback to exploit the U-shaped attention curve:

1. **Result status** (first—immediate orientation)
2. **Issues by category** (middle—detailed content)
3. **Issue count** (severity summary)
4. **Action instructions** (last—what to do next)

**What NOT to Include**

| Avoid | Why |
|-------|-----|
| Full schema | Already in tool definition; wastes tokens in retry loops |
| Boolean `success` field | Ambiguous; use semantic result categories instead |
| Generic hints | Replace with actionable, field-specific instructions |
| Valid fields | Only describe what failed, not what succeeded |

**Example: Before and After**

Anti-pattern (vague, wastes tokens):

```
Error: Validation failed. Expected fields: type, title, protagonist_name,
setting, theme, estimated_passages, tone. Please check your submission
and ensure all required fields are present with valid values.
```

Better (specific, actionable):

```json
{
  "result": "validation_failed",
  "issues": {
    "invalid": [{"field": "type", "value": "story", "requirement": "must be 'dream'"}],
    "missing": ["protagonist_name"],
    "unknown": ["passages"]
  },
  "action": "Fix these 3 issues. Did you mean 'estimated_passages' instead of 'passages'?"
}
```

The improved version:

- Names the exact fields that failed
- Suggests the likely typo (`passages` → `estimated_passages`)
- Doesn't repeat schema information already available to the model
- Ends with a clear action instruction (primacy/recency)

### Retry Budget and Token Efficiency

Validation loops consume tokens. Design for efficiency:

- **Cap retries**: 2-3 attempts is usually sufficient; more indicates a prompt or schema problem
- **Escalate gracefully**: After retry budget exhausted, surface a clear failure rather than looping
- **Track retry rates**: High retry rates signal opportunities for prompt improvement or schema simplification
- **Consider model capability**: Less capable models may need higher retry budgets but with simpler feedback

### Best Practices

- **Independent validator:** Treat validation as a separate layer or service whenever possible; don’t let the same model decide if its own output is valid.
- **Retry budget:** Cap the number of repair attempts; surface a clear failure state instead of looping indefinitely.
- **Partial success:** Prefer emitting valid-but-partial objects over invalid-but-complete-looking ones; downstream systems can handle missing optional fields more safely than malformed structure.

Validate → feedback → repair is a general pattern:

- Works for schema-bound JSON/YAML.
- Works for more informal artifacts (e.g., checklists, outlines) when combined with light-weight structural checks.
- Plays well with the structured-output patterns above and with the reflection/self-critique patterns below.

---

## Prompt-History Conflicts

When the system prompt says "MUST do X first" but the conversation history shows the model already did Y, confusion results.

**Problem:**

```
System: "You MUST call consult_playbook before any delegation."
History: [delegate(...) was called successfully]
Model: "But I already delegated... should I undo it?"
```

**Solutions:**

1. **Use present-tense rules**: "Call consult_playbook before delegating" not "MUST call first"
2. **Acknowledge state**: "If you haven't yet consulted the playbook, do so now"
3. **Avoid absolute language** when state may vary

---

## Chain-of-Thought (CoT)

For complex logical tasks, forcing the model to articulate its reasoning *before* acting significantly reduces hallucination and logic errors.

### The Problem

Zero-shot tool calling often fails on multi-step problems because the model commits to an action before fully processing constraints.

### Implementation

Require explicit reasoning steps:

- **Structure**: `<thought>Analysis...</thought>` followed by tool call
- **Tooling**: Add a mandatory `reasoning` parameter to critical tools
- **Benefits**: +40-50% improvement on complex reasoning benchmarks

### When to Use

- Multi-step planning decisions
- Constraint satisfaction problems
- Quality assessments with multiple criteria
- Decisions with long-term consequences

---

## Dynamic Few-Shot Prompting

Static example lists consume tokens and may not match the current task.

### The Pattern

Use retrieval to inject context-aware examples:

1. **Store** a library of high-quality examples as vectors
2. **Query** using the current task description
3. **Inject** top 3-5 most relevant examples into the prompt

### Benefits

- Smaller prompts (no static example bloat)
- More relevant examples for each task
- Examples improve as library grows

### When to Use

- Tasks requiring stylistic consistency
- Complex tool usage patterns
- Domain-specific formats

---

## Reflection and Self-Correction

Models perform significantly better when asked to critique their own work before finalizing.

### The Pattern

Implement a "Draft-Critique-Refine" loop:

1. **Draft**: Generate preliminary plan or content
2. **Critique**: Evaluate against constraints
3. **Refine**: Generate final output based on critique

### Implementation Options

- **Two-turn**: Separate critique and refinement turns
- **Single-turn**: Internal thought step for capable models
- **Validator pattern**: Separate agent reviews work

### When to Use

- High-stakes actions (modifying persistent state, finalizing content)
- Complex constraint satisfaction
- Quality-critical outputs

---

## Active Context Pruning

Long-running sessions suffer from "Context Rot"—old, irrelevant details confuse the model even within token limits.

### The Problem

Context is often treated as append-only log. But stale context:

- Dilutes attention from current task
- May contain outdated assumptions
- Wastes token budget

### Strategies

**Semantic Chunking:**

Group history by episodes or tasks, not just turns.

**Active Forgetting:**

When a task completes, summarize to high-level outcome and **remove** raw turns.

**State-over-History:**

Prefer providing current *state* (artifacts, flags) over the *history* of how that state was reached.

---

## Testing Agent Prompts

### Test with Target Models

Before deploying:

1. Test with smallest target model
2. Verify first-turn tool calls work
3. Check for unexpected prose generation
4. Measure token count of system prompt

### Metrics to Track

| Metric | What It Measures |
|--------|------------------|
| Tool compliance rate | % of turns with correct tool calls |
| First-turn success | Does the model call a tool on turn 1? |
| Prose leakage | Does a coordinator generate content? |
| Instruction following | Are critical constraints obeyed? |

---

## Provider-Specific Optimizations

- **Anthropic**: Use `token-efficient-tools` beta header for up to 70% output token reduction; temperature capped at 1.0
- **OpenAI**: Consider fine-tuning for frequently-used patterns; temperature range 0.0–2.0
- **Gemini**: Temperature range 0.0–2.0, similar behavior to OpenAI
- **Ollama/Local**: Tool retrieval essential—small models struggle with 10+ tools; default temperature varies by model (typically 0.7–0.8)

See [Sampling Parameters](#sampling-parameters) for detailed temperature guidance by use case.

---

## Quick Reference

| Pattern | Problem It Solves | Key Technique |
|---------|-------------------|---------------|
| Sandwich | Lost in the middle | Repeat critical instructions at start AND end |
| Tool filtering | Small model tool overload | Limit tools by model class |
| Two-stage selection | Large tool libraries | Menu → select → load |
| Concise descriptions | Schema token overhead | 1-2 sentences, details in knowledge |
| Neutral descriptions | Tool preference bias | Descriptive not prescriptive |
| Menu + consult | Context explosion | Summaries in prompt, retrieve on demand |
| Concise content | Small model budgets | Dual-length summaries |
| CoT | Complex reasoning failures | Require reasoning before action |
| Dynamic few-shot | Static example bloat | Retrieve relevant examples |
| Reflection | Quality failures | Draft → critique → refine |
| Context pruning | Context rot | Summarize and remove stale turns |
| Structured feedback | Vague validation errors | Categorize issues (invalid/missing/unknown) |
| Phase-specific temperature | Format errors in structured output | High temp for discuss, low for serialize |

| Model Class | Max Prompt | Max Tools | Strategy |
|-------------|------------|-----------|----------|
| Small (≤8B) | 2,000 tokens | 6-8 | Aggressive filtering, concise content |
| Medium (9B-70B) | 6,000 tokens | 12 | Selective filtering, menu+consult |
| Large (70B+) | 12,000 tokens | 15+ | Full content where beneficial |

---

## Research Basis

| Source | Key Finding |
|--------|-------------|
| Stanford "Lost in the Middle" | U-shaped attention curve; middle content ignored |
| "Less is More" (2024) | Tool count inversely correlates with compliance |
| RAG-MCP (2025) | Two-stage selection reduces tokens 50%+, improves accuracy 3x |
| Anthropic Token-Efficient Tools | Schema optimization reduces output tokens 70% |
| Reflexion research | Self-correction improves quality on complex tasks |
| STROT Framework (2025) | Structured feedback loops achieve 95% first-attempt success |
| AWS Evaluator-Optimizer | Semantic reflection enables self-improving validation |

---

## See Also

- [Branching Narrative Construction](../narrative-structure/branching_narrative_construction.md) — LLM generation strategies for narratives
- [Multi-Agent Patterns](multi_agent_patterns.md) — Team coordination and delegation
