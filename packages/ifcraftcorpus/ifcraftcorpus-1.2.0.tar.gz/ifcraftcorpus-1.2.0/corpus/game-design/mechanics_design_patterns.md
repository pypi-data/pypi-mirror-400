---
title: Mechanics Design Patterns
summary: Designing game mechanics for interactive fiction—stats, skill checks, economy, inventory, and ludonarrative harmony.
topics:
  - game-design
  - mechanics
  - rpg-systems
  - stats
  - skill-checks
  - economy
  - inventory
  - ludonarrative-dissonance
cluster: game-design
---

# Mechanics Design Patterns

Craft guidance for designing game mechanics in interactive fiction—integrating numbers with narrative.

---

## The Role of Stats

### Why Have Stats?

Stats (Strength, Intelligence, relationships, money) allow:

1. **Gating:** Controlling access to content based on past choices.
2. **Expression:** Letting players define *who* their character is.
3. **Consequence:** Accumulating small choices into major outcomes.

### Types of Stat Systems

**1. Personality Traits (Opposed Pairs)**

* *Example:* Stoic vs. Emotional, Ruthless vs. Merciful.
* *Pattern:* Increasing one decreases the other (0-100 scale).
* *Pros:* Enforces character consistency.
* *Cons:* Can punish nuance (players min-maxing to keep stats high).

**2. Skills/Attributes (Accumulative)**

* *Example:* Strength, Hacking, Persuasion.
* *Pattern:* Start at 0, gain points via usage/training.
* *Pros:* Clear sense of progression.
* *Cons:* "Jack of all trades" players may fail all high-level checks.

**3. Hidden Variables**

* *Example:* Trust, Suspicion, Corruption.
* *Pattern:* Tracked silently.
* *Pros:* Surprising but logical consequences.
* *Cons:* Players may feel cheated if they don't understand the cause.

---

## Designing Skill Checks

### Probability vs. Threshold

**Threshold (Deterministic):**

* `If Strength > 5: Success.`
* *Best for:* Narrative consistency. "My character is strong, so they force the door."
* *Risk:* Players "stat-checking" (savescumming) or feeling locked out.

**Probability (Random/Dice):**

* `Roll d20 + Strength. DC 15.`
* *Best for:* Tension, chaotic situations.
* *Risk:* Failing a check despite building a specialist feels bad.

**Best Practice for IF:**
Use **Thresholds** for competency (you know Kung Fu or you don't).
Use **Probability** for external chaos (does the guard look this way?).

### The "Fail Forward" Principle

Never let a failed check stop the story.

* **Success:** You pick the lock silently.
* **Failure:** You pick the lock, but break your pick/alert the guards.
* **Dead End (Avoid):** "You can't open the door. Try again."

---

## Economy Design

### Scarcity vs. Abundance

* **Survival Horror:** Every bullet counts. Scarcity creates tension.
* **Power Fantasy:** Money is trivial. Abundance creates freedom.

### Faucets and Sinks

* **Faucet:** Where resources come from (loot, rewards, salary).
* **Sink:** Where resources go (bribes, gear, healing, upkeep).
* *Balance:* If Faucets > Sinks, currency becomes meaningless.

### The "Shopping List" Problem

In text games, shopping can be boring.

* **Fix:** Make items narrative. Not "Sword +1", but "Your father's rusted blade."
* **Fix:** Limit inventory slots to force meaningful choices.

---

## Inventory Management

### The "Bag of Holding"

Infinite inventory leads to "use everything on everything" puzzle solving.

### Constrained Inventory

* "You can carry 3 items."
* Forces strategic thinking.
* *Example:* Do I take the gun or the medkit?

### Key Items

Items that unlock narrative paths (Keys, Evidence).

* *Rule:* Never let key items be sold/dropped unless that is a valid failure state.

---

## Ludonarrative Dissonance

When the mechanics contradict the story.

* *Example:* Story says "Urgent time pressure!" but Mechanics allow "Rest for 8 hours to heal."
* *Example:* Character is a "Pacifist" but Gameplay requires killing to level up.

**Harmonization Techniques:**

1. **Diegetic UI:** Health is "Willpower" or "Blood Loss."
2. **Mechanic Metaphors:** Sanity meters in Lovecraftian games reflect narrative themes.
3. **Aligned Incentives:** If the story rewards stealth, don't give XP only for combat kills.

---

## Quick Reference

| System | Best Use |
| :--- | :--- |
| **Opposed Stats** | Defining personality (Choice of Games style). |
| **Skill Thresholds** | Rewarding specialization (RPG style). |
| **Hidden Stats** | Relationships, mystery clues. |
| **Fail Forward** | Ensuring pacing never breaks on failure. |

---

## See Also

* [Branching Narrative Construction](../narrative-structure/branching_narrative_construction.md)
* [Player Analytics Metrics](../craft-foundations/player_analytics_metrics.md)
