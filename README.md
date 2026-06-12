# RepoBoost

RepoBoost is a command-line tool that audits a GitHub repository and suggests practical improvements for better open-source presentation.

It checks whether a project has the basic things visitors expect before they star, use, or contribute to a repository.

## Features

- Scores a repository from 0 to 100
- Checks for README, license, .gitignore, tests, and CI
- Detects installation and usage sections
- Detects screenshots, badges, and demo links
- Gives practical next-step suggestions
- Supports JSON output for automation

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

Get JSON output:

```bash
repoboost scan . --json
```

## Example Output

```text
RepoBoost Score: 72/100 — Grade C

MISS  License              0/12   No license file found.
PASS  README               18/18  Found README.md.
MISS  Screenshots or media 0/10   No screenshots or visual media detected.

Next best improvements:
1. Add a LICENSE file so other developers know how they can use the project.
2. Add a screenshot, GIF, or demo image to make the repository easier to understand quickly.
3. Add a simple CI workflow that installs dependencies and runs tests.
```

## Why RepoBoost?

Many repositories contain useful code, but visitors leave because the project is not presented clearly.

RepoBoost helps developers improve the first impression of their repositories by checking the details that make a project easier to trust, understand, and share.

## Roadmap

- Add automatic README section generation
- Add GitHub topic suggestions
- Add project type detection
- Add repository badge generation
- Add GitHub Actions integration
- Add portfolio-readiness score

## License

MIT