# Security policy

## Reporting a vulnerability

Do not open a public issue. Report it privately through GitHub's
[security advisories](https://github.com/holetz/guion/security/advisories/new) for this
repository. You will get an acknowledgement as soon as the maintainer can review it; fixes are made
on a best-effort basis.

## Supported versions

Only the latest commit on the default branch receives fixes.

## Known limitations

Read these before running Guion anywhere reachable from an untrusted network:

- **Target-system credentials are stored in plain text** in the `Keychain` table. Protect the
  database accordingly.
- **Self-registration is open:** anyone who can reach `/register` can create an account. Project
  access is still limited by the `Permissions` table, but restrict network access or disable the
  route in production.
- **Some internal queries are built with string formatting** using project ids (folder names) and
  load ids; do not create project folders from untrusted input.
- **Run behind HTTPS** (see [the deploy guide](docs/how-to/deploy.md)) and set your own
  `SECRET_KEY`.
