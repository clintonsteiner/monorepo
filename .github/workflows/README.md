# GitHub Actions Workflows

This repo keeps CI in small, reusable pieces instead of one large workflow with mixed responsibilities.

## Workflow layout

### `ci.yml`

Runs on pull requests, key branch pushes, and manual dispatch.

Jobs:

- `validate`: BUILD hygiene plus lint and formatting checks
- `unit-tests`: non-Docker Pants tests
- `package`: shared Pants packaging for Python, Go, and Docker artifacts
- `docker-integration`: Docker image build plus Docker-tagged tests
- `summary`: one final status gate with a compact job summary

This keeps fast feedback separate from slower packaging work while still making the final required status easy to understand.

### `release.yml`

Runs on version tags like `v1.2.3` or manual dispatch.

Responsibilities:

- re-run repo validation before publishing
- build every release artifact through `pants package ::`
- build Docker images
- push Docker images to GHCR for tagged releases
- create a GitHub release and attach packaged artifacts for tagged releases
- upload a preview artifact set for manual runs

### `pages.yml`

Runs on pushes to `master` that change the static site, docs, root README, or the Pages workflow itself, and also supports manual dispatch.

Responsibilities:

- package the static content under `site/`
- upload the artifact using the official Pages actions
- deploy to the `github-pages` environment

## Reusable pieces

### `.github/actions/setup-pants`

Shared composite action used by both workflows.

It installs Python and initializes Pants with a single cache configuration, which keeps the workflows easy to extend without copy-pasting the bootstrap block everywhere.

The action also pins `PANTS_BUILDROOT` and `PANTS_TOML` to `github.workspace`, and `XDG_CACHE_HOME`, `SCIE_BASE`, and `PANTS_GLOBAL_CACHE_DIR` to `runner.temp`. That avoids two common bootstrap failures under local Actions emulators and some containerized runners: inherited host-local Pants config paths that do not exist inside the job, and read-only cache paths under `HOME` or the workspace.

### Tagged test split

Docker integration tests are tagged in [`tests/BUILD`](/Users/cs/git/monorepo/tests/BUILD), so CI can run:

- `pants --tag='-docker' test ::` for fast unit coverage
- `pants --tag='docker' test ::` for image-backed integration coverage

## Operating model

- Pull requests should rely on `ci.yml`.
- Releases should be created by pushing a version tag such as `v0.2.0`.
- Manual `workflow_dispatch` is kept for previewing artifacts or rerunning a release build without creating a tag first.
