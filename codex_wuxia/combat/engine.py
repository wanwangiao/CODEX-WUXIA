"""Turn-based gauge simulator for the wuxia combat prototype."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

from . import constants
from .combatant import Combatant
from .model import BattleLogEntry, CombatantDefinition, MoveDefinition, StatusApplication


@dataclass
class BattleResult:
    """Summary of a simulated duel."""

    winner: Optional[str]
    loser: Optional[str]
    log: List[BattleLogEntry]


class BattleSimulator:
    """Simulates a duel using the action gauge rules from the specification."""

    def __init__(
        self,
        combatants: Sequence[CombatantDefinition],
        moves: Dict[str, MoveDefinition],
        seed: int = constants.DEFAULT_RANDOM_SEED,
    ) -> None:
        if len(combatants) != 2:
            raise ValueError("Prototype simulator currently supports exactly two combatants.")
        self.rng = random.Random(seed)
        self.moves = {move_id: moves[move_id] for move_id in moves}
        self.combatants: List[Combatant] = [
            Combatant(combatant, {move_id: moves[move_id] for move_id in self._script_move_ids(combatant)})
            for combatant in combatants
        ]
        self.log: List[BattleLogEntry] = []

    def _script_move_ids(self, definition: CombatantDefinition) -> Iterable[str]:
        ids = [entry.move_id for entry in definition.script if entry.move_id in self.moves]
        if not ids:
            ids = list(self.moves.keys())
        return ids

    def run(self, max_ticks: int = 120, max_actions: int = 100) -> BattleResult:
        actions = 0
        for tick in range(max_ticks):
            timestamp = tick * constants.TICK_DURATION
            for combatant in self.combatants:
                combatant.tick()
            for combatant in self.combatants:
                increment = combatant.compute_gauge_increment()
                combatant.gauge += increment
                self.log.append(
                    BattleLogEntry(
                        timestamp=timestamp,
                        actor=combatant.name,
                        target=None,
                        event="gauge_advance",
                        text=f"{combatant.name} 的行動槽增加 {increment:.1f}，目前 {combatant.gauge:.1f}/{combatant.action_threshold():.0f}。",
                    )
                )
            self._auto_prepare_counters(timestamp)
            while actions < max_actions and any(c.can_act() for c in self.combatants):
                actor = self._select_actor()
                target = self._other(actor)
                self._resolve_action(actor, target, timestamp)
                actions += 1
                if target.hp <= 0 or actor.hp <= 0:
                    winner = actor.name if actor.hp > 0 else target.name
                    loser = target.name if winner == actor.name else actor.name
                    self.log.append(
                        BattleLogEntry(
                            timestamp=timestamp,
                            actor=winner,
                            target=loser,
                            event="victory",
                            text=f"{winner} 取得勝利，{loser} 無力再戰。",
                        )
                    )
                    return BattleResult(winner=winner, loser=loser, log=self.log)
            if actions >= max_actions:
                break
        return BattleResult(winner=None, loser=None, log=self.log)

    def _select_actor(self) -> Combatant:
        ready = [c for c in self.combatants if c.can_act()]
        ready.sort(key=lambda c: (-c.gauge, c.name))
        return ready[0]

    def _other(self, actor: Combatant) -> Combatant:
        for combatant in self.combatants:
            if combatant is not actor:
                return combatant
        raise RuntimeError("Opponent not found")

    def _resolve_action(self, actor: Combatant, target: Combatant, timestamp: float) -> None:
        move = actor.choose_move(target)
        if move.kind == "counter_prep":
            self._resolve_counter_prep(actor, move, timestamp)
        else:
            self._resolve_attack(actor, target, move, timestamp)

    def _resolve_counter_prep(self, actor: Combatant, move: MoveDefinition, timestamp: float, consume_gauge: bool = True) -> None:
        if consume_gauge:
            actor.reduce_gauge(actor.action_threshold(), move)
        else:
            actor.gauge *= move.speed_bias
        actor.set_cooldown(move.id, move.cooldown)
        if move.counter_prep:
            actor.add_status(
                StatusApplication(id="counter_prepped", duration_ticks=move.counter_prep.window_ticks),
                payload={
                    "spec": move.counter_prep,
                    "rating": move.counter_prep.rating + actor.definition.counter_rating,
                },
            )
        text = self._compose_text(move, actor.name, actor.name)
        self.log.append(
            BattleLogEntry(
                timestamp=timestamp,
                actor=actor.name,
                target=None,
                event="prepare_counter",
                text=text,
            )
        )

    def _auto_prepare_counters(self, timestamp: float) -> None:
        for combatant in self.combatants:
            if combatant.has_status("counter_prepped"):
                continue
            opponent = self._other(combatant)
            for entry in combatant.definition.script:
                move = combatant.moves.get(entry.move_id)
                if move is None or move.kind != "counter_prep":
                    continue
                if not combatant.entry_allows(entry, opponent):
                    continue
                if combatant.cooldowns.get(move.id, 0) > 0:
                    continue
                if combatant.gauge < constants.COUNTER_PREP_THRESHOLD:
                    continue
                self._resolve_counter_prep(combatant, move, timestamp, consume_gauge=False)
                break

    def _resolve_attack(self, actor: Combatant, target: Combatant, move: MoveDefinition, timestamp: float) -> None:
        # Check counter before applying damage
        if self._attempt_counter(actor, target, move, timestamp):
            actor.set_cooldown(move.id, move.cooldown)
            actor.gauge = 0.0
            return

        damage = 0.0
        if move.effects.damage:
            damage = move.effects.damage.base
        inflicted = target.apply_damage(damage)
        narration = self._compose_text(move, actor.name, target.name)
        self.log.append(
            BattleLogEntry(
                timestamp=timestamp,
                actor=actor.name,
                target=target.name,
                event="attack",
                text=narration,
                extra={"damage": inflicted},
            )
        )
        if move.effects.statuses_applied:
            for status in move.effects.statuses_applied:
                if self.rng.random() <= status.chance:
                    target.add_status(status)
                    self.log.append(
                        BattleLogEntry(
                            timestamp=timestamp,
                            actor=actor.name,
                            target=target.name,
                            event="status_applied",
                            text=f"{target.name} 受到 {status.id} 狀態 ({status.duration_ticks} ticks)。",
                        )
                    )
        actor.reduce_gauge(actor.action_threshold(), move)
        actor.set_cooldown(move.id, move.cooldown)

    def _attempt_counter(self, actor: Combatant, target: Combatant, move: MoveDefinition, timestamp: float) -> bool:
        status = target.get_counter_status()
        if status is None or target.gauge < constants.COUNTER_THRESHOLD:
            return False
        spec = status.payload.get("spec")
        if spec is None:
            return False
        counter_score = status.payload.get("rating", 0.0) + (target.gauge - actor.gauge) / 10.0
        attack_score = move.momentum
        if counter_score >= attack_score:
            text = self.rng.choice(spec.success_narration) if spec.success_narration else f"{target.name} 成功拆招。"
            self.log.append(
                BattleLogEntry(
                    timestamp=timestamp,
                    actor=target.name,
                    target=actor.name,
                    event="counter_success",
                    text=text,
                )
            )
            if spec.damage:
                damage = spec.damage.base
                dealt = actor.apply_damage(damage)
                self.log.append(
                    BattleLogEntry(
                        timestamp=timestamp,
                        actor=target.name,
                        target=actor.name,
                        event="counter_damage",
                        text=f"{actor.name} 遭受 {damage} 反震傷害。",
                        extra={"damage": dealt},
                    )
                )
            if spec.apply_status_on_target:
                actor.add_status(spec.apply_status_on_target)
                self.log.append(
                    BattleLogEntry(
                        timestamp=timestamp,
                        actor=target.name,
                        target=actor.name,
                        event="status_applied",
                        text=f"{actor.name} 陷入 {spec.apply_status_on_target.id}。",
                    )
                )
            actor.gauge = 0.0
            target.gauge += spec.gauge_reward
            target.remove_status("counter_prepped")
            return True
        else:
            if spec.failure_narration:
                text = self.rng.choice(spec.failure_narration)
                self.log.append(
                    BattleLogEntry(
                        timestamp=timestamp,
                        actor=target.name,
                        target=actor.name,
                        event="counter_fail",
                        text=text,
                    )
                )
            target.gauge += spec.fail_gauge_bonus
            target.remove_status("counter_prepped")
            return False

    def _compose_text(self, move: MoveDefinition, actor: str, target: str) -> str:
        setup = self._pick(move.template.get("setup"))
        strike = self._pick(move.template.get("strike"))
        afterglow = self._pick(move.template.get("afterglow"))
        segments = [segment for segment in [setup, strike, afterglow] if segment]
        text = " ".join(segments)
        return text.format(attacker=actor, defender=target, moveName=move.name)

    def _pick(self, options: Optional[List[str]]) -> Optional[str]:
        if not options:
            return None
        return self.rng.choice(options)
