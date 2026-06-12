# PyPI Publishing Guide

This document explains how to publish RepoBoost to the real PyPI index after testing on TestPyPI.

Do not publish to PyPI until TestPyPI installation works correctly.

## 1. Create or log in to a PyPI account

PyPI and TestPyPI use separate accounts.

Use the real PyPI website for this step.

## 2. Configure Trusted Publishing on PyPI

Go to your PyPI account publishing settings and create a pending trusted publisher.

Use these values:

```text
PyPI project name: repoboost
Owner: mohammad-azimi
Repository name: RepoBoost
Workflow name: publish-pypi.yml
Environment name: leave empty
```

In this workflow, no GitHub environment is used. The environment field is optional for PyPI trusted publishing.

## 3. Run final local checks

Before publishing to PyPI, run:

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

## 6. If the package name is already taken

If PyPI rejects the package name, choose another package name in `pyproject.toml`.

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