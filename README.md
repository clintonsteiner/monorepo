# ercot-lmp-monitor monorepo

## Overview

This repo is a small Python monorepo built around [Pants](https://www.pantsbuild.org/). It combines a real ERCOT LMP monitoring app, shared libraries, infrastructure assets, and example projects without keeping every concern mixed at the repo root.

The root project uses Pants 2.30.0 for dependency inference, linting, formatting, testing, packaging, and Docker image builds. The repo is organized around a few stable buckets:

- `ercot_lmp/` and `lib_ercot/` for core application code
- `infra/` for deployable infrastructure assets
- `examples/` for sample packages and binaries
- `docs/` for long-form documentation
- `uv_only_monorepo/` for a separate workspace-first example layout

## Install / Setup

You can work with this repo in a few different ways depending on whether you want the full Pants workflow or just a local Python environment.

#### Method 1: Pants + local tooling

- Install Python 3.11 or newer.
- Install `pants` 2.30.0.
- Install Docker if you want to build or test container targets.
- Install optional developer tools such as `pre-commit`.

Common commands:

- `make test`
- `make lint`
- `make fmt`
- `make tailor`
- `make update-build-files`
- `make pex`
- `make docker-build`

#### Method 2: Python virtual environment

- Create or activate a local virtual environment.
- Install dependencies from [`pyproject.toml`](/Users/cs/git/monorepo/pyproject.toml).
- Use Pants for build graph operations and target-aware test or packaging commands.

#### Method 3: Explore examples only

- Read the package-specific READMEs such as [`examples/example_lib/README.md`](/Users/cs/git/monorepo/examples/example_lib/README.md) and [`infra/db_setup/README.md`](/Users/cs/git/monorepo/infra/db_setup/README.md).
- Run individual targets with Pants as needed, for example `pants test examples/hello_world::` or `pants package ercot_lmp:docker`.

## Common commands

- `pants tailor --check ::` checks whether BUILD files need to be regenerated.
- `pants update-build-files --check ::` checks BUILD file formatting.
- `pants lint ::` runs flake8 plus read-only Black/isort checks.
- `pants fmt ::` applies Black/isort formatting changes.
- `pants test ::` runs the full test suite.
- `pants package ::` builds packageable targets.

## Top-level directories

#### `/ercot_lmp`

Main application package. Contains the monitor entry point and Docker packaging target for the ERCOT LMP workflow.

#### `/lib_ercot`

Shared support library for parsing, validation, retries, CSV output, and other utility logic used by the monitor.

#### `/infra`

Infrastructure assets such as the PostgreSQL image definition and other container-oriented support files.

#### `/examples`

Example packages and binaries such as `hello_world` and `example_lib`.

#### `/sample_flask`

Example web application project used as another monorepo sample.

#### `/uv_only_monorepo`

Separate example monorepo organized around `uv` workspaces rather than Pants.

#### `/tests`

Repository-level tests that exercise the integrated project behavior.

#### `/docs`

Long-form setup, release, template, and implementation notes.

#### `/.github/workflows`

GitHub Actions workflows for CI and release automation.

## Notes

- `pants fmt --check` is not a valid Pants invocation in this repo. Use `pants lint ::` for non-mutating formatting checks and `pants fmt ::` to apply changes.
- BUILD file formatting is handled separately with `pants update-build-files --check ::`.
- Docker packaging targets live in [`ercot_lmp/BUILD`](/Users/cs/git/monorepo/ercot_lmp/BUILD) and [`infra/db_setup/BUILD`](/Users/cs/git/monorepo/infra/db_setup/BUILD).
- GitHub Pages deployment is configured in [`pages.yml`](/Users/cs/git/monorepo/.github/workflows/pages.yml), and the published static site content lives under [`site/`](/Users/cs/git/monorepo/site).
