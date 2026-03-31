# GitHub Pages Guide

This repo does not currently publish a GitHub Pages site, but the `docs/` directory is structured so you can add one without reorganizing the repository again.

## Recommended approach

Use GitHub Pages with a dedicated static site generator workflow instead of publishing raw Markdown files directly from the default branch.

That keeps the source docs in `docs/` and makes it easier to add navigation, theming, and search later.

Good options:

- MkDocs for a simple docs-first site
- Docusaurus if you want versioning and a richer frontend
- plain static HTML in `docs/site/` if you want the smallest setup

## Simple Pages setup

1. Choose a generator and add its config at the repo root.
2. Keep long-form source docs in `docs/`.
3. Generate the built site into a publish directory such as `site/` or `docs/site/`.
4. Add a GitHub Actions workflow that:
   - checks out the repo
   - installs the docs toolchain
   - builds the site
   - deploys with GitHub Pages
5. In repository settings, configure Pages to deploy from GitHub Actions.

## Suggested content layout

- `README.md`: fast repo overview and links
- `docs/README.md`: docs index
- `docs/SETUP.md`: local development setup
- `docs/RELEASE.md`: release process
- `docs/GITHUB_PAGES.md`: publishing and docs hosting guidance

That split keeps the root README short while preserving room for operational docs.

## If you want a minimal first version

Start with:

- a homepage that links to setup, release, and package docs
- one workflow that builds on pushes to `master` or `main`
- no versioning, no blog, no custom theme work

You can add richer navigation later once the docs structure stabilizes.

## Things to avoid

- treating generated site output as hand-edited source
- duplicating the same setup instructions across the root README and multiple docs pages
- publishing directly from a personal workstation instead of CI
