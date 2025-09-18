"""Data models for the combat simulator prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StatusApplication:
    """Defines how a status is applied to a target."""

    id: str
    duration_ticks: int
    chance: float = 1.0
    magnitude: Optional[float] = None


@dataclass
class DamageProfile:
    """Simplified damage profile used by the prototype."""

    base: int


@dataclass
class CounterPrepSpec:
    """Parameters for preparing a counter stance."""

    rating: float
    window_ticks: int
    success_narration: List[str]
    failure_narration: List[str] = field(default_factory=list)
    damage: Optional[DamageProfile] = None
    gauge_reward: float = 0.0
    fail_gauge_bonus: float = 0.0
    apply_status_on_target: Optional[StatusApplication] = None


@dataclass
class MoveEffects:
    """Container for secondary effects triggered by a move."""

    damage: Optional[DamageProfile] = None
    statuses_applied: List[StatusApplication] = field(default_factory=list)


@dataclass
class MoveDefinition:
    """Metadata describing an executable move."""

    id: str
    name: str
    weapon_family: str
    tier: str
    tags: List[str]
    speed_bias: float
    momentum: float
    cooldown: int
    template: Dict[str, List[str]]
    effects: MoveEffects
    kind: str = "attack"
    counter_prep: Optional[CounterPrepSpec] = None


@dataclass
class ScriptEntry:
    """Represents a single behaviour rule within an AI script."""

    move_id: str
    requires_status_absent: Optional[str] = None
    requires_status_present: Optional[str] = None
    requires_enemy_status_absent: Optional[str] = None
    requires_enemy_status_present: Optional[str] = None


@dataclass
class CombatantDefinition:
    """Static configuration for a combatant in the prototype."""

    name: str
    max_hp: int
    base_speed: float
    counter_rating: float
    script: List[ScriptEntry]


@dataclass
class StatusState:
    """Runtime representation of an active status effect."""

    id: str
    remaining_ticks: int
    magnitude: Optional[float] = None
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BattleLogEntry:
    """Structured log entry emitted by the simulator."""

    timestamp: float
    actor: str
    target: Optional[str]
    event: str
    text: str
    animation: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
