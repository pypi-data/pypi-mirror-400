# Release Guide

This guide explains how to publish a new version of the package using the release branch workflow.

## Overview

The project uses **release branches** for versioning:
- Branch naming: `release/X.Y.x` (e.g., `release/1.0.x`, `release/1.2.x`)
- Tags: `vX.Y.Z` (e.g., `v1.0.0`, `v1.0.1`, `v1.2.0`)
- Patch versions auto-increment on each push to a release branch

## Quick Start Commands

### For a New Minor/Major Version (e.g., 1.0.x → 1.1.x)

```bash
# 1. Create a new release branch
git checkout -b release/1.1.x

# 2. Push the branch to GitHub (triggers auto-publish)
git push -u origin release/1.1.x
```

**Result:** Automatically creates tag `v1.1.0` and publishes to PyPI

---

### For Patch Releases on Existing Branch

```bash
# 1. Switch to the release branch
git checkout release/1.1.x

# 2. Make your changes
# ... edit files ...

# 3. Commit changes
git add .
git commit -m "Fix: your bug fix or feature"

# 4. Push to GitHub (triggers auto-publish)
git push
```

**Result:** Automatically creates tag `v1.1.1` (or next patch) and publishes to PyPI

---

## Step-by-Step Workflow

### 1. Decide Version Number

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (1.X.0): New features, backward compatible
- **PATCH** (1.0.X): Bug fixes, backward compatible

### 2. Create/Switch to Release Branch

**For new MAJOR/MINOR version:**
```bash
# From main branch
git checkout main
git pull origin main

# Create new release branch
git checkout -b release/1.2.x
```

**For existing release branch:**
```bash
git checkout release/1.2.x
git pull origin release/1.2.x
```

### 3. Make Changes (if needed)

```bash
# Edit files
nano src/url_content_type_detector/detector.py

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add support for custom headers"
```

### 4. Push to GitHub

**First time pushing a new branch:**
```bash
git push -u origin release/1.2.x
```

**Subsequent pushes:**
```bash
git push
```

### 5. Automated Process

The GitHub Action automatically:
1. ✅ Detects branch name (`release/1.2.x`)
2. ✅ Finds latest tag for this version (e.g., `v1.2.3`)
3. ✅ Increments patch number (`v1.2.4`)
4. ✅ Creates and pushes the new tag
5. ✅ Builds the package
6. ✅ Publishes to PyPI

### 6. Verify Publication

Check the GitHub Actions tab:
```
https://github.com/krsahil/url-content-type-detector/actions
```

Verify on PyPI:
```
https://pypi.org/project/url-content-type-detector/
```

---

## Complete Example

### Scenario: Release version 1.3.0 with a new feature

```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Create release branch for 1.3.x series
git checkout -b release/1.3.x

# 3. Make your changes
echo "# New feature" >> README.md
git add README.md
git commit -m "Add new feature for 1.3.0"

# 4. Push branch (triggers workflow)
git push -u origin release/1.3.x

# 5. Wait for GitHub Actions to complete
# Check: https://github.com/krsahil/url-content-type-detector/actions

# 6. Verify package published to PyPI
# https://pypi.org/project/url-content-type-detector/
```

**Result:** Package version `1.3.0` is now on PyPI

### Scenario: Bug fix for version 1.3.1

```bash
# 1. Switch to existing release branch
git checkout release/1.3.x
git pull origin release/1.3.x

# 2. Fix the bug
nano src/url_content_type_detector/detector.py
git add .
git commit -m "Fix: handle empty content-type header"

# 3. Push (triggers workflow)
git push

# 4. Wait for GitHub Actions
# Auto-creates tag v1.3.1 and publishes
```

**Result:** Package version `1.3.1` is now on PyPI

---

## Branch Management

### Active Release Branches

Keep track of which release branches are actively maintained:

```bash
# List all release branches
git branch -r | grep release/

# Example output:
# origin/release/1.0.x
# origin/release/1.1.x
# origin/release/1.2.x
```

### Merging Changes Back to Main

After a successful release, merge changes back to main:

```bash
git checkout main
git pull origin main
git merge release/1.2.x
git push origin main
```

---

## Troubleshooting

### Workflow Doesn't Trigger

**Problem:** Pushed to release branch but no workflow runs

**Solution:**
1. Check branch name matches `release/**` pattern
2. Verify you pushed to GitHub: `git push -u origin release/1.2.x`
3. Check Actions tab for errors

### Tag Already Exists

**Problem:** Workflow fails with "tag already exists"

**Solution:** The workflow automatically skips if tag exists. No action needed.

### Build Fails

**Problem:** Build or tests fail during workflow

**Solution:**
1. Check the Actions tab for error logs
2. Test locally before pushing:
   ```bash
   uv build
   ```
3. Fix issues and push again

### PyPI Upload Fails

**Problem:** Workflow fails at publish step

**Solution:**
1. Verify `PYPI_API_TOKEN` secret is set in GitHub repo settings
2. Check token has upload permissions
3. Verify package name isn't taken on PyPI

---

## Requirements

Before releasing, ensure:
- ✅ `PYPI_API_TOKEN` secret configured in GitHub
- ✅ All tests pass
- ✅ README updated
- ✅ Changes documented

---

## Version History

Track your releases on GitHub:
```
https://github.com/krsahil/url-content-type-detector/releases
```

And on PyPI:
```
https://pypi.org/project/url-content-type-detector/#history
```
