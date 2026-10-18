# Guion

A web dashboard to run and supervise RPA (robotic process automation) projects. Upload a
spreadsheet, and Guion turns it into a queue, runs the matching Selenium automation as a background
process, and lets an operator pause it, resume it, answer the questions it asks, and download a
report of each record's outcome.

Built with Flask, SQLAlchemy, Selenium and the AdminLTE dashboard template.

> The UI and parts of the code use Portuguese names (`projetos`, `carga`, `Pendente`). The
> documentation is in English and explains them; see the [glossary](docs/glossary.md).

## Features

- **Projects by convention:** every folder under `projetos/` with a `project.json` becomes an
  automation the dashboard can run.
- **Loads and queues:** `.xlsx` (or `.zip` with attachments) uploads become a per-project queue
  table; each record ends as done or error, with its stack trace.
- **Live control:** start, pause, resume and stop a running automation; read its logs.
- **Operator input:** an automation can stop and ask a question (with an optional image or a list
  of options) and continue with the answer.
- **Per-project access and credentials:** users see only the projects they are granted;
  target-system credentials are stored in the database, not in code.

## Quick start

```bash
cp .env.example .env      # set SECRET_KEY and the DB_* variables
uv sync
uv run flask run
```

PostgreSQL is required for the full automation flow. Follow
[Getting started](docs/tutorials/getting-started.md) for the complete walkthrough with the
example project.

## Documentation

- [Getting started](docs/tutorials/getting-started.md)
- [Create an automation project](docs/how-to/create-project.md)
- [Deploy with nginx and gunicorn](docs/how-to/deploy.md)
- [Configuration](docs/project/configuration.md)
- [Architecture](docs/standards/architecture/layers.md) and the
  [dashboard ↔ project protocol](docs/standards/architecture/integration-points.md)

## Repository layout

| Path | Contents |
| --- | --- |
| `apps/` | Flask dashboard: authentication, pages, automation control |
| `projetos/` | Automation projects; `desenvolvimento/` is the reference example |
| `docs/` | Documentation (OKF knowledge bundle) |
| `nginx/`, `gunicorn.conf.py`, `autorun.sh` | Deployment |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [SUPPORT.md](SUPPORT.md) and the
[code of conduct](CODE_OF_CONDUCT.md). Report vulnerabilities as described in
[SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) © 2026 Israel Holetz.

The dashboard is based on the AppSeed Flask AdminLTE starter (MIT, © 2019 AppSeed.us) and ships
[AdminLTE](https://adminlte.io) (MIT) and the third-party front-end plugins under
`apps/static/assets/plugins/`, each under its own license.
