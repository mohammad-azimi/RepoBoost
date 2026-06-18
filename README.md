# RepoBoost

![CI](https://github.com/mohammad-azimi/RepoBoost/actions/workflows/ci.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/repoboost?label=PyPI\&cacheSeconds=300)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![RepoBoost](https://img.shields.io/badge/RepoBoost-A%20%7C%20100%25-brightgreen)

RepoBoost is a Python command-line tool that audits GitHub repositories and suggests practical improvements for better open-source presentation.

It helps developers make their repositories easier to understand, trust, install, and share.

![RepoBoost demo](docs/repoboost-demo.svg)

## What RepoBoost Checks

RepoBoost looks for the details that make a repository more useful for visitors, recruiters, contributors, and other developers.

It checks for:

* README quality
* License file
* `.gitignore`
* Installation instructions
* Usage examples
* Screenshots or visual media
* Demo or live links
* README badges
* Contributing guide
* Tests
* GitHub Actions workflow
* Repository score and grade

## Installation

Install RepoBoost from PyPI:

```bash
pip install repoboost
```

Verify the installation:

```bash
repoboost --version
```

Expected output:

```text
RepoBoost 0.1.2
```

## Quick Start

Scan the current repository:

```bash
repoboost scan .
```

Show the most important improvement priorities:

```bash
repoboost doctor .
```

Get project-specific recommendations:

```bash
repoboost recommend .
```

Generate a Markdown report:

```bash
repoboost report . --output REPOBOOST_REPORT.md
```

Create a configurable scoring file:

```bash
repoboost init-config .
```

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

## Main Features

* Scores a repository from 0 to 100
* Gives a grade from A to F
* Supports configurable scoring with `.repoboost.toml`
* Supports custom check weights
* Supports disabled checks
* Shows the active scoring profile in scan reports
* Detects README, license, `.gitignore`, tests, and CI
* Detects installation and usage sections
* Detects screenshots, badges, and demo links
* Gives practical next-step suggestions
* Shows top improvement priorities with doctor mode
* Suggests useful GitHub topics
* Detects project type, languages, frameworks, and tools
* Recommends project-specific next steps
* Generates Markdown audit reports
* Generates a RepoBoost README badge
* Generates a GitHub Actions workflow for CI usage
* Saves scan reports as JSON files
* Supports JSON output for automation
* Supports score thresholds for CI usage

## Commands

### `scan`

Run a full repository audit:

```bash
repoboost scan .
```

Scan another local repository:

```bash
repoboost scan path/to/project
```

Useful options:

```bash
repoboost scan . --json
repoboost scan . --output repoboost-report.json
repoboost scan . --fail-under 90
repoboost scan . --config .repoboost.toml
```

### `doctor`

Show the most important missing improvements:

```bash
repoboost doctor .
```

Use a custom config file:

```bash
repoboost doctor . --config .repoboost.toml
```

### `recommend`

Show project-specific recommendations:

```bash
repoboost recommend .
```

Print recommendations as JSON:

```bash
repoboost recommend . --json
```

Use a custom config file:

```bash
repoboost recommend . --config .repoboost.toml
```

### `report`

Generate a Markdown report from the repository audit:

```bash
repoboost report .
```

Save the report to a file:

```bash
repoboost report . --output REPOBOOST_REPORT.md
```

Show only missing checks in the audit table:

```bash
repoboost report . --missing-only
```

Use a custom config file:

```bash
repoboost report . --config .repoboost.toml
```

### `init-config`

Create a `.repoboost.toml` file:

```bash
repoboost init-config .
```

Overwrite an existing config file:

```bash
repoboost init-config . --force
```

Create a config file with a custom profile name:

```bash
repoboost init-config . --profile python-cli
```

### `topics`

Suggest useful GitHub topics:

```bash
repoboost topics .
```

Print topic suggestions as JSON:

```bash
repoboost topics . --json
```

### `inspect`

Detect project type, languages, frameworks, tools, and important files:

```bash
repoboost inspect .
```

Print the detected project profile as JSON:

```bash
repoboost inspect . --json
```

### `badge`

Generate a Markdown badge based on the repository score:

```bash
repoboost badge .
```

Example badge output:

```markdown
![RepoBoost](https://img.shields.io/badge/RepoBoost-A%20%7C%20100%25-brightgreen)
```

### `ci`

Generate a GitHub Actions workflow for running RepoBoost in CI:

```bash
repoboost ci .
```

Save the workflow to a file:

```bash
repoboost ci . --output .github/workflows/repoboost.yml
```

Set a required score threshold:

```bash
repoboost ci . --fail-under 80
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

You can adjust the score weight of each check depending on the type of project.

For example:

* A Python CLI tool may prioritize installation, usage examples, tests, and CI.
* A web app may prioritize screenshots, demo links, deployment, and usage instructions.
* A machine learning project may prioritize results, visual examples, reproducibility, and documentation.

## Markdown Reports

RepoBoost can generate a Markdown report from the repository audit.

Print a report in the terminal:

```bash
repoboost report .
```

Save a report to a file:

```bash
repoboost report . --output REPOBOOST_REPORT.md
```

Generate a report with only missing checks:

```bash
repoboost report . --missing-only
```

A generated report includes:

* repository summary
* score and grade
* active scoring profile
* audit results table
* recommendation table
* next-step suggestions

This is useful for:

* project reviews
* portfolio project tracking
* repository improvement plans
* sharing audit results with teammates
* documenting before-and-after improvements

## JSON Output

RepoBoost supports JSON output for automation and CI workflows.

Example:

```bash
repoboost scan . --json
```

Save the result to a file:

```bash
repoboost scan . --output repoboost-report.json
```

This can be useful for:

* CI checks
* dashboards
* automated repository audits
* portfolio project tracking

## CI Usage

RepoBoost can fail a command if the score is below a required threshold:

```bash
repoboost scan . --fail-under 80
```

This is useful when you want to keep repository presentation quality above a minimum score.

You can also generate a GitHub Actions workflow:

```bash
repoboost ci . --output .github/workflows/repoboost.yml
```

## Why RepoBoost?

Many repositories contain useful code, but visitors may leave quickly if the project is not presented clearly.

A strong repository should answer these questions quickly:

* What does this project do?
* Who is it for?
* How do I install it?
* How do I use it?
* Can I trust it?
* Is it maintained?
* Are there examples, tests, or screenshots?

RepoBoost helps developers improve these details with clear checks and practical suggestions.

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

Generate a Markdown report:

```bash
repoboost report . --output REPOBOOST_REPORT.md
```

## Release History

### 0.1.2

Markdown report generation.

Added:

* `repoboost report` command
* Markdown audit report generation
* `--output` support for saving reports
* `--missing-only` option for reports
* recommendation tables inside generated reports
* next-step suggestions inside generated reports
* tests for Markdown report generation

### 0.1.1

Configurable scoring and smarter recommendations.

Added:

* `.repoboost.toml` support
* `repoboost init-config`
* custom check weights
* disabled checks
* scoring profile display
* `--config` support for scan, doctor, recommend, and badge
* configuration-aware recommendations
* tests for configurable scoring

### 0.1.0

Initial PyPI release.

Added:

* repository scoring
* scan command
* doctor command
* topics command
* inspect command
* recommend command
* badge command
* CI workflow generator
* JSON output
* report saving
* score thresholds

Full release notes are available in:

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

* Add automatic README section generation
* Add configurable scoring presets
* Add more project-type specific recommendations
* Add portfolio-readiness score
* Add Markdown report export
* Add repository comparison mode
* Add optional auto-fix helpers for common missing files

## Contributing

Contributions are welcome.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

This project is licensed under the MIT License.

You are free to use, modify, and distribute this project, as long as the original license and copyright notice are included.

See the [LICENSE](LICENSE) file for more details.
