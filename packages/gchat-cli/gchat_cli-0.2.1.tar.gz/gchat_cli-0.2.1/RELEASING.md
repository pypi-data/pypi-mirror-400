# Releasing gchat

This document describes the release process for gchat.

## Overview

Releases are fully automated via GitHub Actions. When you push a version tag, the workflow will:

1. Build the package
2. Publish to PyPI
3. Create a GitHub Release with auto-generated notes
4. Update the Homebrew formula

## How to Release

### 1. Update the version

Update the version in both files:

```bash
# src/gchat/__init__.py
__version__ = "X.Y.Z"

# pyproject.toml
version = "X.Y.Z"
```

### 2. Commit the version bump

```bash
git add src/gchat/__init__.py pyproject.toml
git commit -m "Bump version to X.Y.Z"
```

### 3. Create and push a tag

```bash
git tag vX.Y.Z -m "Brief description of release"
git push && git push --tags
```

That's it! The GitHub Actions workflow handles everything else.

## Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** (`X.0.0`): Breaking changes
- **MINOR** (`0.X.0`): New features, backward compatible
- **PATCH** (`0.0.X`): Bug fixes, backward compatible

## Monitoring the Release

1. Go to [Actions](https://github.com/chadsaun/gchat/actions) to watch the workflow
2. The workflow has four jobs:
   - `build` - Builds the Python package
   - `publish-pypi` - Publishes to PyPI
   - `create-release` - Creates GitHub Release
   - `update-homebrew` - Updates the Homebrew formula

## Setup Requirements

### PyPI (Trusted Publishing)

PyPI publishing uses [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (no API token needed). This is configured in the PyPI project settings.

### Homebrew Tap Token

The workflow needs a `HOMEBREW_TAP_TOKEN` secret to update the Homebrew formula:

1. Create a fine-grained token at https://github.com/settings/tokens?type=beta
2. Scope it to the `homebrew-tap` repository with **Contents: Read and write**
3. Add it as a secret at https://github.com/chadsaun/gchat/settings/secrets/actions

## Manual Release (if needed)

If automation fails, you can release manually:

### PyPI

```bash
pip install build twine
python -m build
twine upload dist/*
```

### Homebrew

1. Get the SHA256 of the new release:
   ```bash
   curl -sL https://files.pythonhosted.org/packages/source/g/gchat-cli/gchat_cli-X.Y.Z.tar.gz | shasum -a 256
   ```

2. Update `Formula/gchat.rb` in the [homebrew-tap](https://github.com/chadsaun/homebrew-tap) repo:
   - Update the `url` with the new version
   - Update the `sha256` hash

## Troubleshooting

### PyPI publish failed

- Check that the version doesn't already exist on PyPI
- Verify the `pypi` environment is configured in repo settings

### Homebrew update failed

- Check that `HOMEBREW_TAP_TOKEN` secret exists and hasn't expired
- Verify the token has write access to the homebrew-tap repo

### Release notes are wrong

- GitHub auto-generates notes from PR titles and commits
- You can edit the release notes manually on GitHub after creation
