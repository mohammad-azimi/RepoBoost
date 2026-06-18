from typer.testing import CliRunner

from repoboost.cli import app
from repoboost.reports import generate_markdown_report


runner = CliRunner()


def test_generate_markdown_report_contains_summary(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n\nA small demo repository.", encoding="utf-8")

    markdown_report = generate_markdown_report(tmp_path)

    assert "# RepoBoost Report" in markdown_report.content
    assert "## Summary" in markdown_report.content
    assert "**Score:**" in markdown_report.content
    assert "**Grade:**" in markdown_report.content
    assert "## Audit Results" in markdown_report.content
    assert "## Recommendations" in markdown_report.content


def test_generate_markdown_report_can_hide_passed_checks(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n\nA small demo repository.", encoding="utf-8")

    markdown_report = generate_markdown_report(
        tmp_path,
        include_passed=False,
    )

    audit_section = markdown_report.content.split("## Recommendations")[0]

    assert "# RepoBoost Report" in markdown_report.content
    assert "| ✅ PASS | README |" not in audit_section
    assert "| ❌ MISS | License |" in audit_section


def test_cli_report_prints_markdown(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n\nA small demo repository.", encoding="utf-8")

    result = runner.invoke(
        app,
        ["report", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "# RepoBoost Report" in result.output
    assert "## Summary" in result.output


def test_cli_report_writes_output_file(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n\nA small demo repository.", encoding="utf-8")

    output_file = tmp_path / "REPOBOOST_REPORT.md"

    result = runner.invoke(
        app,
        [
            "report",
            str(tmp_path),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    assert "# RepoBoost Report" in output_file.read_text(encoding="utf-8")
    assert "Markdown report created" in result.output