# AGENTS.md — guion

Web dashboard (Flask + SQLAlchemy + Selenium) that runs and supervises RPA automation projects.

## Operating this repo

```bash
cp .env.example .env      # set SECRET_KEY and the DB_* variables
uv sync
uv run flask run
```

- PostgreSQL is required for the full automation flow; the complete walkthrough is
  [Getting started](docs/tutorials/getting-started.md).
- Upgrade the quenching surface with `cq deploy --write` from a new quenching release;
  `.agents/quenching/` and `.claude/skills/` are generated — never edit a generated file.
  Configuration: [`.agents/quenching.json`](.agents/quenching.json).

## Where knowledge lives

Knowledge is **NOT** in this file — it lives in the OKF bundle at [/docs/](docs/index.md).

**Resolving a term.** Hit an unfamiliar repo word, acronym, or codename? Look it up in the
**glossary first** → [/docs/glossary.md](docs/glossary.md): the A–Z lookup,
one entry per term with a link to its full doc when one exists. `grep -i '<term>' docs/glossary.md`.

- [/docs/standards/](docs/standards/index.md) — how WE build (current, proven contracts).
- [/docs/concepts/](docs/concepts/index.md) — generic understanding we hold (concepts, learnings);
  its [glossary.md](docs/glossary.md) is the term lookup.
- [/docs/tutorials/](docs/tutorials/index.md) — learning-oriented pages ("get it running").
- [/docs/how-to/](docs/how-to/index.md) — task-oriented recipes for a reader with a goal.
- [/docs/explanation/](docs/explanation/index.md) — how and why, for the site's reader.
- [/docs/project/](docs/project/index.md) — the manual for this repository: commands, configuration, layout.

<!-- HOW TO FIND A TERM: the glossary is the repo's A–Z vocabulary index at
     /docs/glossary.md — a flat, alphabetically sorted bullet list (the same syntax
     every index.md uses), linked when a concept doc exists. To resolve a word: `grep -i
     '<term>' /docs/glossary.md` (or Ctrl-F it). A matching entry gives the local
     meaning and, when linked, its full concept doc; no entry means the term is not yet
     defined — add it with the `quenching-knowledge-define` skill (one term), backfill many at once
     with `quenching-knowledge-glossary-backfill`, or capture the concept with `quenching-knowledge-learn` (which
     enters the term as its tail step). -->

To **create / edit / move** knowledge (keeping the listing in sync), use the
`quenching` skills: `quenching-knowledge-add` to add one, `quenching-knowledge-define` to add a glossary
term, `quenching-knowledge-align` to migrate/normalize, `quenching-components-harness-align` to keep this file thin.

## Agent etiquette

- **Artifacts are written in English** —
  [/docs/standards/agents/artifact-language.md](docs/standards/agents/artifact-language.md).
- **Every development request goes through a spec**, and the spec runs the flow as far as the
  request authorizes. A request that names a change — "implement X improvement", "fix Y" — is a
  request to build it: develop, execute, conclude, open the PR, without stopping to ask whether to.
  Only a request that names the artifact — "create a spec for X" — stops at the spec. **Merge and
  deploy are not implied by a change request**: they run only when the human declares autonomy in
  the request itself ("do it autonomously", "PR and merge", "all the way to deploy"). Without that
  word the run ends at the open PR, named for the human to decide. The approval a spec carries
  covers every step inside that scope — no later step asks the human again.
- **A new skill joins its family's router** (`.agents/skills/<family>/SKILL.md`) when the family has
  three or more model-invocable skills — never a loose entry, and never an edit to an agent that
  came from the plugin (`.claude/agents/quenching-*.md`).

<!-- Root harness pointer, auto-loaded by every supported harness on every turn. Keep it a thin pointer:
     repo-wide operations + the /docs/ home map. Knowledge is MOVED into /docs/, never copied here.
     Installed/maintained by the quenching plugin; this file is a harness pointer, not an
     OKF concept. -->
