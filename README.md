# ercot-lmp-monitor monorepo

## Overview

This repo is a small Python monorepo built around [Pants](https://www.pantsbuild.org/). It combines a real ERCOT LMP monitoring app, shared libraries, Docker packaging, database bootstrap assets, and a few example projects that show different monorepo layouts.

The root project uses Pants 2.30.0 for dependency inference, linting, formatting, testing, packaging, and Docker image builds. There is also a separate `uv_only_monorepo/` example for a workspace-first layout that does not depend on Pants.

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

- Read the package-specific READMEs such as [`example_lib/README.md`](/Users/cs/git/monorepo/example_lib/README.md) and [`db_setup/README.md`](/Users/cs/git/monorepo/db_setup/README.md).
- Run individual targets with Pants as needed, for example `pants test hello_world::` or `pants package ercot_lmp:docker`.

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

#### `/db_setup`

PostgreSQL image definition plus SQL initialization scripts for local database setup.

#### `/hello_world`

Minimal executable example with tests and a PEX target.

#### `/example_lib`

Small reusable library example that demonstrates a clean package layout, tests, and library documentation.

#### `/sample_flask`

Example web application project used as another monorepo sample.

#### `/uv_only_monorepo`

Separate example monorepo organized around `uv` workspaces rather than Pants.

#### `/tests`

Repository-level tests that exercise the integrated project behavior.

#### `/3rdparty`

Third-party dependency target definitions used by Pants.

#### `/.github/workflows`

GitHub Actions workflows for CI and release automation.

## Notes

- `pants fmt --check` is not a valid Pants invocation in this repo. Use `pants lint ::` for non-mutating formatting checks and `pants fmt ::` to apply changes.
- BUILD file formatting is handled separately with `pants update-build-files --check ::`.
- Docker packaging targets live in [`ercot_lmp/BUILD`](/Users/cs/git/monorepo/ercot_lmp/BUILD) and [`db_setup/BUILD`](/Users/cs/git/monorepo/db_setup/BUILD).
