# Release Process

This document describes how to release a new version of `mcp-taxii` to PyPI.

## Prerequisites

### GitHub Repository Setup

1. **Configure Trusted Publishing on PyPI**:
   - Go to [PyPI](https://pypi.org/) and log in
   - Navigate to your project settings → Publishing
   - Add a new "trusted publisher" for GitHub Actions:
     - Owner: `davydany`
     - Repository: `mcp-taxii`
     - Workflow name: `publish.yml`
     - Environment name: `pypi`

2. **Configure Trusted Publishing on TestPyPI** (optional, for testing):
   - Go to [TestPyPI](https://test.pypi.org/) and log in
   - Same process as above, but use environment name: `testpypi`

3. **Create GitHub Environments**:
   - Go to your GitHub repository → Settings → Environments
   - Create two environments:
     - `pypi` - for production releases
     - `testpypi` - for test releases (optional)

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Release Steps

### 1. Update Version

Update the version in `pyproject.toml`:

```toml
[project]
version = "X.Y.Z"
```

### 2. Update Changelog (if applicable)

Document changes in release notes.

### 3. Commit and Push

```bash
git add pyproject.toml
git commit -m "Bump version to X.Y.Z"
git push origin main
```

### 4. Create a GitHub Release

1. Go to GitHub → Releases → "Create a new release"
2. Click "Choose a tag" and create a new tag: `vX.Y.Z`
3. Set the release title: `vX.Y.Z`
4. Add release notes describing the changes
5. Click "Publish release"

This will automatically trigger the publish workflow.

## Manual Publishing

### Local Publishing (Development)

For testing the build locally:

```bash
# Build the package
make build

# Publish to TestPyPI (for testing)
make publish-test

# Publish to PyPI (production)
make publish
```

### GitHub Actions Manual Trigger

You can also manually trigger the publish workflow:

1. Go to GitHub → Actions → "Publish to PyPI"
2. Click "Run workflow"
3. Select target: `testpypi` or `pypi`
4. Click "Run workflow"

## Verification

After publishing, verify the release:

```bash
# For TestPyPI
pip install -i https://test.pypi.org/simple/ mcp-taxii

# For PyPI
pip install mcp-taxii
```

## Troubleshooting

### Build Issues

If the build fails:
```bash
make clean
make install
make build
```

### Publishing Issues

1. **Authentication errors**: Ensure trusted publishing is configured correctly
2. **Version conflicts**: Ensure the version doesn't already exist on PyPI
3. **Missing metadata**: Check `pyproject.toml` for required fields

### CI Issues

Check the GitHub Actions logs for detailed error messages.
