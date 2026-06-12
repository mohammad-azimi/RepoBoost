# PyPI Publishing Guide

RepoBoost is published on PyPI.

Install it with:

```bash
pip install repoboost
```

This document explains how to publish future RepoBoost versions to the real PyPI index.

## 1. Prerequisites

Before publishing a new version, make sure:

- The TestPyPI release works
- Local tests pass
- Local package build works
- Package metadata passes `twine check`
- The version number has been updated
- The PyPI trusted publisher is configured

## 2. Trusted Publishing

RepoBoost uses PyPI trusted publishing through GitHub Actions.

The PyPI trusted publisher should use these values:

```text
PyPI project name: repoboost
Owner: mohammad-azimi
Repository name: RepoBoost
Workflow name: publish-pypi.yml
Environment name: leave empty
```

The workflow file is:

```text
.github/workflows/publish-pypi.yml
```

The publishing job must include:

```yaml
permissions:
  id-token: write
```

No PyPI token or password should be stored in GitHub secrets for this workflow.

## 3. Run final local checks

Before publishing a new PyPI version, run:

```bash
pytest
python -m build
python -m twine check dist/*
repoboost --version
repoboost scan . --fail-under 90
```

Expected results:

```text
29 passed
PASSED
RepoBoost 0.1.0
```

## 4. Run the PyPI workflow manually

Go to:

```text
GitHub repository -> Actions -> Publish to PyPI -> Run workflow
```

Run it from the `main` branch.

## 5. Install from PyPI

After the workflow succeeds, test installation in a clean virtual environment.

```bash
pip install repoboost
```

Then test the command:

```bash
repoboost --version
repoboost scan .
```

Expected result:

```text
RepoBoost 0.1.0
```

## 6. Version update checklist

Before publishing a new version:

- Update `version` in `pyproject.toml`
- Update `__version__` in `src/repoboost/__init__.py`
- Update `CHANGELOG.md`
- Run tests
- Build package
- Run `twine check`
- Publish to TestPyPI
- Test TestPyPI installation
- Publish to PyPI
- Test PyPI installation
- Create a GitHub release

## 7. If the package name is unavailable

If PyPI rejects the package name in a future setup, choose another package name in `pyproject.toml`.

Possible alternatives:

```text
repoboost-cli
repo-boost
repo-boost-cli
```

If the project name changes, update:

- `pyproject.toml`
- README installation command
- TestPyPI trusted publisher project name
- PyPI trusted publisher project name
- TestPyPI workflow URL
- PyPI project links