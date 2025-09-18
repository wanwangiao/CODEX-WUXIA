"""Runtime combatant logic for the prototype simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from . import constants
from .model import CombatantDefinition, MoveDefinition, ScriptEntry, StatusApplication, StatusState


@dataclass
class Combatant:
    """Represents a combatant in an ongoing battle."""

    definition: CombatantDefinition
    moves: Dict[str, MoveDefinition]
    hp: int = field(init=False)
    gauge: float = field(default=0.0, init=False)
    statuses: Dict[str, StatusState] = field(default_factory=dict, init=False)
    cooldowns: Dict[str, int] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.hp = self.definition.max_hp
        self.cooldowns = {move_id: 0 for move_id in self.moves}

    @property
    def name(self) -> str:
        return self.definition.name

    def action_threshold(self) -> float:
        threshold = constants.ACTION_THRESHOLD
        stagger = self.statuses.get("stagger")
        if stagger is not None:
            threshold *= constants.STAGGER_THRESHOLD_MULTIPLIER
        return threshold

    def gauge_multiplier(self) -> float:
        multiplier = 1.0
        slow = self.statuses.get("slow")
        if slow is not None:
            multiplier *= slow.magnitude or constants.SLOW_MULTIPLIER
        return multiplier

    def effective_speed(self) -> float:
        base = self.definition.base_speed
        if base <= constants.SPEED_SOFT_CAP:
            return base
        overflow = base - constants.SPEED_SOFT_CAP
        return constants.SPEED_SOFT_CAP + overflow * 0.35

    def compute_gauge_increment(self) -> float:
        return self.effective_speed() * constants.TICK_DURATION * self.gauge_multiplier()

    def tick(self) -> None:
        """Advance cooldowns and status durations by one tick."""

        for move_id in list(self.cooldowns.keys()):
            if self.cooldowns[move_id] > 0:
                self.cooldowns[move_id] -= 1
        for status_id in list(self.statuses.keys()):
            status = self.statuses[status_id]
            status.remaining_ticks -= 1
            if status.remaining_ticks <= 0:
                del self.statuses[status_id]

    def can_act(self) -> bool:
        if self.has_status("counter_prepped"):
            return False
        return self.gauge >= self.action_threshold()

    def has_status(self, status_id: str) -> bool:
        return status_id in self.statuses

    def add_status(self, application: StatusApplication, payload: Optional[dict] = None) -> None:
        existing = self.statuses.get(application.id)
        if payload is None and existing is not None:
            payload = existing.payload
        elif payload is None:
            payload = {}
        self.statuses[application.id] = StatusState(
            id=application.id,
            remaining_ticks=application.duration_ticks,
            magnitude=application.magnitude,
            payload=payload,
        )

    def remove_status(self, status_id: str) -> None:
        self.statuses.pop(status_id, None)

    def set_cooldown(self, move_id: str, value: int) -> None:
        self.cooldowns[move_id] = max(value, 0)

    def reduce_gauge(self, spent: float, move: MoveDefinition) -> None:
        self.gauge = max(0.0, (self.gauge - spent) * move.speed_bias)

    def choose_move(self, opponent: "Combatant") -> MoveDefinition:
        """Select a move based on scripted priorities."""

        for entry in self.definition.script:
            if not self.entry_allows(entry, opponent):
                continue
            move = self.moves.get(entry.move_id)
            if move is None:
                continue
            if self.cooldowns.get(move.id, 0) > 0:
                continue
            if move.kind == "counter_prep" and self.has_status("counter_prepped"):
                continue
            return move
        # fallback to the first move defined for the combatant
        for move in self.moves.values():
            if self.cooldowns.get(move.id, 0) > 0:
                continue
            if move.kind == "counter_prep" and self.has_status("counter_prepped"):
                continue
            entry = self._entry_for_move(move.id)
            if entry and not self.entry_allows(entry, opponent):
                continue
            return move
        return next(iter(self.moves.values()))

    def entry_allows(self, entry: ScriptEntry, opponent: "Combatant") -> bool:
        if entry.requires_status_absent and self.has_status(entry.requires_status_absent):
            return False
        if entry.requires_status_present and not self.has_status(entry.requires_status_present):
            return False
        if entry.requires_enemy_status_absent and opponent.has_status(entry.requires_enemy_status_absent):
            return False
        if entry.requires_enemy_status_present and not opponent.has_status(entry.requires_enemy_status_present):
            return False
        return True

    def _entry_for_move(self, move_id: str) -> Optional[ScriptEntry]:
        for entry in self.definition.script:
            if entry.move_id == move_id:
                return entry
        return None

    def apply_damage(self, amount: float) -> float:
        self.hp = max(0, int(self.hp - amount))
        return amount

    def get_counter_status(self) -> Optional[StatusState]:
        status = self.statuses.get("counter_prepped")
        if status and status.remaining_ticks > 0:
            return status
        return None
