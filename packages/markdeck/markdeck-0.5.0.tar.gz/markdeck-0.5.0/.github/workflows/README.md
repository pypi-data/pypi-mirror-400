# GitHub Actions Workflows

This directory contains automated workflows for the MarkDeck project.

## Table of Contents

1. [Screenshots Workflow](#screenshots-workflow) - Automated screenshot generation
2. [PyPI Publishing Workflow](#pypi-publishing-workflow) - Package distribution to PyPI
3. [Claude Code Integration](#claude-code-integration) - AI-assisted development
4. [Code Review Workflow](#code-review-workflow) - Automated code reviews

---

## Screenshots Workflow

Automatically generates screenshots of the MarkDeck grid view feature using Playwright in a CI environment.

### How to Use

#### Method 1: Manual Trigger (Recommended)

1. Go to **Actions** tab in GitHub
2. Select **"Generate Grid View Screenshots"** workflow
3. Click **"Run workflow"**
4. Screenshots will be:
   - Generated automatically
   - Uploaded as artifacts (downloadable for 90 days)
   - Committed back to the repository in `screenshots/` directory

#### Method 2: Automatic Trigger

The workflow runs automatically when you push changes to:
- `markdeck/static/**` (HTML/CSS/JS changes)
- `examples/**` (Example presentation changes)

### What Gets Generated

The workflow creates 6 screenshots:

1. **01_normal_view.png** - Normal presentation view
2. **02_grid_overview.png** - Grid view opened showing all slides
3. **03_grid_scrolled.png** - Scrolled grid view
4. **04_after_navigation.png** - After clicking to navigate to slide 3
5. **05_grid_current_highlight.png** - Grid showing current slide highlighted
6. **06_grid_hover_effect.png** - Hover effect demonstration

### Downloading Screenshots

**From GitHub UI:**
1. Go to the **Actions** tab
2. Click on the completed workflow run
3. Scroll down to **Artifacts**
4. Download **grid-view-screenshots.zip**

**Using GitHub CLI:**
```bash
gh run download <run-id> -n grid-view-screenshots
```

### Why This Works

This workflow solves the network restriction issue because:
- ✅ GitHub Actions has full internet access
- ✅ Can download Playwright browser binaries
- ✅ Runs in a clean Ubuntu environment
- ✅ No corporate firewall restrictions
- ✅ Automated and reproducible

### Local Testing

To test the workflow locally with `act`:

```bash
# Install act (GitHub Actions local runner)
brew install act  # macOS
# or
sudo snap install act  # Linux

# Run the workflow
act workflow_dispatch -W .github/workflows/screenshots.yml
```

### Troubleshooting

**If the workflow fails:**

1. **Server not starting:**
   - Check MarkDeck installation succeeded
   - Verify port 8888 is available
   - Check server logs in workflow output

2. **Screenshots not captured:**
   - Ensure Playwright installed correctly
   - Check browser binary installation
   - Verify `capture_screenshots.py` exists

3. **Commit fails:**
   - Check repository permissions
   - Ensure GITHUB_TOKEN has write access
   - Verify branch protection rules

### Environment Details

**OS:** Ubuntu Latest (GitHub-hosted runner)
**Node.js:** v20
**Python:** 3.11
**Browser:** Chromium (via Playwright)
**Resolution:** 1920x1080

### Cost

GitHub Actions is free for public repositories and includes:
- 2,000 minutes/month for private repos (free tier)
- Unlimited minutes for public repos

This workflow uses approximately **2-3 minutes** per run.

---

## PyPI Publishing Workflow

**File:** `.github/workflows/publish-pypi.yml`

Publishes the MarkDeck package to PyPI (Python Package Index) for distribution. This workflow is **restricted to repository owners only**.

### Security & Access Control

**This workflow only runs if:**
- Repository owner is `orangewise`
- Repository is `orangewise/markdeck` (not a fork)
- Triggered manually or by creating a GitHub release

**Required Secrets:**
- `PYPI_API_TOKEN` - Production PyPI API token
- `TEST_PYPI_API_TOKEN` - TestPyPI API token (for testing)

### How to Use

#### Method 1: Manual Trigger (Recommended for Testing)

1. Go to **Actions** tab in GitHub
2. Select **"Publish to PyPI"** workflow
3. Click **"Run workflow"**
4. Choose options:
   - **Branch:** Usually `main` or release branch
   - **Publish to TestPyPI:** Check this box to test the upload first
5. Click **"Run workflow"**

#### Method 2: GitHub Release (Recommended for Production)

1. Create a new release on GitHub:
   ```bash
   # Tag the release
   git tag v0.3.0
   git push origin v0.3.0
   ```

2. Create release on GitHub UI:
   - Go to **Releases** → **Create new release**
   - Choose the tag you just created
   - Write release notes
   - Click **"Publish release"**

3. Workflow automatically publishes to PyPI

### Workflow Steps

1. **Checkout** - Get repository code
2. **Setup Python** - Install Python 3.11
3. **Install uv** - Install package manager
4. **Install build tools** - Install `build` and `twine`
5. **Verify version** - Extract version from `pyproject.toml`
6. **Build distribution** - Create wheel (`.whl`) and tarball (`.tar.gz`)
7. **Check distribution** - Validate package with `twine check`
8. **Verify contents** - List files in wheel and tarball
9. **Publish** - Upload to TestPyPI or PyPI
10. **Upload artifacts** - Save build artifacts for 90 days
11. **Create summary** - Generate release summary in workflow

### Version Management

**Before publishing:**

1. Update version in `pyproject.toml`:
   ```toml
   [project]
   name = "markdeck"
   version = "0.3.1"  # Update this
   ```

2. Update version in `markdeck/__init__.py`:
   ```python
   __version__ = "0.3.1"
   ```

3. Commit changes:
   ```bash
   git add pyproject.toml markdeck/__init__.py
   git commit -m "Bump version to 0.3.1"
   git push
   ```

### Publishing Checklist

Before publishing to PyPI:

- [ ] All tests pass (`python -m unittest discover tests/`)
- [ ] Code is formatted (`ruff format markdeck/ tests/`)
- [ ] Linting passes (`ruff check markdeck/ tests/`)
- [ ] Version is updated in `pyproject.toml` and `__init__.py`
- [ ] `CHANGELOG.md` is updated (if exists)
- [ ] `README.md` is up to date
- [ ] Create GitHub release with release notes

### Testing the Package Build Locally

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# Check package
twine check dist/*

# Verify contents
python -m zipfile -l dist/*.whl
tar -tzf dist/*.tar.gz

# Test install locally
pip install dist/*.whl

# Or upload to TestPyPI manually
twine upload --repository testpypi dist/*
```

### Troubleshooting

**Issue: "File already exists" error**
- **Cause:** Version already published to PyPI
- **Solution:** Increment version number in `pyproject.toml`

**Issue: "Invalid API token"**
- **Cause:** `PYPI_API_TOKEN` secret not set or incorrect
- **Solution:**
  1. Go to PyPI.org → Account Settings → API tokens
  2. Create new token with scope for `markdeck` project
  3. Add to GitHub Secrets: Settings → Secrets → Actions → New secret

**Issue: Workflow doesn't run**
- **Cause:** Not repository owner or running on fork
- **Solution:** Only repository owner can trigger this workflow

**Issue: Build fails**
- **Cause:** Missing dependencies or syntax errors
- **Solution:**
  - Check workflow logs for errors
  - Run build locally first: `python -m build`
  - Fix errors and commit

### PyPI Package Information

**Package Name:** `markdeck`

**Install Command:**
```bash
pip install markdeck
# or
uv pip install markdeck
```

**Package URLs:**
- **PyPI:** https://pypi.org/project/markdeck/
- **TestPyPI:** https://test.pypi.org/project/markdeck/

### Release Strategy

**Semantic Versioning** (MAJOR.MINOR.PATCH):
- **MAJOR** (1.0.0) - Incompatible API changes
- **MINOR** (0.3.0) - New features, backwards compatible
- **PATCH** (0.3.1) - Bug fixes, backwards compatible

**Pre-release versions:**
- Alpha: `0.3.0a1`
- Beta: `0.3.0b1`
- Release Candidate: `0.3.0rc1`

### Cost

This workflow is **free** for public repositories on GitHub Actions.

---

## Claude Code Integration

**File:** `.github/workflows/claude.yml`

Enables `@claude` mentions in issues and pull requests for AI-assisted development.

**Triggers:**
- Issue comments containing `@claude`
- PR review comments containing `@claude`
- Issues with `@claude` in title/body

**Required Secret:**
- `CLAUDE_CODE_OAUTH_TOKEN`

---

## Code Review Workflow

**File:** `.github/workflows/claude-code-review.yml`

Automated code review for pull requests using Claude.

**See workflow file for details.**
