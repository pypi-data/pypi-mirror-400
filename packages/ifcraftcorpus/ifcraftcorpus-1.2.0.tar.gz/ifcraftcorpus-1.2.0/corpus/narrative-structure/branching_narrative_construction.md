---
title: Branching Narrative Construction
summary: Methodologies for building branching narratives—structural patterns, construction processes, small-scale choice architecture, and LLM generation strategies.
topics:
  - branching-narrative
  - construction-methodology
  - structural-patterns
  - choice-architecture
  - topology-design
  - state-tracking
  - scope-management
  - llm-generation
  - meta-prompting
  - decomposition
cluster: narrative-structure
---

# Branching Narrative Construction

Methodologies for building branching narratives from the ground up—structural patterns, construction processes, and the interplay between large-scale architecture and small-scale choice design.

This document complements `branching_narrative_craft.md` (what makes choices meaningful) by focusing on **how to construct** branching structures.

---

## Structural Patterns

Different patterns suit different narrative goals. Most successful interactive fiction combines multiple patterns.

### Time Cave

Pure branching with minimal re-merging. Each choice leads to more choices.

**Structure:**

- All choices roughly equal significance
- No rejoining or reusing content
- Many unique endings

**Characteristics:**

- Content grows exponentially (3 binary choices = 8 endings)
- Broad rather than long
- Players miss most content per playthrough

**Best for:** Short experimental IF, replay-focused works, high-stakes consequences.

**Tradeoff:** Unsustainable at scale. A 10-choice time cave needs 1,024 endings.

### Gauntlet

Linear central thread with pruned side branches that quickly rejoin or terminate.

**Structure:**

- One primary story path
- Side branches via failure, backtracking, or quick rejoining
- Minimal state-tracking needed

**Characteristics:**

- Creates atmosphere of constraint or hazard
- Most players see core content
- Easy to author

**Best for:** Horror, survival, constrained protagonist situations.

**Tradeoff:** Limited player agency. May feel restrictive despite branching appearance.

### Branch and Bottleneck

Branches diverge then reconverge at key story beats.

**Structure:**

- Paths fan out from bottleneck points
- Heavy state-tracking accumulates differences
- Convergence at narrative milestones

**Characteristics:**

- Sustainable at any length
- Divergence accumulates over time
- Different journeys, shared destinations

**Best for:** Character growth narratives, commercial IF, long-form stories.

**Tradeoff:** Early playthroughs feel similar. Requires substantial content.

### Quest / Modular Clusters

Distinct modular branches organized by geography or topic rather than time.

**Structure:**

- Tightly-grouped node clusters
- Many approaches to single situations
- Episodic rather than linear

**Characteristics:**

- Suited for exploration narratives
- Consistent world, variable paths
- Can be assembled non-linearly

**Best for:** Open-world narratives, investigation stories.

**Tradeoff:** Large minimum scope. Less overall narrative direction.

### Sorting Hat

Heavy early branching determines major late-game branch. Later sections often linear.

**Structure:**

- Early choices set player on track
- Tracks diverge significantly
- Within each track: linear or light branching

**Characteristics:**

- Compromise between breadth and depth
- Multiple complete arcs
- Signals player influence upfront

**Best for:** Games with classes, factions, or major identity choices.

**Tradeoff:** Authors effectively write multiple games. Players may notice funneling.

### Loop and Grow

Central thread loops repeatedly. State-tracking unlocks new options each cycle.

**Structure:**

- Core loop structure (location, routine, time period)
- State changes unlock new content on return
- Progressive revelation through repetition

**Variant (Hub and Spoke):** Central hub with branches that return.

**Characteristics:**

- Emphasizes regularity while maintaining momentum
- Exploration across cycles
- Natural fit for time-loop or trapped narratives

**Best for:** Groundhog Day stories, workplace/routine settings, mystery investigation.

**Tradeoff:** Requires narrative justification for repetition.

---

## Beyond Branching

Pure branching isn't the only option. Alternative architectures avoid exponential content multiplication.

### Quality-Based Narrative (QBN)

Content unlocks based on accumulated stats rather than predetermined paths.

**How it works:**

- Storylets (atomic story pieces) tagged with unlock conditions
- Player stats (skills, relationships, items) determine availability
- System surfaces relevant storylets based on current state

**Advantages:**

- Modular content addition without cascading obligations
- Players create unintended narrative chains
- Scales without exponential growth

**Challenges:**

- Significant bookkeeping for authors
- Narrative spine less visible during authoring
- Requires robust state management

**Examples:** Fallen London, many roguelikes.

### Salience-Based Narrative

System selects most contextually relevant content from a pool.

**How it works:**

- Dialogue/scenes tagged with applicability conditions
- Engine matches current world state to available content
- Most relevant option surfaces automatically

**Advantages:**

- Reactive feel without explicit choice points
- Easy to add specialized variants gradually
- Doesn't require comprehensive coverage

**Best for:** Environmental dialogue, NPC reactions, layered commentary.

**Examples:** Firewatch, Left 4 Dead's dynamic dialogue.

### Waypoint Narrative

System pathfinds toward authored beats while player redirects.

**How it works:**

- Key story beats defined as waypoints
- System constantly navigates toward next waypoint
- Player choices detour but system "heals" back to spine

**Advantages:**

- Reduces combinatorial explosion
- Maintains narrative direction
- Player agency in journey, author control of destination

**Challenges:**

- Can feel like fighting the system
- Requires sophisticated dialogue management

---

## Construction Process

### Phase 1: Concept and Scope

**Define the container:**

- Genre, tone, target length
- Core theme or question
- Target structure pattern (or hybrid)

**Set scope constraints:**

- Number of major branches
- Target passage count
- State variables to track

**Key question:** What kind of story is this? A character growth story (branch-and-bottleneck), an exploration (quest), a transformation (sorting hat)?

### Phase 2: Spine First

Before branching, establish the core arc.

**Identify:**

- Beginning state (character, world)
- Ending state (or ending states)
- Key transformation beats

**The spine is:**

- What every player experiences in some form
- The narrative through-line
- Not necessarily the "main path"—may be the emotional arc underlying all branches

**Why spine first:**

- Prevents meandering branches that lose narrative purpose
- Ensures every path serves the same thematic goal
- Provides anchor points for convergence

### Phase 3: Anchor Points

Declare structural anchors before designing branches.

**Anchors include:**

- **Hubs:** Where player choice fans out
- **Bottlenecks:** Where paths reconverge
- **Gates:** Where progression requires conditions
- **Endings:** Terminal states

**Place anchors on spine:**

- Where do players return?
- What must happen regardless of path?
- Where does meaningful divergence occur?

**Key insight:** Anchors are structural, declared early. They constrain branching rather than emerging from it.

### Phase 4: Fracture Points

Identify where the spine can meaningfully diverge.

**Good fracture points:**

- Character decisions with genuine stakes
- Points where different approaches lead to different content
- Moments where player values can express

**Bad fracture points:**

- Cosmetic choices masquerading as meaningful
- Points where all options lead to same outcome
- Random selection without player investment

**For each fracture, define:**

- What distinguishes the options
- How long before convergence (or termination)
- What state changes result

### Phase 5: Branch Expansion

Expand one branch at a time, not simultaneously.

**Process:**

1. Select highest-priority fracture
2. Design the branch content
3. Validate connection to anchors
4. Repeat for next fracture

**Why sequential:**

- Prevents disconnected parallel narratives
- Each branch can reference established content
- Scope stays visible and controlled

### Phase 6: Connection and Validation

Verify the topology before writing prose.

**Check:**

- All passages reachable from start
- All branches connect to anchors or endings
- Gates have obtainable conditions
- No orphaned content

**Balance check:**

- No branch dramatically shorter than others (unless intentional)
- All paths satisfying
- Consequences proportional to choices

---

## Small-Scale Choice Patterns

Within any structure, local choice patterns create texture.

### Confirmation-Required Choice

Escalating prompts before risky decisions.

> "Are you sure?"
> "This cannot be undone. Proceed?"

**Effect:** Player opts in multiple times. Consequence feels earned.

### Track-Switching Choice

Multiple beats to change direction before commitment.

**Effect:** Mirrors genuine protagonist conflict. Allows mid-narrative reversals.

### Scored Choice

Repeated decisions in one direction accumulate points.

**Effect:** Outcome determined by statistical weight, not single final selection.

### Re-enterable Node

Classic conversation tree—explore sub-topics before progression.

**Effect:** Combats exposition dumps through interactive discovery.

### Floating Choice

Choice available across multiple passages until used.

**Effect:** Player timing matters. Creates strategic layer.

### Delayed Consequence

Choice in early passage affects later passage.

**Effect:** Reward for attentive players. Must signpost connection when consequence arrives.

---

## Scope Management

Branching multiplies content. Managing scope is essential.

### The Exponential Problem

- 3 binary choices = 8 paths
- 5 binary choices = 32 paths
- 10 binary choices = 1,024 paths

**Mitigation strategies:**

- Branch and bottleneck (converge regularly)
- State-based variation (same nodes, different text)
- Delayed branching (choices affect later, not immediately)

### Content Efficiency

**High efficiency:** State-based variations, QBN, salience systems.

**Medium efficiency:** Branch-and-bottleneck, hub-and-spoke.

**Low efficiency:** Time cave, full parallel tracks.

### The Vignette Method

From Choice of Games methodology:

1. Brainstorm 15-20 vignette ideas
2. Identify key variables (honor, cleverness, relationships)
3. Refine to 8-12 scenes with cohesive structure
4. Prototype to test balance
5. Iterate based on playtest

---

## Common Mistakes

### Branching Too Early

Divergence in chapter 1 creates parallel games.

**Fix:** Use early choices for state, not structure. Branch later.

### Converging Too Abruptly

"All roads lead to Rome" destroys agency.

**Fix:** Let differences persist. Converge at natural milestones.

### Forgetting the Spine

Branches meander without narrative purpose.

**Fix:** Every branch should serve the same thematic goal.

### State Without Consequence

Tracking variables that never affect anything.

**Fix:** Every tracked variable should pay off visibly.

### Undeclared Gates

Players hit walls without understanding why.

**Fix:** Foreshadow gate conditions. Make requirements clear.

### Symmetric Branches

All branches equal length, equal weight, interchangeable.

**Fix:** Asymmetry creates interest. Some paths should be harder, shorter, more rewarding.

---

## LLM Generation Strategies

When using LLMs to generate branching narratives, specific strategies address model limitations. The construction process above applies, but with additional techniques.

### Why LLMs Struggle with Branching

LLMs face specific challenges:

- **State tracking degrades** over long generation sessions
- **Character motivation hallucinates** from training data rather than established story
- **Full topology requests** produce deviation, stagnation, or poor branching point selection
- **Simultaneous branch generation** creates disconnected parallel narratives
- **Default emotional arcs** trend toward "happily ever after" with less suspense

### Meta-Prompting

Ask the LLM to generate prompts that will guide subsequent generation, rather than generating content directly.

**Why it works:**

- Indirection improves output quality
- LLM reasons about what questions to ask before answering
- Avoids over-literal instruction following

**Example:**

Instead of:
> "Write an alternate path where the protagonist betrays the faction."

Use:
> "What prompt would generate a compelling alternate path that maintains the protagonist's established motivation while exploring betrayal? Consider what internal conflict would make this choice feel earned."

Then use the generated prompt for actual branch creation.

### Emotional Arc Scaffolding

Use emotional trajectory (rise, fall, tension, release) as structural backbone.

**Patterns:**

- **Rise:** Building tension, escalating stakes
- **Fall:** Setback, loss, descent
- **Rise-Fall-Rise:** Classic hero's journey shape
- **Fall-Rise:** Redemption arc

**Application:**

1. Define the emotional shape for the spine
2. Assign different emotional patterns to major branches
3. Request specific trajectory when generating each branch

**Why it works:**

- Provides universal structure across cultures
- Guides pacing without dictating content
- Counters LLM tendency toward flat, homogeneous arcs

### Three-Act Anchoring

Use three fixed structural points to ground generation:

1. **Inciting Incident** — What disrupts the status quo
2. **Crisis** — The point of maximum tension/decision
3. **Climax** — The decisive action/resolution

**Application:**

- Identify these three points on the spine FIRST
- All branches must pass through (or meaningfully subvert) these anchors
- When generating branches, constrain them to reach the next anchor

**Why it works:**

- LLMs struggle with branching point selection when considering all events equally
- Fixed anchors provide structural grounding
- Prevents branches from drifting away from narrative purpose

### Bottom-Up Iteration

Generate one complete storyline first, then iteratively add branches.

**Process:**

1. Generate the spine as a complete linear story
2. Validate spine coherence
3. Select first fracture point
4. Generate ONE alternate branch from that point
5. Validate branch connects to anchors
6. Repeat for next fracture

**Why it works:**

- Each branch can reference established content
- Produces authentic branching (not parallel narratives)
- Scope stays visible and controlled

**Contrast with what fails:**

> "Generate a branching narrative with three possible paths from the beginning"

This produces three separate stories, not one story with branches.

### State/Goal Semantics

Include explicit state information with each generation request.

**For each node, specify:**

- **Character State:** Where the protagonist is emotionally/physically
- **Goal:** What they're trying to achieve
- **Key Decision:** The choice they made to reach this point
- **Alternate Decision:** What they could have done instead

**Why it works:**

- Prevents motivation hallucination
- Maintains consistency across branches
- Eliminates illogical or non-meaningful choices

**Example prompt structure:**

```
Current state: Elena has discovered the conspiracy but hasn't told anyone.
Goal: Decide whether to confront Director Mills alone or gather allies first.
Key decision leading here: She chose to investigate rather than report.
Alternate that would have led elsewhere: Reporting would have triggered Act 2 early.

Generate the confrontation scene, maintaining her established caution and her conflicted loyalty to Mills as a mentor.
```

### Validation Between Phases

Always validate topology BEFORE generating prose or briefs.

**Between phases, check:**

- All passages reachable from start
- All branches connect to declared anchors or endings
- Gates have obtainable conditions
- Scope budget not exceeded (N passages = N PIDs maximum)

**Why it works:**

- Structural errors caught late require expensive rework
- Downstream phases (prose writing) cannot fix topology problems
- Early validation keeps scope under control

---

## LLM Failure Modes

Specific patterns that produce poor results.

### Full Topology in One Shot

**Symptom:** Asking LLM to "generate a complete branching narrative" or "create the full topology."

**Result:** Deviation from storyline, story stagnation at single decisions, poor branching point selection.

**Fix:** Use the Grow decomposition: spine → anchors → fractures → branches → connections → briefs.

### Simultaneous Branch Generation

**Symptom:** Prompting for multiple alternate paths in a single request.

**Result:** Disconnected parallel narratives that don't feel like branches of the same story.

**Fix:** Generate one branch at a time. Each branch references established content before the next is generated.

### Discovering Anchors During Branching

**Symptom:** Designing branches before declaring where convergence occurs.

**Result:** Hubs and gates emerge inconsistently. Branches don't properly converge. Structure feels arbitrary.

**Fix:** Declare anchors (hubs, gates, bottlenecks) BEFORE designing branches. Anchors constrain branching.

### State Tracking Degradation

**Symptom:** Long generation sessions without explicit state summaries.

**Result:** LLM forgets established context. Characters act inconsistently. Plot holes emerge.

**Fix:** Include explicit state summary with each generation request. Validate state consistency between phases.

### Motivation Hallucination

**Symptom:** Characters suddenly caring about things not established in the story.

**Result:** Actions feel arbitrary. Branches don't feel like the same character's story.

**Fix:** Include character state and goal in each node. Ground all decisions in established motivation.

### Homogeneous Emotional Arcs

**Symptom:** All generated branches follow "challenge → quick success → happy ending."

**Result:** Branches feel interchangeable. Less suspense, fewer setbacks.

**Fix:** Explicitly request varied emotional trajectories. Specify setbacks, complications, delayed gratification. Use emotional arc scaffolding with different patterns per branch.

---

## Research Basis

These strategies derive from recent research on LLM narrative generation:

| Source | Key Finding |
|--------|-------------|
| WHAT-IF (2024) | Meta-prompting and five-phase decomposition produces coherent branching from linear input |
| GENEVA (2024) | Bottom-up iteration outperforms top-down generation; better-documented settings yield richer narratives |
| Emotional Arc Studies (2025) | Emotional arc as structural backbone guides branching while allowing content variation |
| Narrative Planning Benchmarks | GPT-4 tier LLMs generate causally sound stories at small scales; character intentionality and dramatic conflict remain challenging |
| Human-Level Narrative Studies | LLMs default to happier arcs, earlier turning points, less suspense than human storytellers |

---

## Quick Reference

| Construction Phase | Output | Key Question |
|--------------------|--------|--------------|
| Concept & Scope | Pattern choice, constraints | What kind of story? |
| Spine First | Core arc, transformation | What happens regardless of choices? |
| Anchor Points | Hubs, bottlenecks, gates | Where do players return/converge? |
| Fracture Points | Meaningful divergences | Where can this go differently? |
| Branch Expansion | Content for each path | What happens on this branch? |
| Connection | Validated topology | Does everything connect properly? |

| Pattern | Scope Efficiency | Narrative Depth | Player Agency |
|---------|------------------|-----------------|---------------|
| Time Cave | Low | Low (broad) | High |
| Gauntlet | High | High | Low |
| Branch & Bottleneck | Medium | Medium-High | Medium |
| Quest/Modular | Medium | Medium | High |
| Sorting Hat | Low-Medium | High (per track) | Medium |
| Loop and Grow | High | Medium | Medium |
| QBN/Salience | High | Variable | High |

| LLM Strategy | What It Addresses | Key Technique |
|--------------|-------------------|---------------|
| Meta-prompting | Over-literal responses | Ask LLM to generate prompts first |
| Emotional arc scaffolding | Homogeneous arcs | Specify Rise/Fall patterns per branch |
| Three-act anchoring | Poor branching point selection | Fix Inciting/Crisis/Climax first |
| Bottom-up iteration | Disconnected parallel narratives | One branch at a time, sequential |
| State/goal semantics | Motivation hallucination | Include state summary each request |
| Validation between phases | Late-caught structural errors | Check topology before prose |

| LLM Failure Mode | Symptom | Fix |
|------------------|---------|-----|
| Full topology in one shot | Deviation, stagnation | Grow decomposition |
| Simultaneous branches | Disconnected narratives | Sequential generation |
| Discovering anchors late | Inconsistent convergence | Declare anchors early |
| State degradation | Inconsistent characters | Explicit state summaries |
| Motivation hallucination | Arbitrary actions | Ground in established goals |
| Homogeneous arcs | Interchangeable branches | Request varied trajectories |

---

## See Also

- [Branching Narrative Craft](branching_narrative_craft.md) — What makes choices meaningful
- [Diegetic Design](../craft-foundations/diegetic_design.md) — Gates as in-world obstacles, contrastive choices
- [Nonlinear Structure](nonlinear_structure.md) — Time manipulation and parallel narratives
- [Pacing and Tension](pacing_and_tension.md) — Emotional rhythm for arcs
- [Scope and Length](../scope-and-planning/scope_and_length.md) — Managing branching scope
- [Agent Prompt Engineering](../agent-design/agent_prompt_engineering.md) — Prompt design for LLM agents
- [Multi-Agent Patterns](../agent-design/multi_agent_patterns.md) — Orchestration for complex generation
