"""Smoke tests for the combat simulator prototype."""

from __future__ import annotations

import unittest
from pathlib import Path

from codex_wuxia.combat.engine import BattleSimulator
from codex_wuxia.combat.loader import load_combatants, load_moves


class BattleSimulatorTest(unittest.TestCase):
    """Ensure the sample duel wiring behaves as expected."""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.moves = load_moves(root / "codex_wuxia" / "data" / "moves.yaml")
        cls.combatants = load_combatants(root / "codex_wuxia" / "data" / "sample_duel.yaml")

    def test_counter_triggers_and_attacks(self) -> None:
        simulator = BattleSimulator(self.combatants, self.moves)
        result = simulator.run(max_ticks=32, max_actions=24)
        events = {entry.event for entry in result.log}
        self.assertIn("counter_success", events)
        self.assertIn("attack", events)


if __name__ == "__main__":
    unittest.main()
