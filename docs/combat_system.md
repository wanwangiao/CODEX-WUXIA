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

## Example Battle Flow
The following walkthrough demonstrates how the gauge, counter windows, and narration interplay during a short duel. It assumes
the default `ActionThreshold = 1000` and `TickDuration = 0.25s`.

| Tick | Actor Gauge | Defender Gauge | Event | Narration Highlight |
| ---- | ----------- | -------------- | ----- | ------------------- |
| 0.00 | 0 / 1000 (陸雲) | 0 / 1000 (秦霜) | Initialization | `陸雲沉肩調息，秦霜身形如竹。` |
| 0.25 | 180 | 140 | Gauges advance by base speed (陸雲 720、秦霜 560). No one ready. | — |
| 0.50 | 360 | 280 | 陸雲預設快攻套路《飛燕連環》進入候選。 | `陸雲腳尖點地，身影晃動。` |
| 0.75 | 540 | 420 | 秦霜準備拆招《柔雲化勁》，被標記為 `CounterPrepared`。 | `秦霜氣脈沉穩，掌心柔力如潮。` |
| 1.00 | 720 | 560 | 陸雲 gauge ≥ 1000? 尚未；但 momentum buff (+120) 讓下個 tick 可超標。 | — |
| 1.25 | 900 | 700 | 陸雲仍未達閾值；秦霜 gauge 700 尚無法拆招。 | — |
| 1.50 | 1080 | 840 | 陸雲 first to act，施展《飛燕連環》。Gauge 扣除 1000 後餘 80。 | `掌影如燕掠空，連出三記快拍。` |
|      |           |                | Counter Check | 秦霜 gauge 840 ≥ `CounterThreshold` 600，觸發拆招比較：`CounterScore = 65 + (840-80)/10 = 149`，`AttackScore = 120`，成功。 |
|      |           |                | Counter Action | `秦霜掌心柔力一轉，借勢拍向陸雲胸口。` 攻擊中斷，陸雲 gauge 清零並施加 `slow`。秦霜獲得 200 gauge 奬勵。 |
| 1.75 | 200 | 40 | 陸雲因 `slow` 下次增量僅 120；秦霜經反制獲得先手機會。 | — |
| 2.00 | 320 | 520 | 秦霜 gauge ≥ 1000? 尚未，但下一 tick 將達到。 | — |
| 2.25 | 440 | 1000 | 秦霜 gauge 達 1000，施展《太虛雲掌》，造成 210 傷害並附 `stagger`。 | `雲掌柔中帶剛，陸雲氣血翻湧。` |
| 2.50 | 560 | 240 | 陸雲受到 `stagger`，下次可行動門檻提高 15%。 | `陸雲連退數步，尚需調息。` |
| 2.75 | 680 | 380 | 雙方進入下一輪節奏，戰鬥持續。 | — |

Key takeaways:
- **速度差帶來節奏優勢**：陸雲起手較快，但秦霜透過拆招逆轉先手。
- **拆招與狀態交織**：成功拆招立即重置攻擊者行動槽並施加 `slow`，為後續《太虛雲掌》鋪路。
- **敘事與數值同步**：每個事件皆對應文字段落與可觸發的動畫 cue，方便 UI 轉接。

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
