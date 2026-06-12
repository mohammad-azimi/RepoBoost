# Contributing to RepoBoost

Thank you for your interest in contributing to RepoBoost.

RepoBoost is a small developer tool that helps improve the presentation quality of GitHub repositories.

## How to contribute

You can contribute by:

- Reporting bugs
- Suggesting new repository checks
- Improving the README
- Adding tests
- Improving the command-line output
- Adding support for more project types

## Local setup

Clone the repository:

```bash
git clone https://github.com/mohammad-azimi/RepoBoost.git
cd RepoBoost
```

Create a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -e ".[dev]"
```

Run the tests:

```bash
pytest
```

Run RepoBoost locally:

```bash
repoboost scan .
```

## Pull request checklist

Before opening a pull request, please make sure that:

- The code is easy to read
- The feature has a clear purpose
- Tests pass successfully
- The README is updated if needed
- The command-line output is still clear and useful

## Project direction

RepoBoost should stay simple, practical, and beginner-friendly.

The goal is not only to analyze code quality, but also to help developers make their repositories easier to understand, trust, and share.