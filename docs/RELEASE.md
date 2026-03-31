# Release Process

This repo now uses a tag-driven release flow instead of an automated weekly version bump.

## Normal release path

1. Update code and docs on a branch.
2. Merge to `main` or `master` after `ci.yml` passes.
3. Create and push a semantic version tag.

```bash
git tag v0.2.0
git push origin v0.2.0
```

That tag triggers [`release.yml`](/Users/cs/git/monorepo/.github/workflows/release.yml).

## What the release workflow does

- validates BUILD files and lint state again
- runs the full Pants test suite
- packages the PEX binaries
- builds the Docker images
- pushes tagged images to GHCR
- creates a GitHub release with the generated `.pex` files attached

## Manual preview runs

You can run `release.yml` manually from GitHub Actions to build and upload preview artifacts without publishing a tagged release.

That is useful when you want to verify packaging changes before creating a public tag.

## Release rules

- Tags should use the format `vMAJOR.MINOR.PATCH`.
- Only tagged runs publish images and create GitHub releases.
- Manual runs upload artifacts for inspection but do not publish a release.

## Pre-release checklist

- `pants tailor --check ::`
- `pants update-build-files --check ::`
- `pants lint ::`
- `pants test ::`
- `pants package //ercot_lmp:pex //examples/hello_world:pex`
- `pants package //ercot_lmp:docker //infra/db_setup:docker`

## Why this is simpler

- No bot-generated version bump commits.
- No scheduled release job mutating the default branch.
- The same release process works for normal releases and hotfixes.
- CI and release responsibilities are clearly separated.
