# Wuxia Idle Game Design Overview

## Vision
Create a text-driven idle (AFK) wuxia RPG that marries the strategic depth of "九陰真經" with lightweight UI animations. Players witness richly described martial duels while configuring automation rules that continue to run while they are offline.

## Core Pillars
1. **Speed-Driven Combat** – Battles are resolved through an action gauge that emphasizes "以快制慢" and reactive counterplay.
2. **Idle Growth Loop** – Characters train, gather loot, and trigger story events automatically, returning with a battle log recap.
3. **Narrative Flexibility** – Modular text templates and events let designers rapidly add new moves, encounters, and story arcs.

## Player Fantasy
- **Role**: A wandering martial artist that eventually establishes a martial hall, recruiting spirits/disciples (武魂/俠客) with unique traits.
- **Motivation**: Master rare manuals, cultivate inner power, and discover the secrets of the Nine Yin Manual.
- **Engagement**: Configure builds, read stylized battle logs, respond to pop-up incidents, and trade loot via the auction house.

## High-Level Loop
```mermaid
flowchart LR
    A[Select Activity / Set Script] --> B[Idle Simulation]
    B --> C[Battle/Event Log Recap]
    C --> D[Rewards & Resources]
    D --> E[Strengthen Characters / Unlock Content]
    E --> A
```

## Feature Roadmap
| Phase | Scope | Goal |
| --- | --- | --- |
| **Prototype** | Core combat (speed gauge, text renderer), simple idle simulation, manual list of moves | Validate feel of "文字＋動畫" battles |
| **Alpha** | Character growth (experience, equipment), idle job board, modular events, minimal UI | Provide long-term retention hooks |
| **Beta** | Auction house, multiplayer raids (team co-op), ladder (華山論劍), expanded storytelling | Support community-oriented systems |

## Combat System Detail
### Action Gauge
- Each combatant owns a gauge with threshold `ActionThreshold` (e.g., 1000).
- Gauge increases per tick: `Increment = BaseSpeed * BuffMultiplier + RandomJitter`.
- When gauge ≥ threshold, combatant acts, spending `ActionCost` (~threshold) and possibly retaining overflow for quick follow-up.
- Soft cap on speed ensures diminishing returns to prevent infinite loops.

### Action Resolution Steps
1. **Determine Intent**: Use scripting AI or player choice to pick a move.
2. **Pre-Action Checks**: Resolve control effects (stuns, slows, immobilize).
3. **Narrative Template**: Fetch move template by tier (起勢/出招/收招) and apply character traits.
4. **Mechanical Resolution**:
   - Hit chance via `Accuracy vs. Evasion` influenced by yin/yang alignment.
   - Damage formula factoring weapon tier, inner power, combo chains.
   - Counter/拆招 check if defender has reactive move queued.
5. **Aftermath**: Apply buffs/debuffs, adjust gauge modifiers, log textual outcome, trigger lightweight animation cue.

### Move Taxonomy
- **Weapon Families**: 拳掌、劍、刀、槍、棍、暗器、鞭。
- **Flow Structure**: Each move defined by `setup`, `strike`, `afterglow` segments for text & animation alignment.
- **Tags**: `yin/yang`, `hard/soft`, `range`, `speedBias`, `counterType`.
- **Learning Path**:
  - `Foundation`: unlocks basic moves within a family.
  - `Specialization`: branches that reward consistent usage (熟練度) or quest completion.
  - `Ultimate`: rare manuals requiring specific yin-yang balance, event tokens, or inner power thresholds.

### Counterplay Mechanics
- **拆招**: Defender compares `CounterRating + SpeedDelta` vs. attacker `Momentum`. Success interrupts and plays reactive template.
- **以柔克剛**: Soft-tagged moves reduce damage from hard-tagged opponents, encouraging loadout variety.
- **身法 Adjustments**: Certain moves temporarily boost/decrease action gauge gain, capturing "快慢互制" feel.

## Idle Simulation
- **Activity Types**: Wilderness grinding, sect meditation, escort missions, manual research.
- **Scheduling**: Player sets duration & priority; simulation generates resource yields + event seeds.
- **Event Cards**: Weighted random draws (奇遇, 衝突, 機緣). Each card stores condition checks and narrative outputs.
- **Offline Handling**: Server processes ticks; upon return, compile battle/event summaries grouped by activity.

## Progression Systems
- **Attributes**: `Qi`, `InnerPower`, `Speed`, `Technique`, `Will`. Derived stats feed combat formulas.
- **Equipment**: Weapon/armor/accessory slots with rarity, reforging, socket runes (加速, 拆招率, 內功恢復).
- **Meridians (經脈)**: Node graph representing the Eight Extraordinary Meridians + Twelve Principals. Unlocking nodes grants passive stats and occasionally new reactive options.
- **Companions**: Recruitable spirits/disciples with unique move pools, loyalty arcs, and synergy bonuses.

## Meta Systems
- **Auction House**: Player-to-player listings with taxes, batch posting automation.
- **Competitive Modes**: 華山論劍 ladder (async PvP), timed trials, sect wars.
- **Narrative Delivery**: Episodic chronicles triggered by milestone completions, delivered through formatted logs.

## Content Pipeline
- **Data-Driven Definitions**: Moves, events, NPCs, and templates stored in JSON/YAML for quick iteration.
- **Tooling Ideas**: Simple script to preview text sequences, gauge fill simulation visualizer, balancing spreadsheets.
- **Localization Friendly**: Keep narrative templates modular with placeholders (`{attacker}`, `{moveName}`, `{effect}`) for future translation.

## Next Steps
1. Detail move data schema & sample entries for each weapon family.
2. Prototype gauge simulator that outputs battle logs for a single duel.
3. Define idle event card format and offline reward calculation.
4. Draft UI wireframes focusing on battle log pane, activity planner, and resource dashboard.

