---
type: tutorial
title: Getting started
description: From clone to a locally running dashboard with the example project processing a synthetic load
resource: "pyproject.toml, run.py, .env.example, projetos/desenvolvimento/**"
tags: [setup, uv, postgres]
timestamp: 2026-10-17
audience: human
authority: current
source: original readme + repository code
maintainer: Israel Holetz
---

# Getting started

## Prerequisites

- Python 3.10 and [uv](https://docs.astral.sh/uv/) (or `nix develop`, which provides uv,
  Chromium and chromedriver — `flake.nix`)
- PostgreSQL: automation queries use the `public` schema, so the full flow needs Postgres.
  Without `DB_*` the dashboard falls back to SQLite, which is only good for browsing the UI.
- Firefox + geckodriver for Selenium automations (set `GECKODRIVER_PATH` if it is not on PATH)

## 1. Database

```bash
sudo -u postgres createuser guion
sudo -u postgres psql -c "ALTER USER guion WITH PASSWORD 'change-me' CREATEDB;"
psql -U guion -d postgres -c "CREATE DATABASE guion;"
```

## 2. Configuration

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste into SECRET_KEY
```

Uncomment and fill in the `DB_*` variables (see [configuration](../project/configuration.md)).

## 3. Run

```bash
uv sync
uv run flask run          # or: uv run gunicorn run:app
```

Open the dashboard, create an account under *Registrar* (register) and sign in.

## 4. First load

1. Under *Projetos*, open **Example project**.
2. Download the template (`template.zip`, fictitious data) and upload it as a load.
3. Click *Iniciar* (start): the automation processes the three records, asks a question on the
   first iteration (answer it in the dashboard) and deliberately fails one record so you can
   see both outcomes.

Next: [create a project](../how-to/create-project.md).
