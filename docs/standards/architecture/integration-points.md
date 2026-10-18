---
type: standard
title: Dashboard ↔ project protocol
description: The four control files (command, status, input, response) through which the dashboard drives a running automation and answers the questions it asks the operator
resource: "apps/automacao/utils.py, projetos/*/rpa/utils/controller.py"
tags: [architecture, ipc, rpa]
timestamp: 2026-10-17
audience: both
authority: current
source: repository code
maintainer: Israel Holetz
---

# Dashboard ↔ project protocol

The dashboard and an automation exchange messages through text files in the project folder,
`projetos/<id>/socket_<name>` (`get_projeto_socket` in `apps/automacao/utils.py`;
`projetos/desenvolvimento/rpa/utils/controller.py:26-43`).

| File | Written by | Values |
| --- | --- | --- |
| `socket_command` | dashboard | `Pausar` (pause), `Parar` (stop), `Continuar` (resume); the automation clears it after reading |
| `socket_status` | automation | `Iniciando`, `Executando`, `Pausado`, `Input` |
| `socket_input` | automation | JSON `{title, question, image?, options?}` — a question for the operator |
| `socket_response` | dashboard | JSON with the operator's answer |

The values are Portuguese literals in the code and must be matched exactly.

## Cycle

1. The automation calls `Controller.yield_command()` between queue items; that is where it
   pauses, resumes or stops (`controller.py:45-69`).
2. `Controller.get_next_queue()` returns the next `Pendente` record of the latest load plus
   the attachments matching its `arquivos` column (`controller.py:76-97`).
3. `Controller.get_input()` writes the question to `socket_input`, sets status `Input` and
   waits until the dashboard empties the file and writes the answer (`controller.py:99-135`).
4. Each record ends with `results_status` `Concluído` (done) or `Erro` (error), plus
   `results_error`/`results_stacktrace` (`projetos/desenvolvimento/main.py`).

The `socket_*` files are runtime state and are not versioned.
