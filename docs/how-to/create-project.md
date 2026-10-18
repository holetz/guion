---
type: how-to
title: Create an automation project
description: How to create a new folder under projetos/ that the dashboard discovers, queues and runs
resource: "projetos/**"
tags: [rpa, projects]
timestamp: 2026-10-17
audience: both
authority: current
source: repository code
maintainer: Israel Holetz
---

# Create an automation project

1. Copy the example: `cp -r projetos/desenvolvimento projetos/my_project`. The folder name is
   the project id and the name of its queue table.
2. Edit `project.json` (`name`, `sector`, `system`, `description`, `rev_date`,
   `enabled`).
3. In `model.py`, declare the load columns on `Queue` and set `__template_type__`
   (`.xlsx`, or `.zip` with an `arquivos/` folder). Override `projeto_transformer` if the
   spreadsheet needs preprocessing.
4. Replace `template.*` with a template that contains **no real data**.
5. Write the loop in `main.py` with `Controller`: `yield_command()`, `get_next_queue()`,
   `get_input()` — see the [protocol](/docs/standards/architecture/integration-points.md).
6. Page objects for target systems go in `rpa/pages/custom/<system>/`, inheriting from
   `rpa/pages/base`.
7. Restart the dashboard (tables are created at boot) and grant the user access in the
   `Permissions` table.

Target-system credentials live in the `Keychain` table and are read with
`Keychain.get_credentials` — never in code or in the repository.
