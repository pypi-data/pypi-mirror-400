# Releasing VibeLab

## Quick Release (Recommended)

1. Go to **Actions** → **Bump and Release** → **Run workflow**
2. Select:
   - `bump_type`: `patch`, `minor`, or `major`
   - `repository`: `testpypi` (to test) or `pypi` (to publish)
3. Click **Run workflow**

This will:
- Bump the version in `src/vibelab/__init__.py`
- Sync dependencies and build frontend
- Commit and tag as `vX.Y.Z`
- Push to main
- Build and publish the package
- Create a GitHub Release (if publishing to PyPI)

## Two-Step Release

If you want to verify before publishing:

### Step 1: Bump Version

1. Go to **Actions** → **Version Bump** → **Run workflow**
2. Select `bump_type` and run
3. Verify the commit and tag were created correctly

### Step 2: Publish

1. Go to **Actions** → **Release** → **Run workflow**
2. Select `testpypi` to test, or `pypi` to publish
3. Run the workflow

## Local Release (Alternative)

```bash
# Bump version, commit, tag, and push
make release-patch   # 0.0.2 → 0.0.3
make release-minor   # 0.0.2 → 0.1.0
make release-major   # 0.0.2 → 1.0.0

# Then trigger the Release workflow in GitHub Actions UI
```

## Version Scheme

VibeLab uses [Semantic Versioning](https://semver.org/):

- **patch**: Bug fixes, minor improvements (0.0.2 → 0.0.3)
- **minor**: New features, backwards compatible (0.0.2 → 0.1.0)
- **major**: Breaking changes (0.0.2 → 1.0.0)

## Setup Requirements

Before your first release, configure:

1. **PyPI Trusted Publishing** (no token needed):
   - Go to PyPI project settings → Publishing → Add GitHub as trusted publisher
   - Repository: `<owner>/<repo>`
   - Workflow: `release.yml` (for Release workflow)
   - Workflow: `bump-and-release.yml` (for Bump and Release workflow)

2. **TestPyPI** (optional, for testing):
   - Create API token at https://test.pypi.org/manage/account/token/
   - Add as repository secret: Settings → Secrets → `TEST_PYPI_API_TOKEN`

## Workflow Files

| Workflow | Purpose |
|----------|---------|
| `bump-and-release.yml` | One-click: bump + publish |
| `version-bump.yml` | Bump version only |
| `release.yml` | Publish only |

