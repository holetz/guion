---
type: project
title: Documentation site
description: Building the documentation site from /docs/ with zensical
resource: "zensical.toml"
tags: [docs, tooling]
timestamp: 2026-11-03
audience: both
authority: current
source: zensical.toml
maintainer: Israel Holetz
---

# Documentation site

The site is built from the `/docs/` bundle by [zensical](https://zensical.org), configured in
`zensical.toml` at the repository root. zensical is in the `dev` dependency group, so `uv sync`
installs it.

```bash
uv run zensical build   # writes the static site to site/ (git-ignored)
uv run zensical serve   # serves it locally with live reload
```
