# GitHub Actions Workflows

Automated CI/CD pipelines for the ERCOT LMP Monorepo.

## Workflows

### 1. CI (`ci.yml`)

**Triggers:**
- Push to main/master/develop branches
- Pull requests to main/master/develop branches

**Jobs:**
- **Test and Lint**
  - Check BUILD files are up to date (tailor)
  - Check BUILD file formatting
  - Run linters (black, isort, flake8)
  - Check code formatting
  - Run all tests
- **Build Artifacts**
  - Build PEX executables
  - Build Docker images
  - Test Docker containers
  - Upload artifacts

**Status:** Required to pass before merging PRs

### 2. Weekly Release (`weekly-release.yml`)

**Triggers:**
- Scheduled: Every Monday at 00:00 UTC
- Manual: `workflow_dispatch`

**Jobs:**
- **Test Before Release**
  - Run full test suite
  - Validate formatting and linting
- **Create Release**
  - Calculate next version (auto-increment patch)
  - Update pyproject.toml version
  - Build PEX files
  - Build and push Docker images
  - Commit version bump
  - Create Git tag
  - Create GitHub release with artifacts

**Outputs:**
- GitHub Release with PEX files attached
- Docker images pushed to Docker Hub and GHCR
- Automated release notes

### 3. Docker Publish (`docker-publish.yml`)

**Triggers:**
- GitHub release published
- Manual: `workflow_dispatch`

**Jobs:**
- Build and push Docker images to:
  - Docker Hub
  - GitHub Container Registry (ghcr.io)
- Tag with version and `latest`

### 4. Dependabot (`dependabot.yml`)

**Updates:**
- GitHub Actions (weekly)
- Python dependencies (weekly)
- Docker base images (weekly)

**Configuration:**
- Automatically creates PRs for updates
- Labels PRs appropriately

## Setup Requirements

### GitHub Secrets

Add these secrets to your repository:

```bash
# Docker Hub credentials (required for Docker image publishing)
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-password-or-token
```

**How to add secrets:**
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret

### GitHub Permissions

The workflows require these permissions:
- ✅ `contents: write` - For creating releases and pushing tags
- ✅ `packages: write` - For publishing to GitHub Container Registry
- ✅ `actions: read` - For workflow caching

These are configured in each workflow file.

## Versioning Strategy

### Semantic Versioning

Format: `vMAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (manual increment)
- **MINOR**: New features (manual increment)
- **PATCH**: Bug fixes and improvements (auto-incremented weekly)

### Weekly Auto-Release Process

1. Every Monday at 00:00 UTC (or manual trigger)
2. Run all tests and checks
3. If all tests pass:
   - Increment PATCH version (e.g., v1.2.3 → v1.2.4)
   - Update `pyproject.toml`
   - Build artifacts
   - Create Git tag
   - Push Docker images
   - Create GitHub release

### Manual Version Bump

To manually increment MAJOR or MINOR:

```bash
# Update version in pyproject.toml
version = "2.0.0"

# Commit and tag
git add pyproject.toml
git commit -m "chore: bump version to v2.0.0"
git tag v2.0.0
git push origin main --tags

# This will trigger the docker-publish workflow
```

## Usage Examples

### Running Workflows Manually

**Trigger weekly release manually:**
```bash
# Via GitHub UI:
# Actions → Weekly Release → Run workflow

# Via GitHub CLI:
gh workflow run weekly-release.yml
```

**Publish Docker images manually:**
```bash
gh workflow run docker-publish.yml
```

### Checking Workflow Status

```bash
# List all workflows
gh workflow list

# View workflow runs
gh run list --workflow=ci.yml

# View specific run
gh run view <run-id>

# Watch a running workflow
gh run watch
```

### Downloading Artifacts

```bash
# Download PEX files from latest release
gh release download --pattern '*.pex'

# Download from specific release
gh release download v1.2.3 --pattern '*.pex'
```

## Docker Image Usage

### From Docker Hub

```bash
# Pull latest
docker pull <username>/ercot-lmp:latest
docker pull <username>/ercot-db:latest

# Pull specific version
docker pull <username>/ercot-lmp:v1.2.3
docker pull <username>/ercot-db:v1.2.3
```

### From GitHub Container Registry

```bash
# Pull latest
docker pull ghcr.io/<org>/ercot-lmp:latest
docker pull ghcr.io/<org>/ercot-db:latest

# Pull specific version
docker pull ghcr.io/<org>/ercot-lmp:v1.2.3
```

## Monitoring and Notifications

### Email Notifications

GitHub sends email notifications on:
- Workflow failures
- New releases
- Dependabot PRs

Configure in: Settings → Notifications

### Slack Integration (Optional)

Add to workflow files:

```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Workflow failed: ${{ github.workflow }}"
      }
```

## Troubleshooting

### Workflow Fails on Pants Commands

**Issue:** Pants initialization fails

**Solution:**
- Ensure `pants.toml` is valid
- Check Python version matches (3.11)
- Clear Pants cache: Add `pants clean-all` step

### Docker Build Fails

**Issue:** Cannot build Docker images

**Solution:**
- Check Dockerfile syntax
- Ensure PEX files are built first
- Verify `.dockerignore` isn't excluding needed files

### Release Creation Fails

**Issue:** Cannot create release or push tags

**Solution:**
- Check `GITHUB_TOKEN` permissions
- Ensure no conflicting tags exist
- Verify version format is correct (vX.Y.Z)

### Docker Push Fails

**Issue:** Cannot push to Docker Hub

**Solution:**
- Verify `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets
- Check Docker Hub token permissions
- Ensure repository name is correct

## Best Practices

### CI/CD
- ✅ Always run tests before releasing
- ✅ Use semantic versioning
- ✅ Tag all releases
- ✅ Keep workflows DRY (use reusable workflows)
- ✅ Cache Pants and Docker builds

### Security
- ✅ Use secrets for credentials
- ✅ Use GitHub tokens, not personal access tokens
- ✅ Scan Docker images for vulnerabilities
- ✅ Keep GitHub Actions updated

### Maintenance
- ✅ Review Dependabot PRs weekly
- ✅ Monitor workflow runs
- ✅ Update workflows when adding new packages
- ✅ Test workflows in feature branches

## Custom Workflows

### Adding a New Workflow

1. Create `.github/workflows/your-workflow.yml`
2. Define triggers and jobs
3. Test with manual trigger first
4. Document in this README

### Reusable Workflow Example

```yaml
name: Reusable Test

on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
      - run: pants test ::
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Pants CI/CD Guide](https://www.pantsbuild.org/docs/using-pants/using-pants-in-ci)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Semantic Versioning](https://semver.org/)
