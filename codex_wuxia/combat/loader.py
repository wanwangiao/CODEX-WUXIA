"""Helpers for loading prototype data files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

from .model import (
    CombatantDefinition,
    CounterPrepSpec,
    DamageProfile,
    MoveDefinition,
    MoveEffects,
    ScriptEntry,
    StatusApplication,
)

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback to json
    yaml = None


def _load_raw(path: Path) -> Iterable[dict]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if isinstance(data, dict):
        return [data]
    return data


def load_moves(path: Path) -> Dict[str, MoveDefinition]:
    """Load move definitions from a YAML/JSON file."""

    moves: Dict[str, MoveDefinition] = {}
    for raw in _load_raw(path):
        effects = raw.get("effects", {})
        statuses = [
            StatusApplication(
                id=entry["id"],
                duration_ticks=int(entry.get("durationTicks", entry.get("duration_ticks", 0))),
                chance=float(entry.get("chance", 1.0)),
                magnitude=entry.get("magnitude"),
            )
            for entry in effects.get("statusesApplied", [])
        ]
        damage_cfg = effects.get("damage")
        damage = DamageProfile(base=int(damage_cfg["base"])) if damage_cfg else None
        counter_cfg = raw.get("counterPrep")
        counter = None
        if counter_cfg:
            status_cfg = counter_cfg.get("applyStatusOnTarget")
            counter_status = (
                StatusApplication(
                    id=status_cfg["id"],
                    duration_ticks=int(status_cfg.get("durationTicks", 0)),
                    chance=float(status_cfg.get("chance", 1.0)),
                    magnitude=status_cfg.get("magnitude"),
                )
                if status_cfg
                else None
            )
            counter = CounterPrepSpec(
                rating=float(counter_cfg.get("rating", 0.0)),
                window_ticks=int(counter_cfg.get("windowTicks", 0)),
                success_narration=list(counter_cfg.get("successNarration", [])),
                failure_narration=list(counter_cfg.get("failureNarration", [])),
                damage=DamageProfile(base=int(counter_cfg["damage"]["base"]))
                if counter_cfg.get("damage")
                else None,
                gauge_reward=float(counter_cfg.get("gaugeReward", 0.0)),
                fail_gauge_bonus=float(counter_cfg.get("failGaugeBonus", 0.0)),
                apply_status_on_target=counter_status,
            )
        move = MoveDefinition(
            id=raw["id"],
            name=raw["name"],
            weapon_family=raw.get("weaponFamily", raw.get("weapon_family", "")),
            tier=raw.get("tier", "foundation"),
            tags=list(raw.get("tags", [])),
            speed_bias=float(raw.get("speedBias", 1.0)),
            momentum=float(raw.get("momentum", 0.0)),
            cooldown=int(raw.get("cooldown", 0)),
            template={k: list(v) for k, v in raw.get("template", {}).items()},
            effects=MoveEffects(damage=damage, statuses_applied=statuses),
            kind=raw.get("kind", "attack"),
            counter_prep=counter,
        )
        moves[move.id] = move
    return moves


def load_combatants(path: Path) -> List[CombatantDefinition]:
    """Load combatant definitions used for the sample duel."""

    roster: List[CombatantDefinition] = []
    for raw in _load_raw(path):
        script_entries = [
            ScriptEntry(
                move_id=entry["move"],
                requires_status_absent=entry.get("requiresStatusAbsent"),
                requires_status_present=entry.get("requiresStatusPresent"),
                requires_enemy_status_absent=entry.get("requiresEnemyStatusAbsent"),
                requires_enemy_status_present=entry.get("requiresEnemyStatusPresent"),
            )
            for entry in raw.get("script", [])
        ]
        roster.append(
            CombatantDefinition(
                name=raw["name"],
                max_hp=int(raw.get("maxHP", raw.get("max_hp", 0))),
                base_speed=float(raw.get("baseSpeed", raw.get("base_speed", 0))),
                counter_rating=float(raw.get("counterRating", raw.get("counter_rating", 0))),
                script=script_entries,
            )
        )
    return roster
