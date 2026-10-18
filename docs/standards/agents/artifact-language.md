---
type: standard
title: Artifact language
description: Every durable artifact of this repository — doc bodies, README and community files, code comments, commit messages, PR bodies — is written in English, whatever language the conversation uses
resource: "/docs/**, CLAUDE.md, README.md, CONTRIBUTING.md, SECURITY.md, .env.example, .gitignore"
tags: [agents, language, open-source]
timestamp: 2026-10-17
audience: both
authority: current
source: project memory
maintainer: Israel Holetz
---

# Artifact language

**Artifact language: `en`.** This is the declaration that
[communication.md](communication.md#artifact-language) reads.

## Rule

- Write in English: concept-doc bodies (not only slugs and frontmatter), `README.md`, community
  and governance files, new code comments, configuration comments, commit messages and PR bodies.
- The conversation band is independent: an agent answers each person in the language they use.
- Existing Portuguese identifiers and UI strings in `apps/` and `projetos/` (e.g. `projetos`,
  `Carga`, status literals such as `Pendente`) are code, not prose; they stay as they are until a
  dedicated translation change renames them. Docs quote them verbatim and explain them in English.

## Why

Guion is published as open source, and English is the open-source default for reaching
contributors. The maintainer stated it directly when the repository was prepared for publication.

## How to apply

Before writing any file in this repository, write its prose in English. When touching an older
artifact that is still in Portuguese, translate the prose you change rather than extending it in
Portuguese.
