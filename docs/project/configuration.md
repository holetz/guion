---
type: project
title: Configuration
description: Environment variables read by the dashboard and the automations
resource: "apps/config.py, run.py, .env.example"
tags: [config, env]
timestamp: 2026-10-17
audience: both
authority: current
source: apps/config.py
maintainer: Israel Holetz
---

# Configuration

Read from `.env` at the repository root (`python-dotenv`). Template: `.env.example`.

| Variable | Default | Effect |
| --- | --- | --- |
| `DEBUG` | `False` | `True` enables Flask debug mode, DEBUG logs and captured project output |
| `SECRET_KEY` | required in production | Signs sessions. With `DEBUG=False` the app refuses to start without it; with `DEBUG=True` a random per-process key is used and a warning is logged |
| `ASSETS_ROOT` | `/static/assets` | Root of static assets |
| `DB_ENGINE`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASS` | — | Relational database; without `DB_ENGINE`/`DB_NAME`/`DB_USERNAME` it uses SQLite at `apps/db.sqlite3` |
| `GECKODRIVER_PATH` | — | Path to geckodriver for Selenium automations |

## Dependencies

`pyproject.toml` is the single source of dependencies; `requirements.txt` is exported from `uv.lock`
(`uv export --format requirements-txt --no-hashes --frozen --no-emit-project --no-dev -o requirements.txt`).
The web stack runs on Flask 3.1. These packages were removed from the runtime dependencies because
no code in `apps/`, `projetos/` or `run.py` imports them: `flask-restx`, `thefuzz`, `unidecode`,
`webdriver_manager`, `seleniumbase`, `ipykernel`, `jupyterlab`. An automation project that needs one
must declare it itself. `pytest` and `zensical` live in the `dev` dependency group.
