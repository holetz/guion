# `how-to/` — task recipes

Task-oriented pages that answer "how do I do X" for someone using the product (the Diátaxis
**how-to** quadrant). This section absorbs the former `guides/` home. Each page carries
`type: how-to`.

**Boundary:** a how-to gets a known task done for a user who already knows the basics; a
guided first lesson is a [tutorial](../tutorials/index.md); the current internal *rule*
for how WE build is a `standard` in the `standards/` home, not a how-to.

## How to organize

The repo decides which recipes exist — the skeleton ships none. Standalone pages live as
`.md` files here; group a coherent set into a subfolder with its own `index.md`. One concept
per file, kebab-case English slug.

## Pages

* [create-project.md](create-project.md) — How to create a new folder under projetos/ that the dashboard discovers, queues and runs
* [deploy.md](deploy.md) — Deploying on a Linux server with gunicorn behind nginx as a reverse proxy
