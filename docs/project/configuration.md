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
| `SECRET_KEY` | random per boot | Signs sessions; without it, logins are dropped on every restart |
| `ASSETS_ROOT` | `/static/assets` | Root of static assets |
| `DB_ENGINE`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASS` | — | Relational database; without `DB_ENGINE`/`DB_NAME`/`DB_USERNAME` it uses SQLite at `apps/db.sqlite3` |
| `GECKODRIVER_PATH` | — | Path to geckodriver for Selenium automations |
