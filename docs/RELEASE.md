# Release Checklist

This document describes how to prepare and publish RepoBoost releases.

RepoBoost is available on PyPI:

```bash
pip install repoboost
```

## 1. Check repository status

```bash
git status
```

Make sure the working tree is clean before building a release.

## 2. Update version

Update the version in:

```text
pyproject.toml
src/repoboost/__init__.py
```

For example:

```text
0.1.0 -> 0.1.1
```

## 3. Update changelog

Update:

```text
CHANGELOG.md
```

Add a new section for the release version.

## 4. Run tests

```bash
pytest
```

Expected result for the current version:

```text
29 passed
```

## 5. Run RepoBoost on itself

```bash
repoboost scan . --fail-under 90
repoboost doctor .
repoboost inspect .
repoboost topics .
repoboost recommend .
repoboost badge .
```

## 6. Build the package

```bash
python -m build
```

This should create a `dist/` directory with files similar to:

```text
repoboost-0.1.0-py3-none-any.whl
repoboost-0.1.0.tar.gz
```

## 7. Check package metadata

```bash
python -m twine check dist/*
```

Expected result:

```text
PASSED
```

## 8. Test install from wheel locally

On Windows:

```bash
pip install --force-reinstall dist\repoboost-0.1.0-py3-none-any.whl
repoboost --version
repoboost scan .
```

Expected result for the current version:

```text
RepoBoost 0.1.0
```

## 9. Restore editable install for development

After testing the wheel, return to editable development mode:

```bash
pip install -e ".[dev]"
```

## 10. Publish to TestPyPI first

Before publishing to the real PyPI index, publish to TestPyPI.

Read:

```text
docs/TESTPYPI.md
```

Then run the manual GitHub Actions workflow:

```text
Actions -> Publish to TestPyPI -> Run workflow
```

## 11. Test installation from TestPyPI

After the TestPyPI workflow succeeds, test installation in a clean environment:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ repoboost
repoboost --version
repoboost scan .
```

Expected result for the current version:

```text
RepoBoost 0.1.0
```

## 12. Publish to PyPI

Only publish to PyPI after TestPyPI works correctly.

Read:

```text
docs/PYPI.md
```

Then run the manual GitHub Actions workflow:

```text
Actions -> Publish to PyPI -> Run workflow
```

## 13. Test installation from PyPI

After the PyPI workflow succeeds, test installation in a clean environment:

```bash
pip install repoboost
repoboost --version
repoboost scan .
```

Expected result for the current version:

```text
RepoBoost 0.1.0
```

## 14. Create GitHub release

After publishing to PyPI, create a GitHub release with:

```text
Tag: v0.1.0
Title: RepoBoost 0.1.0
```

Include the main changes from `CHANGELOG.md`.

## 15. Publishing order

Recommended publishing order:

1. Local tests
2. Local build
3. Local wheel install test
4. TestPyPI
5. TestPyPI installation test
6. Real PyPI
7. PyPI installation test
8. GitHub release
9. LinkedIn/GitHub announcement post

## 16. Version checklist

Before publishing a new version:

- Update `version` in `pyproject.toml`
- Update `__version__` in `src/repoboost/__init__.py`
- Update `CHANGELOG.md`
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