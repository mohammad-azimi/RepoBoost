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

## 8. Publish to TestPyPI first

Before publishing to the real PyPI index, publish to TestPyPI.

Read:

```text
docs/TESTPYPI.md
```

Then run the manual GitHub Actions workflow:

```text
Actions -> Publish to TestPyPI -> Run workflow
```

## 9. Test installation from TestPyPI

After the TestPyPI workflow succeeds, test installation in a clean environment:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ repoboost
repoboost --version
repoboost scan .
```

Expected result:

```text
RepoBoost 0.1.0
```

## 10. Publish to PyPI

Only publish to PyPI after TestPyPI works correctly.

Read:

```text
docs/PYPI.md
```

Then run the manual GitHub Actions workflow:

```text
Actions -> Publish to PyPI -> Run workflow
```

## 11. Test installation from PyPI

After the PyPI workflow succeeds, test installation in a clean environment:

```bash
pip install repoboost
repoboost --version
repoboost scan .
```

Expected result:

```text
RepoBoost 0.1.0
```

## 12. Publishing notes

Do not publish to the real PyPI index unless all checks pass.

Recommended publishing order:

1. Local build
2. Local wheel install test
3. TestPyPI
4. TestPyPI installation test
5. Real PyPI
6. PyPI installation test
7. GitHub release
8. LinkedIn/GitHub announcement post

## 13. Version checklist

Before publishing a new version:

- Update `version` in `pyproject.toml`
- Update `__version__` in `src/repoboost/__init__.py`
- Run tests
- Build package
- Run `twine check`
- Test local wheel installation
- Publish to TestPyPI
- Test TestPyPI installation
- Create a Git tag
- Publish to real PyPI
- Test PyPI installation
- Create a GitHub release