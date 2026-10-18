---
type: standard
title: System layers
description: Guion's three layers — the Flask dashboard, automation projects run as child processes, and the shared database — and what each one may import
resource: "apps/**, projetos/**, run.py"
tags: [architecture, flask, rpa]
timestamp: 2026-10-17
audience: both
authority: current
source: repository code
maintainer: Israel Holetz
---

# System layers

Guion has three layers. The rule is that **the dashboard never imports a project's automation
code**, only its `model.py`; the automation runs isolated in another process.

| Layer | Where | Role |
| --- | --- | --- |
| Dashboard | `apps/` | Flask app with three blueprints — `authentication`, `home`, `automacao` (`apps/__init__.py:19-22`) |
| Projects | `projetos/<id>/` | Each folder is an independent automation with `main.py`, `model.py`, `project.json` and `template.*` |
| Database | PostgreSQL (SQLite for the dashboard only) | Users, `Permissions`, `Cargas`, `Keychain` (`apps/automacao/models.py`) and one queue table per project |

## Rules

- **Discovery by convention.** On startup the dashboard registers every `projetos/*/model.py`
  into the SQLAlchemy metadata (`apps/__init__.py:24-27`). A project exists when it has a
  `project.json` with `"enabled": true` (`get_projeto_path` in `apps/automacao/utils.py`).
- **One table per project.** The queue inherits from `BaseQueue`, whose `__tablename__` is
  the project id, i.e. its folder name (`projetos/desenvolvimento/rpa/utils/models.py:14-24`).
- **Isolated execution.** The *start* command launches `python projetos/<id>/main.py` in a
  `multiprocessing.Process` (`set_projeto_command` in `apps/automacao/utils.py`). Dashboard
  and automation talk only through the database and the control files described in
  [integration-points.md](integration-points.md).
- **Repository root is resolved from the file's position**, never from the checkout folder name
  (`apps/automacao/utils.py:28`, `projetos/desenvolvimento/rpa/utils/projeto.py:9`).
