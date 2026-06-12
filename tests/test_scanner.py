from repoboost.scanner import scan_project


def test_scan_empty_project(tmp_path):
    report = scan_project(tmp_path)

    assert report.max_score == 100
    assert report.score < 50
    assert report.grade in {"D", "F"}
    assert any(not check.passed for check in report.checks)


def test_scan_good_project(tmp_path):
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

    (tmp_path / "LICENSE").write_text("MIT License", encoding="utf-8")
    (tmp_path / ".gitignore").write_text(".venv/\n__pycache__/\n", encoding="utf-8")
    (tmp_path / "CONTRIBUTING.md").write_text("# Contributing\n", encoding="utf-8")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_demo.py").write_text(
        "def test_demo():\n    assert True\n",
        encoding="utf-8",
    )

    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "ci.yml").write_text("name: CI\n", encoding="utf-8")

    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "screenshot.png").write_bytes(b"fake image content")

    report = scan_project(tmp_path)

    assert report.max_score == 100
    assert report.score >= 90
    assert report.grade in {"A", "B"}