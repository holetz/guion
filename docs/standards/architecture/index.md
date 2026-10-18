# `standards/architecture/`

System structure (layers, modules, boundaries) and the current/active **architectural
patterns**. **`patterns` lives here** — there is no `/docs/patterns/`; a design pattern is
a doc in this home.

**Boundary:** the shape of the system (the structural *why*). An agreed-but-unproven architectural
rule sits here as `authority: background` (its history lives in `decisions/`). One standard per file
(files, not sub-folders); each carries `type: standard` + a derived `resource:`; add each to
[../index.md](../index.md).

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`layers` · `module-boundaries` · `patterns` · `dependency-direction` · `integration-points`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- [layers.md](layers.md) — dashboard, projects and database, and what each imports (present).
- [integration-points.md](integration-points.md) — dashboard ↔ project control-file protocol (present).
- `module-boundaries` — covered by layers.md; there are no further internal modules to split (deferred).
- `dependency-direction` — covered by layers.md (the dashboard only imports `model.py`) (deferred).
- `patterns` — no recurring pattern besides page objects under `rpa/pages`, not yet normative (deferred).

## Current docs

* [layers.md](layers.md) — Guion's three layers and what each one may import
* [integration-points.md](integration-points.md) — The four control files between dashboard and automation
