"""Command line entry point for running the sample duel."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..combat.engine import BattleSimulator
from ..combat.loader import load_combatants, load_moves


def run_simulation(moves_path: Path, duel_path: Path, max_ticks: int, max_actions: int) -> None:
    moves = load_moves(moves_path)
    combatants = load_combatants(duel_path)
    simulator = BattleSimulator(combatants, moves)
    result = simulator.run(max_ticks=max_ticks, max_actions=max_actions)
    for entry in result.log:
        if entry.target:
            print(f"[{entry.timestamp:5.2f}] {entry.actor} -> {entry.target} | {entry.event}: {entry.text}")
        else:
            print(f"[{entry.timestamp:5.2f}] {entry.actor} | {entry.event}: {entry.text}")
    if result.winner:
        print(f"\n勝者：{result.winner}")
    else:
        print("\n戰鬥在時限內未分勝負。")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CODEX Wuxia combat prototype duel")
    parser.add_argument(
        "--moves",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "moves.yaml",
        help="Path to the move definitions file.",
    )
    parser.add_argument(
        "--duel",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "sample_duel.yaml",
        help="Path to the duel combatant configuration.",
    )
    parser.add_argument("--ticks", type=int, default=48, help="Maximum simulation ticks to execute.")
    parser.add_argument("--actions", type=int, default=32, help="Maximum actions before stopping the duel.")
    args = parser.parse_args()
    run_simulation(args.moves, args.duel, args.ticks, args.actions)


if __name__ == "__main__":
    main()
