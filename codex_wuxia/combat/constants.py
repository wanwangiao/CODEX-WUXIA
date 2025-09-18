"""Configuration constants for the combat prototype."""

from __future__ import annotations

# Simulation pacing
TICK_DURATION: float = 0.25  # seconds per tick
ACTION_THRESHOLD: float = 1000.0
COUNTER_THRESHOLD: float = 600.0
COUNTER_PREP_THRESHOLD: float = 400.0
SPEED_SOFT_CAP: float = 900.0

# Status tuning
SLOW_MULTIPLIER: float = 0.8
STAGGER_THRESHOLD_MULTIPLIER: float = 1.15

# Randomness helpers
DEFAULT_RANDOM_SEED: int = 42
