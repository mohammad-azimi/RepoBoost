import json

from typer.testing import CliRunner

from repoboost.cli import app


runner = CliRunner()


def test_cli_scan_fails_below_threshold(tmp_path):
    result = runner.invoke(
        app,
        ["scan", str(tmp_path), "--fail-under", "1"],
    )

    assert result.exit_code == 1
    assert "below the required threshold" in result.output


def test_cli_scan_passes_with_good_project(tmp_path):
    create_good_project(tmp_path)

    result = runner.invoke(
        app,
        ["scan", str(tmp_path), "--fail-under", "90"],
    )

    assert result.exit_code == 0
    assert "RepoBoost Score" in result.output


def test_cli_scan_saves_json_report(tmp_path):
    create_good_project(tmp_path)
    output_file = tmp_path / "repoboost-report.json"

    result = runner.invoke(
        app,
        ["scan", str(tmp_path), "--output", str(output_file)],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    assert "Saved report" in result.output

    report_data = json.loads(output_file.read_text(encoding="utf-8"))

    assert report_data["score"] == 100
    assert report_data["max_score"] == 100
    assert report_data["grade"] == "A"
    assert report_data["percentage"] == 100.0


def test_cli_scan_prints_json_and_saves_report(tmp_path):
    create_good_project(tmp_path)
    output_file = tmp_path / "report.json"

    result = runner.invoke(
        app,
        ["scan", str(tmp_path), "--json", "--output", str(output_file)],
    )

    assert result.exit_code == 0
    assert output_file.exists()

    printed_data = json.loads(result.output)
    saved_data = json.loads(output_file.read_text(encoding="utf-8"))

    assert printed_data["score"] == saved_data["score"]
    assert printed_data["grade"] == saved_data["grade"]


def test_cli_doctor_shows_top_improvements_for_empty_project(tmp_path):
    result = runner.invoke(
        app,
        ["doctor", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "RepoBoost Doctor" in result.output
    assert "Top improvement priorities" in result.output
    assert "README" in result.output


def test_cli_doctor_reports_ready_project(tmp_path):
    create_good_project(tmp_path)

    result = runner.invoke(
        app,
        ["doctor", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "No missing improvements found" in result.output


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