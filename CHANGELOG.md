# Changelog

All notable changes to RepoBoost will be documented in this file.

## 0.1.1 - Configurable Scoring and Smarter Recommendations

### Added

- Added `.repoboost.toml` support for project-specific scoring
- Added `repoboost init-config` command
- Added custom check weights
- Added disabled checks support
- Added scoring profile display in scan reports
- Added `--config` support for scan, doctor, recommend, and badge commands
- Added smarter recommendations with score impact information
- Added configuration-aware recommendations
- Added tests for configurable scoring

### Changed

- Updated package version to `0.1.1`
- Improved recommendation wording for Python CLI projects
- Improved repository recommendations for package distribution and documentation
- Updated documentation to explain configurable scoring

## 0.1.0 - Initial PyPI Release

RepoBoost is now available on PyPI.

Install it with:

```bash
pip install repoboost
```

### Added

- Repository scoring from 0 to 100
- Grade system from A to F
- README, license, .gitignore, tests, and CI checks
- Installation and usage section detection
- Screenshot, badge, and demo link detection
- `scan` command for full repository audits
- `doctor` command for improvement priorities
- `topics` command for GitHub topic suggestions
- `inspect` command for project type and tool detection
- `recommend` command for project-specific suggestions
- `badge` command for generating a RepoBoost README badge
- `ci` command for generating a GitHub Actions workflow
- JSON output support
- Report saving with `--output`
- CI threshold support with `--fail-under`
- GitHub Actions workflows for tests, package checks, TestPyPI publishing, and PyPI publishing
- Release documentation
- TestPyPI validation
- PyPI release workflow

### Verified

- Local tests pass
- Local package build works
- Twine package metadata check passes
- TestPyPI installation works
- PyPI installation works
- `repoboost --version` returns `RepoBoost 0.1.0`