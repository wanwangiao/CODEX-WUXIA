# Combat System Specification

## Goals
- Recreate the "以快制慢" tempo of wuxia duels through an action gauge that rewards speed without letting it dominate.
- Support text-first battle narration synchronized with lightweight animation cues.
- Provide hooks for counterplay (拆招), status effects, and scripted AI behaviours suitable for idle simulations.

## Core Concepts
### Action Gauge
- **Threshold**: `ActionThreshold = 1000` by default.
- **Tick Rate**: Simulation advances in `TickDuration = 0.25s` slices.
- **Increment Formula**: `Gauge += (BaseSpeed * SpeedScaling + BuffDelta + RandomJitter) * TickDuration`.
  - `BaseSpeed`: Derived from character stats, equipment, and active buffs.
  - `SpeedScaling`: Default `1.0`; can be adjusted globally for encounter pacing.
  - `BuffDelta`: Sum of additive modifiers from moves or statuses.
  - `RandomJitter`: Optional ±3% noise to avoid deterministic loops.
- **Overflow Handling**: Upon acting, subtract `ActionThreshold`; leftover value carries toward next turn.
- **Soft Cap**: Apply diminishing returns when `BaseSpeed` exceeds encounter `SpeedSoftCap`:
  ```
  EffectiveSpeed = BaseSpeed if BaseSpeed <= SpeedSoftCap
                  else SpeedSoftCap + (BaseSpeed - SpeedSoftCap) * 0.35
  ```

### Turn Resolution Pipeline
1. **Ready Check**: When gauge ≥ threshold and combatant is not stunned/rooted.
2. **Intent Selection**:
   - Idle AI consults a scripted priority list (`MoveScripts`) with condition checks (hp %, enemy tags, cooldowns).
   - Player-configured script slots for manual override.
3. **Pre-Action Triggers**:
   - Resolve start-of-turn statuses (e.g., poison ticks, stance decay).
   - Evaluate counter windows—defender may pre-empt if holding a `PreparedCounter`.
4. **Narrative Rendering**:
   - Assemble text from move template segments `setup`, `strike`, `afterglow` with contextual substitutions.
   - Emit animation cues (e.g., `"slash_arc"`) for the UI layer.
5. **Mechanical Resolution**:
   - `HitChance = BaseAccuracy + AccuracyBuffs - TargetEvasion`.
   - On hit, compute damage via `BaseDamage * (1 + YinYangBonus + ComboMultiplier) - TargetMitigation`.
   - Trigger secondary effects (bleed, slows, buffs) defined on the move.
6. **Aftermath**:
   - Apply gauge modifiers (`Gauge += MomentumBonus` or `Gauge *= SlowFactor`).
   - Queue counter opportunities: defending characters gaining `CounterPrepared` for X ticks.
   - Log outcome to battle transcript with severity tags (`success`, `countered`, `fumble`).

### Counterplay &拆招
- **Counter Rating (`CR`)**: Derived from stats, move tags, and statuses.
- **Counter Window**: Moves with `counterTag` grant defenders a window measured in ticks. If defender gauge ≥ `CounterThreshold` before window expires, a counter action triggers.
- **Resolution**:
  - `CounterScore = Defender.CR + SpeedDelta + CounterBonuses`.
  - `AttackScore = Attacker.Momentum - CounterPenalties`.
  - If `CounterScore >= AttackScore`, attacker is interrupted; play `counter` template and optional reversal damage.
  - On failure, defender loses `CounterPrepared` but gains a minor speed boost to signal near-miss.

### Status Effects
- **Buff**: Positive effect with duration in ticks and stacking rules (`stack`, `refresh`, `exclusive`).
- **Debuff**: Negative effect with cleanse difficulty and potential to reduce gauge gain.
- **Stance**: Special buff altering move availability (e.g., `凌波身法` enabling speed surges). Only one stance active per character.

## Data Structures
```yaml
MoveDefinition:
  id: string
  name: string
  weaponFamily: [拳掌|劍|刀|槍|棍|暗器|鞭]
  tier: [foundation|specialization|ultimate]
  tags: [yin, soft, counter]
  speedBias: float   # modifies gauge after use (e.g., 0.9 for faster follow-up)
  cost:
    qi: int
    stamina: int
  template:
    setup: ["{attacker}沉肩墜肘，氣沉丹田。"]
    strike: ["一記『{moveName}』疾攻而至，掌風如驟雨。"]
    afterglow: ["{defender}胸口氣血翻湧，退後三步。"]
  effects:
    damage:
      base: 120
      scaling:
        innerPower: 1.1
        technique: 0.4
    statusesApplied:
      - id: "stagger"
        chance: 0.35
        durationTicks: 6
    counterWindow:
      ticks: 4
      counterTemplate: "{defender}以柔化剛，借力打力。"
```

## Sample Tick Pseudocode
```python
for tick in ticks:
    for combatant in combatants:
        combatant.gauge += compute_increment(combatant, tick)
        if combatant.can_act():
            action = combatant.choose_action()
            resolve_pre_action(action)
            render_text(action)
            resolve_mechanics(action)
            resolve_aftermath(action)
```

## Logging & Replay
- Maintain chronological log entries with fields: `timestamp`, `actor`, `target`, `moveId`, `outcome`, `text`, `animationCue`.
- Aggregate logs into digestible segments for idle recap (e.g., group every 5 actions into a paragraph).

## Balancing Hooks
- Expose `SpeedSoftCap`, `CounterThreshold`, and `HitChanceFloor` via configuration files for quick tuning.
- Include telemetry counters (average gauge per minute, counter success rate) to guide balancing passes.

## Next Actions
1. Implement gauge simulator CLI that reads YAML move definitions and prints battle logs.
2. Author baseline move set per weapon family following the schema above.
3. Create unit tests covering gauge overflow, counter success/failure, and status stacking.
