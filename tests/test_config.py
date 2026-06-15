from typer.testing import CliRunner

from repoboost.cli import app
from repoboost.config import generate_config_template, load_repoboost_config
from repoboost.scanner import scan_project


runner = CliRunner()


def test_generate_config_template_contains_weights():
    template = generate_config_template()

    assert 'profile = "python-cli"' in template
    assert "[weights]" in template
    assert "readme = 18" in template
    assert "ci = 6" in template


def test_load_repoboost_config_reads_custom_weights(tmp_path):
    config_file = tmp_path / ".repoboost.toml"
    config_file.write_text(
        """
profile = "custom"
fail_under = 75
disabled_checks = ["demo_link", "badges"]

[weights]
readme = 60
license = 40
""",
        encoding="utf-8",
    )

    config = load_repoboost_config(tmp_path)

    assert config.profile == "custom"
    assert config.fail_under == 75
    assert config.weights["readme"] == 60
    assert config.weights["license"] == 40
    assert "demo_link" in config.disabled_checks
    assert "badges" in config.disabled_checks


def test_scan_project_uses_custom_scoring_config(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n", encoding="utf-8")

    config_file = tmp_path / ".repoboost.toml"
    config_file.write_text(
        """
profile = "custom"
disabled_checks = [
  "gitignore",
  "installation",
  "usage",
  "screenshots",
  "demo_link",
  "badges",
  "contributing",
  "tests",
  "ci"
]

[weights]
readme = 60
license = 40
""",
        encoding="utf-8",
    )

    report = scan_project(tmp_path)

    assert report.profile == "custom"
    assert report.score == 60
    assert report.max_score == 100
    assert report.percentage == 60.0
    assert report.grade == "C"


def test_cli_init_config_creates_config_file(tmp_path):
    result = runner.invoke(
        app,
        ["init-config", str(tmp_path)],
    )

    config_file = tmp_path / ".repoboost.toml"

    assert result.exit_code == 0
    assert config_file.exists()
    assert "RepoBoost config created" in result.output
    assert "[weights]" in config_file.read_text(encoding="utf-8")


def test_cli_scan_reports_config_profile(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n", encoding="utf-8")

    config_file = tmp_path / ".repoboost.toml"
    config_file.write_text(
        """
profile = "docs-only"
disabled_checks = [
  "license",
  "gitignore",
  "installation",
  "usage",
  "screenshots",
  "demo_link",
  "badges",
  "contributing",
  "tests",
  "ci"
]

[weights]
readme = 100
""",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["scan", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "Profile: docs-only" in result.output
    assert "RepoBoost Score: 100/100" in result.output