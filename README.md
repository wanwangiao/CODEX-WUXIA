# CODEX-WUXIA

Design assets and documentation for a text-driven idle wuxia RPG inspired by *九陰真經*.

## Documentation
- [High-level design overview](docs/design.md)
  - [Combat system specification](docs/combat_system.md)
  - [Combat core prototype outline](docs/combat_prototype.md)
- [Move system blueprint](docs/move_system.md)

## Prototype

The repository now ships with a lightweight Python prototype that replays a 1v1 duel using the documented action-gauge and拆招 rules.

```
python -m codex_wuxia.cli.simulate --ticks 32 --actions 24
```

The command prints a chronological battle log showing gauge growth, counter triggers, and resulting narration beats.

