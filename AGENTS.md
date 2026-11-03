# AGENTS.md

This repository uses quenching. The editable automation surface is `.agents/`; the
Claude Code bridge under `.claude/skills/` is generated from it.

- Configuration: [`.agents/quenching.json`](.agents/quenching.json).
- Durable knowledge: [`docs/index.md`](docs/index.md).
- Skills: `.agents/skills/` (source) and `.claude/skills/` (generated bridge).
- Deployed runtime: `.agents/quenching/` (generated; do not edit).
- Upgrade with `cq deploy --write` from a new quenching release; never edit a generated file.
