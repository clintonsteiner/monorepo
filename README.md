# ercot-lmp-monitor monorepo

This repository is a small Python monorepo built around [Pants](https://www.pantsbuild.org/). It includes the ERCOT LMP monitor, shared libraries, Docker images, and a few example projects without keeping every concern at the repo root.

## Repo layout

- `ercot_lmp/`: main application package and Docker image target
- `lib_ercot/`: shared utility library
- `infra/`: infrastructure-oriented assets, including the PostgreSQL image
- `examples/`: sample Pants packages and binaries
- `sample_flask/`: separate Flask example app
- `uv_only_monorepo/`: uv-workspace example project
- `tests/`: repository-level integration and Docker tests
- `docs/`: maintained project documentation

## Quick start

Requirements:

- Python 3.11+
- Pants 2.30.0
- Docker for Docker packaging or Docker-tagged tests
- `pre-commit` if you want local hook enforcement

Common commands:

- `make test`
- `make lint`
- `make fmt`
- `make tailor`
- `make update-build-files`
- `make pex`
- `make docker-build`

Direct Pants equivalents:

- `pants tailor --check ::`
- `pants update-build-files --check ::`
- `pants lint ::`
- `pants fmt ::`
- `pants test ::`
- `pants package ::`

## Documentation

The main docs entrypoint is [docs/README.md](/Users/cs/git/monorepo/docs/README.md).

Key guides:

- [docs/SETUP.md](/Users/cs/git/monorepo/docs/SETUP.md)
- [docs/RELEASE.md](/Users/cs/git/monorepo/docs/RELEASE.md)
- [docs/GITHUB_PAGES.md](/Users/cs/git/monorepo/docs/GITHUB_PAGES.md)
- [examples/example_lib/README.md](/Users/cs/git/monorepo/examples/example_lib/README.md)
- [infra/db_setup/README.md](/Users/cs/git/monorepo/infra/db_setup/README.md)

## CI and dependency maintenance

- GitHub Actions workflow notes live in [.github/workflows/README.md](/Users/cs/git/monorepo/.github/workflows/README.md).
- Dependabot configuration lives in [.github/dependabot.yml](/Users/cs/git/monorepo/.github/dependabot.yml).
- Docker packaging targets live in [ercot_lmp/BUILD](/Users/cs/git/monorepo/ercot_lmp/BUILD) and [infra/db_setup/BUILD](/Users/cs/git/monorepo/infra/db_setup/BUILD).

## Notes

- `pants fmt --check` is not a valid invocation in this repo. Use `pants lint ::` for non-mutating formatting checks and `pants fmt ::` to apply changes.
- BUILD file formatting is handled separately with `pants update-build-files --check ::`.
