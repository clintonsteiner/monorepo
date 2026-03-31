# GitHub Pages Guide

This repository can publish a small project site through GitHub Actions instead of using branch-based Pages publishing.

## Workflow

The Pages deployment workflow lives at [`.github/workflows/pages.yml`](/Users/cs/git/monorepo/.github/workflows/pages.yml).

It uses the current Actions-based GitHub Pages flow:

- `actions/configure-pages@v5`
- `actions/upload-pages-artifact@v4`
- `actions/deploy-pages@v4`

## What gets published

The workflow publishes the static content under `site/`.

Key files:

- [site/index.html](/Users/cs/git/monorepo/site/index.html)
- [site/styles.css](/Users/cs/git/monorepo/site/styles.css)
- [site/404.html](/Users/cs/git/monorepo/site/404.html)

## Repository setup

To enable the site in GitHub:

1. Open repository `Settings`.
2. Open `Pages`.
3. Set the source to `GitHub Actions`.

After that, pushes to `master` that touch `site/`, `docs/`, `README.md`, or the Pages workflow will trigger a deployment.

## Editing the site

- Keep long-form project docs in `docs/`.
- Keep the public landing page and static Pages assets in `site/`.
- Update the workflow only if the deployment trigger or artifact path changes.

This split keeps the repo docs readable in GitHub while also providing a lightweight published site.
