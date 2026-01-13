---
title: Multi-Agent Patterns
summary: Coordination patterns for LLM agent systems—orchestration models, delegation strategies, team organization, feedback loops, and failure recovery.
topics:
  - multi-agent
  - orchestration
  - delegation
  - team-coordination
  - feedback-loops
  - rework-patterns
  - agent-design
cluster: agent-design
---

# Multi-Agent Patterns

Coordination patterns for LLM agent systems—orchestration models, delegation strategies, team organization, feedback loops, and failure recovery.

This document is useful both for agents coordinating work AND for humans designing multi-agent systems.

---

## Orchestration Models

### Hub-and-Spoke

A central orchestrator receives all requests and delegates to specialists.

```
           ┌─────────────┐
           │ Orchestrator │
           └──────┬──────┘
        ┌─────────┼─────────┐
        ▼         ▼         ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │Specialist│ │Specialist│ │Specialist│
   └────────┘ └────────┘ └────────┘
```

**Characteristics:**

- Single point of coordination
- Clear responsibility for task decomposition
- Orchestrator maintains global state
- Specialists have narrow scope

**When to use:**

- Well-defined task boundaries
- Need for consistent delegation logic
- Quality gates between steps
- External interface requirements

**Tradeoffs:**

- Orchestrator becomes bottleneck
- Deep domain knowledge distributed across specialists
- Single point of failure

### Hierarchical

Multiple levels of orchestration, with sub-orchestrators for complex domains.

```
           ┌─────────────┐
           │  Executive   │
           └──────┬──────┘
        ┌─────────┴─────────┐
        ▼                   ▼
   ┌──────────┐        ┌──────────┐
   │ Manager A │        │ Manager B │
   └─────┬────┘        └─────┬────┘
      ┌──┴──┐             ┌──┴──┐
      ▼     ▼             ▼     ▼
    [Workers]           [Workers]
```

**Characteristics:**

- Delegation of coordination responsibility
- Domain-specific sub-orchestrators
- Reduced cognitive load at each level

**When to use:**

- Complex domains with sub-specializations
- Large agent populations
- Need for domain-specific delegation logic

**Tradeoffs:**

- More complex communication patterns
- Potential for conflicting instructions
- Harder to maintain global consistency

### Peer-to-Peer

Agents communicate directly without central orchestration.

```
   ┌────────┐     ┌────────┐
   │ Agent A │◄───►│ Agent B │
   └────┬───┘     └────┬───┘
        │              │
        ▼              ▼
   ┌────────┐     ┌────────┐
   │ Agent C │◄───►│ Agent D │
   └────────┘     └────────┘
```

**Characteristics:**

- No single point of coordination
- Agents negotiate directly
- Emergent rather than planned coordination

**When to use:**

- Highly autonomous agents
- Collaborative creative tasks
- Situations requiring real-time adaptation

**Tradeoffs:**

- Harder to ensure consistency
- Risk of deadlock or infinite loops
- Difficult to debug

---

## Delegation Patterns

### Basic Delegation

Orchestrator assigns task, waits for completion, receives result.

```
Orchestrator: delegate(agent="specialist", task="Do X")
    └─► Specialist receives task
    └─► Specialist completes work
    └─► Specialist returns result
Orchestrator: receives result, continues
```

**Key elements:**

- Clear task description
- Expected outputs specified
- Quality criteria communicated
- Context passed to specialist

### Context Passing

What to include when delegating:

| Element | Purpose | When to Include |
|---------|---------|-----------------|
| Task description | What to do | Always |
| Expected outputs | What to produce | Always |
| Quality criteria | How to judge success | When relevant |
| Related artifacts | Input data | When needed |
| Constraints | What NOT to do | When non-obvious |
| Previous attempts | For rework | After failures |

**Anti-pattern: Context starvation**

Delegating with minimal context, forcing specialist to guess.

**Anti-pattern: Context flooding**

Passing entire conversation history instead of relevant summary.

### Parallel Delegation

Multiple specialists work simultaneously on independent tasks.

```
Orchestrator:
    ├─► delegate(agent="A", task="Part 1")  ─┐
    ├─► delegate(agent="B", task="Part 2")  ─┼─► wait_all()
    └─► delegate(agent="C", task="Part 3")  ─┘
Orchestrator: receives all results, integrates
```

**When to use:**

- Tasks are independent
- Speed matters
- Integration is well-defined

**Challenges:**

- Results may conflict
- Partial failures complicate integration
- Coordination overhead for many parallel tasks

### Sequential Delegation

Each step depends on previous output.

```
Orchestrator:
    └─► delegate(agent="researcher", task="Research X")
        └─► result_1
    └─► delegate(agent="planner", task="Plan based on {result_1}")
        └─► result_2
    └─► delegate(agent="executor", task="Execute {result_2}")
        └─► final_result
```

**When to use:**

- Steps have dependencies
- Output of one step is input to next
- Quality gates between steps

### Conditional Delegation

Next step depends on outcome of previous.

```
result = delegate(agent="validator", task="Validate X")

if result.passed:
    delegate(agent="publisher", task="Publish X")
else:
    delegate(agent="editor", task="Fix issues: {result.feedback}")
```

---

## Team Organization

### Self-Organizing Teams

Define a team with roles; let them self-coordinate.

**Team definition:**

```yaml
team:
  roles:
    - archetype: researcher
      responsibility: "Gather background information"
    - archetype: creator
      responsibility: "Draft content using research"
    - archetype: validator
      responsibility: "Review for accuracy"
  coordination: self_organizing
  lead: creator
```

**Flow:**

1. Lead receives delegation
2. Lead assesses what's needed
3. Lead requests input from other roles
4. Team members execute responsibilities
5. Lead integrates results
6. Lead reports completion

### Coordination Modes

| Mode | Behavior | When to Use |
|------|----------|-------------|
| `sequential` | Roles execute in listed order | Clear dependencies |
| `parallel` | Roles work simultaneously | Independent tasks |
| `self_organizing` | Lead coordinates, team decides order | Complex, adaptive |

### Specialist Archetypes

Common agent role patterns:

| Archetype | Responsibility | Key Traits |
|-----------|----------------|------------|
| Orchestrator | Coordinate work, delegate tasks | Doesn't create content |
| Creator | Produce artifacts | Domain expertise |
| Validator | Check quality, enforce rules | Critical eye, knows standards |
| Researcher | Gather information | Search skills, synthesis |
| Curator | Maintain consistency | Cross-domain awareness |

---

## Feedback Loops

### Rework Loop Pattern

Quality gates may reject work, requiring revision.

**Structure:**

```
┌────────┐     ┌──────────┐     ┌────────┐
│ Create │────►│ Validate │────►│ Deliver │
└────────┘     └────┬─────┘     └────────┘
     ▲              │ fail
     │              ▼
     │         ┌────────┐
     └─────────│ Revise │
               └────────┘
```

**Feedback preservation:**

When delegating for rework, include previous attempts:

```json
{
  "context": {
    "previous_attempts": [
      {
        "attempt": 1,
        "outcome": "rejected",
        "feedback": "Inconsistent character voice",
        "artifacts": ["draft_v1"]
      }
    ]
  }
}
```

### Rework Limits

**Problem:** Infinite revision loops.

**Solution:** Define `max_rework_cycles` (typical: 3).

After exceeding limit:

1. Escalate to orchestrator
2. Orchestrator may: adjust requirements, change agent, or report failure

### Feedback Quality

Good feedback is:

- **Specific**: Points to exact issues
- **Actionable**: Clear what to change
- **Prioritized**: Most important issues first
- **Constructive**: Suggests fixes, not just problems

**Anti-pattern: Vague rejection**

> "This doesn't work. Try again."

**Better:**

> "The dialogue in paragraph 3 breaks character voice. The protagonist uses modern slang inconsistent with the Victorian setting. Revise to use period-appropriate language."

---

## Nudging and Recovery

### Runtime Nudging

When agents skip steps or forget outputs, the system can detect and nudge.

**Nudge types:**

**Missing Output:**

> "Step 'create_draft' should produce a 'draft' artifact, but none was created. Should you create it now?"

**Unexpected State:**

> "We're in 'review' phase, but you're creating new content. Is this intentional?"

**Quality Gate Reminder:**

> "Before proceeding, the workflow requires passing 'style_check'. Should I run that check?"

### Nudge vs. Error

| Situation | Response |
|-----------|----------|
| Agent forgot step | Nudge (question) |
| Agent lacks capability | Error (fail and escalate) |
| System misconfiguration | Error |
| Ambiguous instructions | Nudge (clarify) |

Nudges are **questions**, not commands. The agent decides how to proceed.

### Failure Recovery

**Graceful degradation:**

When a specialist fails:

1. Capture failure reason
2. Attempt retry with adjusted parameters
3. Escalate to orchestrator if retry fails
4. Orchestrator may assign to different specialist

**Checkpoint recovery:**

For long-running workflows:

1. Save state after each major step
2. On failure, resume from last checkpoint
3. Don't restart entire workflow

---

## Observability

### Structured Communication

All inter-agent communication should be typed and logged:

| Type | Purpose |
|------|---------|
| `delegation` | Task assignment |
| `result` | Work completion |
| `question` | Clarification request |
| `status` | Progress update |
| `error` | Failure notification |

### Tracing

Each task should have:

- Unique identifier
- Parent task reference (for sub-tasks)
- Timestamps for start/end
- Agent assignments
- Outcome status

This enables:

- Debugging coordination issues
- Performance analysis
- Audit trails

---

## Anti-Patterns

### Orchestrator as Bottleneck

**Problem:** Orchestrator tries to do everything, doesn't delegate enough.

**Fix:** Clear boundaries on orchestrator scope. Force delegation for domain work.

### Context Telephone

**Problem:** Information degrades as it passes through multiple agents.

**Fix:** Pass original artifacts, not summaries of summaries. Reference shared state.

### Delegation Ping-Pong

**Problem:** Agents delegate back and forth without progress.

**Fix:** Clear ownership. Agent who receives task must complete or explicitly fail.

### Silent Failure

**Problem:** Agent fails but doesn't report. Orchestrator waits indefinitely.

**Fix:** Timeout mechanisms. Require explicit success/failure response.

### Role Confusion

**Problem:** Agents do work outside their archetype.

**Fix:** Clear role definitions. Runtime enforcement for critical boundaries (e.g., orchestrators don't create content).

---

## Quick Reference

| Pattern | When to Use | Key Consideration |
|---------|-------------|-------------------|
| Hub-and-spoke | Clear task boundaries | Orchestrator cognitive load |
| Hierarchical | Complex domains | Communication overhead |
| Peer-to-peer | Autonomous collaboration | Consistency risk |
| Parallel delegation | Independent tasks | Integration strategy |
| Sequential delegation | Step dependencies | Feedback between steps |
| Self-organizing teams | Adaptive work | Clear lead role |
| Rework loops | Quality enforcement | Max cycle limits |
| Nudging | Forgotten steps | Question, don't command |

| Anti-Pattern | Symptom | Fix |
|--------------|---------|-----|
| Bottleneck orchestrator | Single agent overloaded | Force delegation |
| Context telephone | Information degradation | Reference original artifacts |
| Delegation ping-pong | No progress | Clear ownership |
| Silent failure | Hanging tasks | Timeouts, explicit responses |
| Role confusion | Boundary violations | Runtime enforcement |

---

## See Also

- [Agent Prompt Engineering](agent_prompt_engineering.md) — Prompt design for individual agents
- [Branching Narrative Construction](../narrative-structure/branching_narrative_construction.md) — Decomposition strategies for complex generation
