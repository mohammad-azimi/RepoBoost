from repoboost.badges import generate_badge


def test_generate_badge_for_empty_project(tmp_path):
    badge = generate_badge(tmp_path)

    assert badge.label == "RepoBoost"
    assert badge.color == "red"
    assert "RepoBoost" in badge.markdown
    assert "img.shields.io" in badge.url


def test_generate_badge_for_good_project(tmp_path):
    create_good_project(tmp_path)

    badge = generate_badge(tmp_path)

    assert badge.label == "RepoBoost"
    assert badge.message == "A | 100%"
    assert badge.color == "brightgreen"
    assert "A%20%7C%20100%25" in badge.url


def create_good_project(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        """
# Demo Project

![License](https://img.shields.io/badge/license-MIT-blue.svg)

A small demo project.

## Installation

```bash
pip install demo-project
```

## Usage

```bash
demo-project run
```

## Demo

Live demo: https://example.com

## Screenshot

![Screenshot](assets/screenshot.png)
""",
        encoding="utf-8",
    )

    license_file = tmp_path / "LICENSE"
    license_file.write_text("MIT License", encoding="utf-8")

    gitignore_file = tmp_path / ".gitignore"
    gitignore_file.write_text(".venv/\n__pycache__/\n", encoding="utf-8")

    contributing_file = tmp_path / "CONTRIBUTING.md"
    contributing_file.write_text("# Contributing\n", encoding="utf-8")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    test_file = tests_dir / "test_demo.py"
    test_file.write_text(
        "def test_demo():\n    assert True\n",
        encoding="utf-8",
    )

    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    ci_file = workflows_dir / "ci.yml"
    ci_file.write_text("name: CI\n", encoding="utf-8")

    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    screenshot_file = assets_dir / "screenshot.png"
    screenshot_file.write_bytes(b"fake image content")