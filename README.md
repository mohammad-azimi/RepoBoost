# RepoBoost

![CI](https://github.com/mohammad-azimi/RepoBoost/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![RepoBoost](https://img.shields.io/badge/RepoBoost-A%20%7C%20100%25-brightgreen)

RepoBoost is a command-line tool that audits a GitHub repository and suggests practical improvements for better open-source presentation.

It checks whether a project has the basic things visitors expect before they star, use, or contribute to a repository.

![RepoBoost demo](docs/repoboost-demo.svg)

## Features

- Scores a repository from 0 to 100
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

## Installation

For local development:

```bash
git clone https://github.com/mohammad-azimi/RepoBoost.git
cd RepoBoost
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

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

Show more improvement priorities:

```bash
repoboost doctor . --limit 5
```

Suggest GitHub topics:

```bash
repoboost topics .
```

Show more topic suggestions:

```bash
repoboost topics . --limit 15
```

Print topic suggestions as JSON:

```bash
repoboost topics . --json
```

Inspect project type, languages, frameworks, and tools:

```bash
repoboost inspect .
```

Print project inspection as JSON:

```bash
repoboost inspect . --json
```

Get project-specific recommendations:

```bash
repoboost recommend .
```

Print recommendations as JSON:

```bash
repoboost recommend . --json
```

Generate a README badge:

```bash
repoboost badge .
```

Print badge data as JSON:

```bash
repoboost badge . --json
```

Generate a GitHub Actions workflow:

```bash
repoboost ci .
```

Save the workflow to a file:

```bash
repoboost ci . --output .github/workflows/repoboost.yml
```

Generate a workflow with a custom required score:

```bash
repoboost ci . --fail-under 90
```

Get JSON output in the terminal:

```bash
repoboost scan . --json
```

Save the scan report to a JSON file:

```bash
repoboost scan . --output repoboost-report.json
```

Print JSON and save the same report to a file:

```bash
repoboost scan . --json --output repoboost-report.json
```

Fail if the repository score is below a required threshold:

```bash
repoboost scan . --fail-under 80
```

This is useful for CI pipelines where you want to prevent poorly documented repositories from passing quality checks.

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

## Doctor Mode Example

```text
RepoBoost Doctor
Score: 54/100 — Grade D

Top improvement priorities:

1. README
   Status: Missing
   Impact: 18 points
   Problem: No README file found.
   Fix: Add a README.md with a short pitch, features, installation, usage, screenshots, and roadmap.

2. License
   Status: Missing
   Impact: 12 points
   Problem: No license file found.
   Fix: Add a LICENSE file so other developers know how they can use the project.
```

## Topics Example

```text
Suggested GitHub topics

python
cli
developer-tools
github
open-source
repository-audit
documentation
```

## Inspect Example

```text
Project inspection

Project types: cli, developer-tool, repository-tool
Languages: python
Package managers: pip
Frameworks: typer, rich, pytest
Tools: github-actions, pytest
```

## Recommendations Example

```text
Recommended next steps

high    distribution    Publish the CLI package to PyPI
medium  code-quality    Add Ruff linting
medium  automation      Add a GitHub Actions usage example
low     code-quality    Add pre-commit hooks
```

## Badge Example

```markdown
![RepoBoost](https://img.shields.io/badge/RepoBoost-A%20%7C%20100%25-brightgreen)
```

## CI Workflow Example

```yaml
name: RepoBoost

on:
  push:
    branches:
      - main
      - master
  pull_request:

jobs:
  repoboost:
    name: Run RepoBoost
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install RepoBoost
        run: |
          python -m pip install --upgrade pip
          pip install repoboost

      - name: Run RepoBoost scan
        run: repoboost scan . --fail-under 80
```

## JSON Report Example

```json
{
  "path": "G:\\Projects\\RepoBoost",
  "score": 100,
  "max_score": 100,
  "percentage": 100.0,
  "grade": "A",
  "checks": []
}
```

## Why RepoBoost?

Many repositories contain useful code, but visitors leave because the project is not presented clearly.

RepoBoost helps developers improve the first impression of their repositories by checking the details that make a project easier to trust, understand, and share.

## Development

Install the project in editable mode:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Run RepoBoost on itself:

```bash
repoboost scan .
```

Run doctor mode:

```bash
repoboost doctor .
```

Suggest GitHub topics:

```bash
repoboost topics .
```

Inspect project profile:

```bash
repoboost inspect .
```

Get project recommendations:

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

Save a report file:

```bash
repoboost scan . --output repoboost-report.json
```

Run RepoBoost with a required score threshold:

```bash
repoboost scan . --fail-under 90
```

## Roadmap

- Add automatic README section generation
- Add smarter GitHub topic suggestions
- Add portfolio-readiness score
- Publish package to PyPI

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

MIT