# TestPyPI Publishing Guide

This document explains how to publish RepoBoost to TestPyPI before publishing to the real PyPI index.

TestPyPI is used only for testing package publishing and installation.

## 1. Create a TestPyPI account

Create or log in to a TestPyPI account.

Important: TestPyPI and PyPI use separate accounts.

## 2. Configure Trusted Publishing on TestPyPI

Go to your TestPyPI account publishing settings and create a pending trusted publisher.

Use these values:

```text
PyPI project name: repoboost
Owner: mohammad-azimi
Repository name: RepoBoost
Workflow name: publish-testpypi.yml
Environment name: leave empty
```

In this workflow, no GitHub environment is used. The environment field is optional for PyPI trusted publishing.

## 3. Run the workflow manually

Go to:

```text
GitHub repository -> Actions -> Publish to TestPyPI -> Run workflow
```

Run it from the `main` branch.

## 4. Install from TestPyPI

After the workflow succeeds, test installation in a clean virtual environment.

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ repoboost
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

## 5. If the package name is already taken

If TestPyPI or PyPI rejects the package name, choose another package name in `pyproject.toml`.

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
- workflow environment URL