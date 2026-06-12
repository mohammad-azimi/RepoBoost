# Release Checklist

This document describes how to prepare a RepoBoost release.

RepoBoost is not published to PyPI yet. These steps are for preparing and validating a release locally before publishing.

## 1. Check repository status

```bash
git status
```

Make sure the working tree is clean before building a release.

## 2. Run tests

```bash
pytest
```

Expected result:

```text
29 passed
```

## 3. Run RepoBoost on itself

```bash
repoboost scan . --fail-under 90
repoboost doctor .
repoboost inspect .
repoboost topics .
repoboost recommend .
repoboost badge .
```

## 4. Build the package

```bash
python -m build
```

This should create a `dist/` directory with files similar to:

```text
repoboost-0.1.0-py3-none-any.whl
repoboost-0.1.0.tar.gz
```

## 5. Check package metadata

```bash
python -m twine check dist/*
```

Expected result:

```text
PASSED
```

## 6. Test install from wheel locally

On Windows:

```bash
pip install --force-reinstall dist\repoboost-0.1.0-py3-none-any.whl
repoboost --version
repoboost scan .
```

Expected result:

```text
RepoBoost 0.1.0
```

## 7. Restore editable install for development

After testing the wheel, return to editable development mode:

```bash
pip install -e ".[dev]"
```

## 8. Publishing notes

Do not publish immediately unless all checks pass.

Recommended publishing order:

1. TestPyPI
2. Real PyPI
3. GitHub release
4. LinkedIn/GitHub announcement post

## 9. Version checklist

Before publishing a new version:

- Update `version` in `pyproject.toml`
- Update `__version__` in `src/repoboost/__init__.py`
- Run tests
- Build package
- Run `twine check`
- Create a Git tag
- Publish release