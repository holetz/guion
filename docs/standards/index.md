# `standards/` — current/active reference, OUR contracts

The current/active **standard/contract** — "how it should be and why", versioned, the
shared source of truth. One standard per file; subfolder names by **subject**. Each
concept doc carries `type: standard` + a derived `resource:` (the repo scope it governs).

**Boundary:** `standards/` = "how **WE** do it (current/active)".  An **agreed-but-unproven** rule sits here as
`authority: background` and graduates to `current` once proven — there is no separate decisions
home.

Keep only the subtopics that apply to the repo; within each, break standards **one
concept per file** by considering the candidate sub-standards catalog (a
**consideration** checklist, evidence-gated generation, recorded deferral — not a blind
generate list). The **agent-facing pointer** for this home is [CLAUDE.md](CLAUDE.md)
(auto-loaded).

## Subtopics

* [agents/](agents/index.md) — how we instruct agents: the language our prose is written in, and the conduct expected of the agent writing it
* [architecture/](architecture/index.md) — system structure + architectural patterns (patterns live here)

## Current docs

<!-- BEGIN GENERATED: rebuilt from disk by `quenching-align:knowledge:align`/`quenching-align:knowledge:add` — DO NOT edit by hand.
     Scans standards/**/*.md, reads title/description/timestamp/type, grouped by subject subfolder.
     Row model per subfolder:
       ### code/
       | Doc | Covers |
       | --- | --- |
       | [imports.md](code/imports.md) | <the doc's description:> |
-->
### agents/

| Doc | Covers |
| --- | --- |
| [communication.md](agents/communication.md) | The two languages a repo declares for what its agents write — the conversation tag on the root harness line, and an artifact language declared by a standard or the artifactLanguage config key — and the conduct contract that holds whether or not either is declared |
| [ephemeral-writes.md](agents/ephemeral-writes.md) | Where an agent puts a file it creates — the three destinations, the one question that sorts them, and the session-start declaration that makes the durable-ignored path present before the first write |
| [artifact-language.md](agents/artifact-language.md) | Every durable artifact of this repository — doc bodies, README and community files, code comments, commit messages, PR bodies — is written in English, whatever language the conversation uses |

_(other subjects fill in as standards are created — these tables are regenerated deterministically from the real files)_

### architecture/

| Doc | Covers |
| --- | --- |
| [integration-points.md](architecture/integration-points.md) | The four control files (command, status, input, response) through which the dashboard drives a running automation and answers the questions it asks the operator |
| [layers.md](architecture/layers.md) | Guion's three layers — the Flask dashboard, automation projects run as child processes, and the shared database — and what each one may import |
<!-- END GENERATED -->
