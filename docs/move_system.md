# Move System Blueprint

## Objectives
- Offer a layered progression from foundational techniques to signature ultimates for each weapon family.
- Ensure every move carries tags that influence combat AI, counterplay, and textual flavor.
- Provide designers with a data-driven template to add new moves without touching core code.

## Progression Tiers
1. **Foundation (入門)**
   - Unlock prerequisite for the weapon family.
   - Grants passive familiarity bonus: `+5%` hit chance and `+3%` counter resistance against matching family.
   - Learned via sect instructors or starting manuals.
2. **Specialization (專精)**
   - Requires foundation move at Rank 3 (熟練度 milestone) and completion of weapon-specific trials.
   - Introduces branching mechanics such as combo chains, stance switching, or status infliction.
   - Costs rare resources (e.g., sect reputation, manual fragments).
3. **Ultimate (絕學)**
   - Tied to major story events or legendary manuals.
   - Often mixes weapon families or leverages yin-yang balance thresholds.
   - Provides unique battle log templates with cinematic wording and bespoke animation cues.

## Weapon Families & Sample Flows
| Weapon | Core Fantasy | Foundation Example | Specialization Path | Ultimate Hook |
| ------ | ------------ | ------------------ | ------------------- | ------------- |
| 拳掌 | Close-range control,拆招追擊 | **羅漢推山**：陰剛，提升拆招成功率 | **螳螂纏腕**（連鎖抓取）或**太極推手**（以柔化剛） | **降龍十八掌**：連續爆發，對陽剛敵人追加震退 |
| 劍 | 流暢連段，高命中 | **清風十三劍**：陽柔，式目連接 | **青城劍閣**（身法加速）或**獨孤九劍**（拆招專精） | **天外飛仙**：速度突破，首段必中 |
| 刀 | 爆發與破甲 | **狂風刀勢**：陽剛，首擊破甲 | **血影斬**（吸血）或**霸刀弦月**（蓄勢斬） | **伏魔刀歌**：斬殺線，擊倒低血敵人 |
| 槍 | 中距離壓制、突刺 | **破雲鎗**：陽剛，距離控制 | **霸王槍**（擊退）或**化骨游龍**（穿刺多段） | **一氣化三清**：三段攻擊，附加慢速 |
| 棍 | 守禦與群控 | **伏虎棍**：陰剛，格擋提升 | **少林羅漢陣**（群攻）或**天罡北斗**（結界加護） | **降魔金身棍**：反彈傷害且群體嘲諷 |
| 暗器 | 插招與異常 | **袖裡針**：陰柔，插入行動槽 | **孔雀翎**（範圍多段）或**七蟲七花**（毒疊加） | **群玉無光**：一次性爆發附帶致盲 |
| 鞭 | 範圍牽制、節奏干擾 | **靈蛇出洞**：陰柔，延緩敵方速度 | **九節遊龍**（距離掌控）或**天蠶絲雨**（多段軟控制） | **碧海潮生**：大範圍牽制並自加速度 |

## Move Data Fields
```yaml
rankedMove:
  moveId: "luohan_push"
  tier: foundation
  maxRank: 5
  unlock:
    requirements:
      - type: "weapon_mastery"
        weapon: "fist"
        level: 1
      - type: "quest"
        id: "shaolin_initiation"
  rankRewards:
    - rank: 1
      bonus: {hitChance: 0.05}
    - rank: 3
      bonus: {counterGuard: 0.08}
      grants: "mantis_wrap"
    - rank: 5
      bonus: {speedBias: -0.05}
```

## Familiarity & 熟練度
- Every move tracks `usageXP` accrued during battles (active or idle).
- Thresholds: `Rank1` unlocked on learn, `Rank2` at 50 uses, `Rank3` at 150, `Rank4` at 300, `Rank5` at 600.
- Rank rewards can modify text templates (unlocking new adjectives) and mechanical bonuses.

## Loadout Slots
- Characters have `Primary`, `Secondary`, and `Utility` slots.
- Foundation moves must occupy `Primary` to ensure weapon identity.
- Specialization moves can fill `Secondary`; ultimates usually consume `Utility` and have cooldown measured in gauge units (e.g., 2500).

## Synergy Tags
- `comboStarter`: increases hit chance if used immediately after a stance change.
- `finisher`: gains bonus damage if combo counter ≥2.
- `counterBreaker`: reduces defender counter rating by 20% for the current action.
- `stanceShift`: toggles character stance, altering subsequent script weights.

## Example Move Set (拳掌)
```yaml
moves:
  - id: "luohan_push"
    name: "羅漢推山"
    weaponFamily: "拳掌"
    tier: "foundation"
    tags: ["yang", "hard", "comboStarter"]
    speedBias: 1.05
    cost: {qi: 15, stamina: 10}
    template:
      setup: ["{attacker}扎馬沉肩，雙掌平推。"]
      strike: ["掌勁如山洪傾瀉，震得{defender}胸骨發麻。"]
      afterglow: ["勁道未歇，掌風仍在場中迴盪。"]
    effects:
      damage: {base: 140, scaling: {innerPower: 0.8, strength: 0.6}}
      statusesApplied:
        - {id: "armor_break", chance: 0.3, durationTicks: 8}
      gaugeMod: {multiplier: 0.92}
  - id: "mantis_wrap"
    name: "螳螂纏腕"
    weaponFamily: "拳掌"
    tier: "specialization"
    tags: ["yin", "soft", "counter"]
    speedBias: 0.85
    cost: {qi: 20, stamina: 18}
    template:
      setup: ["{attacker}雙臂盤旋，手勢如蟲臂。"]
      strike: ["忽而貼身纏住{defender}手臂，借勢反摔。"]
      afterglow: ["{defender}身形一滯，經脈被封。"]
    effects:
      damage: {base: 90, scaling: {technique: 1.1}}
      statusesApplied:
        - {id: "root", chance: 0.45, durationTicks: 5}
      counterWindow: {ticks: 6, bonusCR: 25}
  - id: "xianglong_combo"
    name: "降龍十八掌"
    weaponFamily: "拳掌"
    tier: "ultimate"
    tags: ["yang", "hard", "finisher"]
    cooldownGauge: 2500
    cost: {qi: 60, stamina: 45}
    template:
      setup: ["{attacker}怒吼一聲，真氣化龍。"]
      strike: ["十八掌如狂風暴雨般連綿不絕，掌影層疊。"]
      afterglow: ["{defender}被震得氣血倒流，胸口陣陣作痛。"]
    effects:
      damage: {base: 420, scaling: {innerPower: 1.6, strength: 0.9}}
      statusesApplied:
        - {id: "stagger", chance: 0.6, durationTicks: 10}
      special:
        comboRequirement: 2
        overflowDamage: 0.25
```

## Designer Workflow
1. Choose weapon family and determine role (starter, control, finisher).
2. Assign tier and define unlock requirements.
3. Write template lines with placeholders; ensure at least two variations per segment for freshness.
4. Configure mechanical effects and synergy tags.
5. Playtest via gauge simulator; adjust `speedBias`, damage scaling, and counter windows.

## Future Enhancements
- Introduce dual-weapon combos (e.g., 劍＋鞭) using combined templates.
- Add lineage bonuses: mastering three moves within a lineage unlocks a passive buff.
- Support localization metadata (tone indicators, voiceover cues).
