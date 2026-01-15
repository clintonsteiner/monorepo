# Release Process

Documentation for the automated and manual release process.

## Automated Weekly Releases

### How It Works

Every **Monday at 00:00 UTC**, the GitHub Actions workflow automatically:

1. **Tests Everything**
   - Runs all unit tests
   - Validates BUILD files (tailor)
   - Checks code formatting (black, isort)
   - Runs linters (flake8)

2. **If All Tests Pass:**
   - Increments the PATCH version (e.g., v1.2.3 → v1.2.4)
   - Updates `pyproject.toml` with new version
   - Builds PEX executables
   - Builds and pushes Docker images
   - Creates Git tag
   - Commits version bump
   - Creates GitHub release with artifacts

3. **If Tests Fail:**
   - No release is created
   - Workflow fails with error details
   - Team is notified via GitHub

### Version Format

Semantic Versioning: `vMAJOR.MINOR.PATCH`

- **MAJOR** (v2.0.0): Breaking changes - **Manual only**
- **MINOR** (v1.3.0): New features - **Manual only**
- **PATCH** (v1.2.4): Bug fixes - **Automated weekly**

## Manual Releases

### When to Release Manually

- **Breaking changes** (bump MAJOR)
- **New features** (bump MINOR)
- **Hotfixes** (immediate PATCH release)
- **Before major deployments**

### Manual Release Process

#### Option 1: Trigger Weekly Release Workflow

```bash
# Via GitHub CLI
gh workflow run weekly-release.yml

# Via GitHub UI
# Go to Actions → Weekly Release → Run workflow → Run workflow
```

This will auto-increment PATCH version.

#### Option 2: Manual Version Bump

For MAJOR or MINOR version bumps:

```bash
# 1. Update version in pyproject.toml
sed -i 's/version = ".*"/version = "2.0.0"/' pyproject.toml

# 2. Commit the change
git add pyproject.toml
git commit -m "chore: bump version to v2.0.0"

# 3. Create and push tag
git tag v2.0.0
git push origin main --tags

# 4. Create release via GitHub
gh release create v2.0.0 \
  --title "Release v2.0.0" \
  --notes "Major release with breaking changes" \
  dist/*.pex
```

## Release Artifacts

Each release includes:

### 1. PEX Files (GitHub Release)

```bash
# Download from latest release
gh release download --pattern '*.pex'

# Or via URL
wget https://github.com/YOUR_ORG/monorepo/releases/download/v1.2.3/ercot_lmp.pex
wget https://github.com/YOUR_ORG/monorepo/releases/download/v1.2.3/hello_world.pex
```

### 2. Docker Images

**Docker Hub:**
```bash
docker pull YOUR_USERNAME/ercot-lmp:latest
docker pull YOUR_USERNAME/ercot-lmp:v1.2.3
docker pull YOUR_USERNAME/ercot-db:latest
docker pull YOUR_USERNAME/ercot-db:v1.2.3
```

**GitHub Container Registry:**
```bash
docker pull ghcr.io/YOUR_ORG/ercot-lmp:latest
docker pull ghcr.io/YOUR_ORG/ercot-lmp:v1.2.3
```

### 3. Release Notes

Auto-generated with:
- Version number
- Artifact sizes
- Installation instructions
- Docker image tags
- Quality check status
- Changelog link

## Pre-Release Checklist

Before creating a manual release:

- [ ] All tests pass locally
  ```bash
  make test
  ```

- [ ] Code is properly formatted
  ```bash
  make fmt
  ```

- [ ] Linters pass
  ```bash
  make lint
  ```

- [ ] BUILD files are current
  ```bash
  make tailor
  ```

- [ ] Documentation is updated
  - README.md
  - CHANGELOG.md (if exists)
  - Version-specific docs

- [ ] Dependencies are up to date
  ```bash
  # Review Dependabot PRs
  ```

- [ ] Docker images build successfully
  ```bash
  make docker-build
  make db-build
  ```

- [ ] PEX files build and run
  ```bash
  make pex
  ./dist/ercot_lmp.pex --help
  ./dist/hello_world.pex --help
  ```

## Hotfix Process

For urgent production fixes:

```bash
# 1. Create hotfix branch from main
git checkout -b hotfix/critical-bug main

# 2. Make fixes and test
# ... make changes ...
make test

# 3. Update version (increment PATCH)
# Edit pyproject.toml: version = "1.2.4"

# 4. Commit and tag
git add .
git commit -m "fix: critical bug in module X"
git tag v1.2.4

# 5. Push and create PR
git push origin hotfix/critical-bug --tags

# 6. Merge PR to main

# 7. Trigger release workflow or create release manually
gh workflow run weekly-release.yml
```

## Rolling Back a Release

If a release has issues:

### Option 1: Create a Fix Release

```bash
# Fix the issue
# Increment version
# Create new release
```

### Option 2: Delete Release and Tag

```bash
# Delete the GitHub release
gh release delete v1.2.3 --yes

# Delete the local tag
git tag -d v1.2.3

# Delete the remote tag
git push origin :refs/tags/v1.2.3

# Delete Docker images (if needed)
# Contact Docker Hub support or use CLI
```

### Option 3: Create a Revert Commit

```bash
# Revert the problematic commit
git revert <commit-hash>

# Create new patch release
git tag v1.2.4
git push origin main --tags
```

## Release Notes Template

When creating manual releases, use this template:

```markdown
# Release vX.Y.Z

## 🚀 What's New

- Feature 1: Description
- Feature 2: Description

## 🐛 Bug Fixes

- Fix 1: Description
- Fix 2: Description

## 📦 What's Included

### PEX Executables
- `ercot_lmp.pex` - Main application (XX MB)
- `hello_world.pex` - CLI tool (XX KB)

### Docker Images
- `ercot-lmp:vX.Y.Z` - Application container
- `ercot-db:vX.Y.Z` - PostgreSQL database

## 📥 Installation

### Using PEX
\`\`\`bash
wget https://github.com/ORG/REPO/releases/download/vX.Y.Z/ercot_lmp.pex
chmod +x ercot_lmp.pex
./ercot_lmp.pex
\`\`\`

### Using Docker
\`\`\`bash
docker pull username/ercot-lmp:vX.Y.Z
docker run --rm username/ercot-lmp:vX.Y.Z
\`\`\`

## ⚠️ Breaking Changes

- Breaking change 1
- Breaking change 2

## 🔄 Migration Guide

Steps to upgrade from previous version...

## ✅ Verified

- ✓ All tests passed
- ✓ Code formatting validated
- ✓ Linting passed
- ✓ Docker images tested
```

## Troubleshooting

### Release Workflow Fails

**Issue:** Weekly release workflow fails on tests

**Solution:**
1. Check workflow logs in Actions tab
2. Fix failing tests locally
3. Push fixes to main
4. Workflow will run again next week (or trigger manually)

### Version Conflict

**Issue:** Tag already exists

**Solution:**
```bash
# Delete existing tag
git tag -d v1.2.3
git push origin :refs/tags/v1.2.3

# Create new tag
git tag v1.2.3
git push origin main --tags
```

### Docker Push Fails

**Issue:** Cannot push Docker images

**Solution:**
1. Check Docker Hub credentials in GitHub Secrets
2. Verify token has push permissions
3. Ensure repository exists on Docker Hub
4. Check rate limits

## Monitoring Releases

### GitHub CLI

```bash
# List releases
gh release list

# View specific release
gh release view v1.2.3

# Check workflow status
gh run list --workflow=weekly-release.yml
```

### Email Notifications

Configure in GitHub Settings → Notifications:
- Watch releases
- Subscribe to Actions
- Get failure notifications

## Release Metrics

Track release success:

- **Release Frequency**: Weekly (automated)
- **Test Success Rate**: Should be >95%
- **Time to Release**: <10 minutes (automated)
- **Artifact Sizes**: Monitor for unexpected growth
- **Download Stats**: Check GitHub Insights

## Best Practices

### DO ✅
- Let automated releases handle PATCH versions
- Test thoroughly before manual releases
- Use semantic versioning correctly
- Document breaking changes
- Keep CHANGELOG up to date
- Tag all releases
- Include release notes

### DON'T ❌
- Skip tests to force a release
- Manually edit versions without updating pyproject.toml
- Create releases without tags
- Push broken code to main
- Use arbitrary version numbers

## Questions?

- Check GitHub Actions logs
- Review workflow files in `.github/workflows/`
- See `.github/workflows/README.md` for workflow details
