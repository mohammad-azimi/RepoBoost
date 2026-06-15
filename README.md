# RepoBoost

![CI](https://github.com/mohammad-azimi/RepoBoost/actions/workflows/ci.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/repoboost.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![RepoBoost](https://img.shields.io/badge/RepoBoost-A%20%7C%20100%25-brightgreen)

RepoBoost is a command-line tool that audits a GitHub repository and suggests practical improvements for better open-source presentation.

It checks whether a project has the basic things visitors expect before they star, use, or contribute to a repository.

![RepoBoost demo](docs/repoboost-demo.svg)

## Installation

Install RepoBoost from PyPI:

```bash
pip install repoboost
```

Check that it works:

```bash
repoboost --version
```

Expected output:

```text
RepoBoost 0.1.1
```

## Features

- Scores a repository from 0 to 100
- Gives a grade from A to F
- Supports configurable scoring with `.repoboost.toml`
- Checks for README, license, .gitignore, tests, and CI
- Detects installation and usage sections
- Detects screenshots, badges, and demo links
- Gives practical next-step suggestions
- Shows top improvement priorities with doctor mode
- Suggests useful GitHub topics
- Detects project type, languages, frameworks, and tools
- Recommends project-specific next steps
- Generates a RepoBoost README badge
- Generates a GitHub Actions workflow for CI usage
- Saves scan reports as JSON files
- Supports JSON output for automation
- Supports score thresholds for CI usage

## Usage

Scan the current repository:

```bash
repoboost scan .
```

Scan another local repository:

```bash
repoboost scan path/to/project
```

Show only the most important improvement priorities:

```bash
repoboost doctor .
```

Suggest GitHub topics:

```bash
repoboost topics .
```

Inspect project type, languages, frameworks, and tools:

```bash
repoboost inspect .
```

Get project-specific recommendations:

```bash
repoboost recommend .
```

Generate a README badge:

```bash
repoboost badge .
```

Generate a GitHub Actions workflow:

```bash
repoboost ci .
```

Generate a configuration file:

```bash
repoboost init-config .
```

Use a custom configuration file:

```bash
repoboost scan . --config .repoboost.toml
```

Get JSON output:

```bash
repoboost scan . --json
```

Save the scan report to a JSON file:

```bash
repoboost scan . --output repoboost-report.json
```

Fail if the repository score is below a required threshold:

```bash
repoboost scan . --fail-under 80
```

## Configurable Scoring

RepoBoost can use a `.repoboost.toml` file to customize scoring for different repository types.

Create a default config file:

```bash
repoboost init-config .
```

Example `.repoboost.toml`:

```toml
profile = "python-cli"
fail_under = 90
disabled_checks = []

[weights]
readme = 18
license = 12
gitignore = 8
installation = 10
usage = 10
screenshots = 10
demo_link = 8
badges = 6
contributing = 6
tests = 6
ci = 6

[recommendations]
focus = [
  "documentation",
  "automation",
  "distribution",
  "code-quality"
]
```

You can increase or decrease the weight of each check depending on the type of project.

For example, a Python CLI tool may prioritize installation, usage, tests, and CI. A visual machine learning project may prioritize screenshots, examples, evaluation results, and documentation.

## Example Output

```text
RepoBoost Score: 72/100 — Grade C

MISS  Screenshots or media 0/10   No screenshots or visual media detected.
MISS  Badges               0/6    No README badges detected.
MISS  Contributing guide   0/6    No contributing guide found.
MISS  CI workflow          0/6    No GitHub Actions workflow detected.

Next best improvements:
1. Add a screenshot, GIF, or demo image to make the repository easier to understand quickly.
2. Add small badges for license, tests, or package version after the project title.
3. Add CONTRIBUTING.md if you want other developers to contribute.
```

## Commands

### scan

```bash
repoboost scan .
```

Runs a full repository audit.

Useful options:

```bash
repoboost scan . --json
repoboost scan . --output repoboost-report.json
repoboost scan . --fail-under 90
repoboost scan . --config .repoboost.toml
```

### doctor

```bash
repoboost doctor .
```

Shows the most important missing improvements.

### topics

```bash
repoboost topics .
```

Suggests GitHub topics for the repository.

### inspect

```bash
repoboost inspect .
```

Detects project type, languages, frameworks, tools, and important files.

### recommend

```bash
repoboost recommend .
```

Shows project-specific recommendations.

### badge

```bash
repoboost badge .
```

Generates a Markdown badge for the repository score.

### ci

```bash
repoboost ci .
```

Generates a GitHub Actions workflow for running RepoBoost in CI.

### init-config

```bash
repoboost init-config .
```

Creates a `.repoboost.toml` file for configurable scoring.

## Why RepoBoost?

Many repositories contain useful code, but visitors leave because the project is not presented clearly.

RepoBoost helps developers improve the first impression of their repositories by checking the details that make a project easier to trust, understand, and share.

## Development

Clone the repository:

```bash
git clone https://github.com/mohammad-azimi/RepoBoost.git
cd RepoBoost
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install the project in editable mode:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Build the package locally:

```bash
python -m build
python -m twine check dist/*
```

Run RepoBoost on itself:

```bash
repoboost scan . --fail-under 90
```

## Release

RepoBoost is available on PyPI:

```bash
pip install repoboost
```

Release notes are available in:

```text
CHANGELOG.md
```

Release documentation is available in:

```text
docs/RELEASE.md
docs/TESTPYPI.md
docs/PYPI.md
```

## Roadmap

- Add automatic README section generation
- Add smarter GitHub topic suggestions
- Add portfolio-readiness score
- Add more project-type specific recommendations
- Add configurable scoring presets

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

MIT