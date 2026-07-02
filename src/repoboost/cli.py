from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from repoboost import __version__
from repoboost.badges import generate_badge
from repoboost.ci import CIWorkflow, generate_ci_workflow
from repoboost.config import generate_config_template
from repoboost.presets import list_presets
from repoboost.project import ProjectProfile, inspect_project
from repoboost.recommendations import Recommendation, generate_recommendations
from repoboost.reports import generate_markdown_report
from repoboost.scanner import CheckResult, ScanReport, scan_project
from repoboost.topics import suggest_topics


app = typer.Typer(
    help="RepoBoost audits a repository and suggests practical improvements for better open-source presentation.",
    invoke_without_command=True,
)

console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show RepoBoost version.",
    ),
) -> None:
    if version:
        console.print(f"RepoBoost {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()


@app.command()
def scan(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the repository you want to scan.",
    ),
    config_path: Path | None = typer.Option(
        None,
        "--config",
        help="Path to a custom .repoboost.toml config file.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print the report as JSON.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Save the scan report to a JSON file.",
    ),
    fail_under: int | None = typer.Option(
        None,
        "--fail-under",
        min=0,
        max=100,
        help="Exit with an error if the repository score is below this percentage.",
    ),
) -> None:
    """
    Scan a repository and print a full RepoBoost score report.
    """
    report = scan_project(path, config_path=config_path)

    if output is not None:
        _write_json_report(report, output)

    if json_output:
        console.print_json(data=report.to_dict())
    else:
        _render_report(report)

        if output is not None:
            console.print(f"[green]Saved report to {output}[/green]")

    if fail_under is not None and report.percentage < fail_under:
        console.print(
            f"[bold red]RepoBoost score {report.percentage}% is below the required threshold of {fail_under}%.[/bold red]"
        )
        raise typer.Exit(code=1)


@app.command()
def doctor(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the repository you want to inspect.",
    ),
    config_path: Path | None = typer.Option(
        None,
        "--config",
        help="Path to a custom .repoboost.toml config file.",
    ),
    limit: int = typer.Option(
        3,
        "--limit",
        "-n",
        min=1,
        max=10,
        help="Number of improvement priorities to show.",
    ),
) -> None:
    """
    Show the most important improvement priorities for a repository.
    """
    report = scan_project(path, config_path=config_path)
    missing_checks = _rank_missing_checks(report.checks)

    console.print()
    console.print(
        Panel.fit(
            f"[bold]RepoBoost Doctor[/bold]\n"
            f"Score: {report.score}/{report.max_score} — Grade {report.grade}\n"
            f"Profile: {report.profile}\n"
            f"Path: {report.path}",
            title="Doctor",
            border_style="blue",
        )
    )

    if not missing_checks:
        console.print("[bold green]No missing improvements found. This repository looks ready to share.[/bold green]")
        console.print()
        return

    console.print("[bold]Top improvement priorities:[/bold]")

    for index, check in enumerate(missing_checks[:limit], start=1):
        console.print()
        console.print(f"[bold]{index}. {check.name}[/bold]")
        console.print(f"   Status: [red]Missing[/red]")
        console.print(f"   Impact: {check.max_score} points")
        console.print(f"   Problem: {check.message}")
        console.print(f"   Fix: {check.suggestion}")

    console.print()


@app.command(name="init-config")
def init_config_command(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the repository where .repoboost.toml should be created.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Custom output path for the config file.",
    ),
    profile: str | None = typer.Option(
        None,
        "--profile",
        help="Profile name to write into the generated config file.",
    ),
    preset_name: str = typer.Option(
        "python-cli",
        "--preset",
        help="Built-in scoring preset to use.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite the config file if it already exists.",
    ),
) -> None:
    """
    Create a .repoboost.toml file for configurable scoring.
    """
    output_path = output if output is not None else path / ".repoboost.toml"
    output_path = output_path.resolve()

    if output_path.exists() and not force:
        console.print(
            f"[bold red]Config file already exists: {output_path}[/bold red]\n"
            "Use --force to overwrite it."
        )
        raise typer.Exit(code=1)

    try:
        config_template = generate_config_template(
            profile=profile or preset_name,
            preset_name=preset_name,
        )
    except ValueError as error:
        console.print(f"[bold red]{error}[/bold red]")
        raise typer.Exit(code=1) from error

    _write_text_file(config_template, output_path)

    console.print()
    console.print(
        Panel.fit(
            f"[bold]RepoBoost config created[/bold]\n"
            f"Preset: {preset_name}\n"
            f"Path: {output_path}",
            title="Config",
            border_style="blue",
        )
    )
    console.print()


@app.command(name="presets")
def presets_command(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print built-in presets as JSON.",
    ),
) -> None:
    """
    List built-in scoring presets.
    """
    presets = list_presets()

    if json_output:
        console.print_json(
            data={
                "presets": [
                    preset.to_dict()
                    for preset in presets
                ],
            }
        )
        return

    console.print()
    console.print(
        Panel.fit(
            "[bold]Built-in scoring presets[/bold]\nUse them with: repoboost init-config . --preset <name>",
            title="Presets",
            border_style="blue",
        )
    )

    table = Table(title="Available presets")
    table.add_column("Preset")
    table.add_column("Description")
    table.add_column("Focus")

    for preset in presets:
        table.add_row(
            preset.name,
            preset.description,
            ", ".join(preset.recommendation_focus) or "None",
        )

    console.print(table)
    console.print()


@app.command()
def topics(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the repository you want topic suggestions for.",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        max=20,
        help="Maximum number of topic suggestions to show.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print topic suggestions as JSON.",
    ),
) -> None:
    """
    Suggest useful GitHub topics for a repository.
    """
    suggestions = suggest_topics(path)[:limit]

    if json_output:
        console.print_json(
            data={
                "path": str(path.resolve()),
                "topics": [suggestion.to_dict() for suggestion in suggestions],
            }
        )
        return

    console.print()
    console.print(
        Panel.fit(
            f"[bold]GitHub topic suggestions[/bold]\nPath: {path.resolve()}",
            title="Topics",
            border_style="blue",
        )
    )

    if not suggestions:
        console.print("[yellow]No topic suggestions found.[/yellow]")
        console.print()
        return

    table = Table(title="Suggested GitHub topics")
    table.add_column("Topic")
    table.add_column("Reason")

    for suggestion in suggestions:
        table.add_row(suggestion.topic, suggestion.reason)

    console.print(table)
    console.print()

    topic_line = ", ".join(suggestion.topic for suggestion in suggestions)
    console.print("[bold]Copyable topic list:[/bold]")
    console.print(topic_line)
    console.print()


@app.command(name="inspect")
def inspect_command(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the repository you want to inspect.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print project profile as JSON.",
    ),
) -> None:
    """
    Detect project type, languages, tools, frameworks, and important files.
    """
    profile = inspect_project(path)

    if json_output:
        console.print_json(data=profile.to_dict())
        return

    _render_project_profile(profile)


@app.command()
def recommend(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the repository you want recommendations for.",
    ),
    config_path: Path | None = typer.Option(
        None,
        "--config",
        help="Path to a custom .repoboost.toml config file.",
    ),
    limit: int = typer.Option(
        8,
        "--limit",
        "-n",
        min=1,
        max=20,
        help="Maximum number of recommendations to show.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print recommendations as JSON.",
    ),
) -> None:
    """
    Recommend practical next steps based on repository checks and detected project type.
    """
    recommendations = generate_recommendations(
        path,
        limit=limit,
        config_path=config_path,
    )

    if json_output:
        console.print_json(
            data={
                "path": str(path.resolve()),
                "recommendations": [
                    recommendation.to_dict()
                    for recommendation in recommendations
                ],
            }
        )
        return

    _render_recommendations(path, recommendations)


@app.command()
def report(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the repository you want to generate a Markdown report for.",
    ),
    config_path: Path | None = typer.Option(
        None,
        "--config",
        help="Path to a custom .repoboost.toml config file.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Save the Markdown report to a file.",
    ),
    include_passed: bool = typer.Option(
        True,
        "--include-passed/--missing-only",
        help="Include passed checks in the Markdown report.",
    ),
    recommendation_limit: int = typer.Option(
        8,
        "--recommendation-limit",
        min=1,
        max=20,
        help="Maximum number of recommendations to include.",
    ),
) -> None:
    """
    Generate a Markdown report from the repository audit.
    """
    markdown_report = generate_markdown_report(
        path,
        config_path=config_path,
        include_passed=include_passed,
        recommendation_limit=recommendation_limit,
    )

    if output is not None:
        _write_text_file(markdown_report.content, output)

        console.print()
        console.print(
            Panel.fit(
                f"[bold]Markdown report created[/bold]\nPath: {output.resolve()}",
                title="Report",
                border_style="blue",
            )
        )
        console.print()
        return

    console.print(markdown_report.content)


@app.command()
def badge(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the repository you want a RepoBoost badge for.",
    ),
    config_path: Path | None = typer.Option(
        None,
        "--config",
        help="Path to a custom .repoboost.toml config file.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print badge data as JSON.",
    ),
) -> None:
    """
    Generate a Markdown badge based on the repository RepoBoost score.
    """
    badge_data = generate_badge(path, config_path=config_path)

    if json_output:
        console.print_json(data=badge_data.to_dict())
        return

    console.print()
    console.print(
        Panel.fit(
            "[bold]RepoBoost badge[/bold]\nCopy this Markdown into your README.",
            title="Badge",
            border_style="blue",
        )
    )
    console.print(badge_data.markdown)
    console.print()


@app.command(name="ci")
def ci_command(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the repository you want a CI workflow for.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Save the generated workflow to a YAML file.",
    ),
    fail_under: int = typer.Option(
        80,
        "--fail-under",
        min=0,
        max=100,
        help="Required RepoBoost score for the generated workflow.",
    ),
    python_version: str = typer.Option(
        "3.12",
        "--python-version",
        help="Python version to use in the generated workflow.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print CI workflow data as JSON.",
    ),
) -> None:
    """
    Generate a GitHub Actions workflow for running RepoBoost in CI.
    """
    workflow = generate_ci_workflow(
        fail_under=fail_under,
        python_version=python_version,
    )

    if output is not None:
        _write_text_file(workflow.content, output)

    if json_output:
        console.print_json(data=workflow.to_dict())
        return

    _render_ci_workflow(path, workflow)

    if output is not None:
        console.print(f"[green]Saved workflow to {output}[/green]")

    console.print()


def _render_report(report: ScanReport) -> None:
    title = f"RepoBoost Score: {report.score}/{report.max_score} — Grade {report.grade}"

    if report.percentage == 100:
        summary = "Excellent. This repository passes all RepoBoost checks."
    elif report.percentage >= 75:
        summary = "This repository is already presented well. Improve the remaining items to make it stronger."
    elif report.percentage >= 50:
        summary = "This repository has a good base, but several presentation details need improvement."
    else:
        summary = "This repository needs important presentation improvements before sharing widely."

    config_line = f"\nProfile: {report.profile}"
    if report.config_path:
        config_line += f"\nConfig: {report.config_path}"

    console.print()
    console.print(
        Panel.fit(
            f"[bold]{title}[/bold]\n{summary}\n{config_line}\n\nPath: {report.path}",
            title="RepoBoost",
            border_style="blue",
        )
    )

    table = Table(title="Repository audit")
    table.add_column("Status", justify="center")
    table.add_column("Check")
    table.add_column("Score", justify="right")
    table.add_column("Message")
    table.add_column("Suggestion")

    for check in report.checks:
        status = "[green]PASS[/green]" if check.passed else "[red]MISS[/red]"
        table.add_row(
            status,
            check.name,
            f"{check.score}/{check.max_score}",
            check.message,
            check.suggestion,
        )

    console.print(table)
    console.print()

    missing = [check for check in report.checks if not check.passed]
    if missing:
        console.print("[bold]Next best improvements:[/bold]")
        for index, check in enumerate(missing[:3], start=1):
            console.print(f"{index}. {check.suggestion}")
    else:
        console.print("[bold green]Excellent. No missing checks found.[/bold green]")

    console.print()


def _render_project_profile(profile: ProjectProfile) -> None:
    console.print()
    console.print(
        Panel.fit(
            f"[bold]Project inspection[/bold]\nPath: {profile.path}",
            title="Inspect",
            border_style="blue",
        )
    )

    table = Table(title="Detected project profile")
    table.add_column("Category")
    table.add_column("Detected values")

    table.add_row("Project types", _format_list(profile.project_types))
    table.add_row("Languages", _format_list(profile.languages))
    table.add_row("Package managers", _format_list(profile.package_managers))
    table.add_row("Frameworks", _format_list(profile.frameworks))
    table.add_row("Tools", _format_list(profile.tools))

    console.print(table)

    files_table = Table(title="Important files")
    files_table.add_column("File group")
    files_table.add_column("Status")

    for name, exists in profile.important_files.items():
        status = "[green]Found[/green]" if exists else "[red]Missing[/red]"
        files_table.add_row(name, status)

    console.print(files_table)
    console.print()


def _render_recommendations(path: Path, recommendations: list[Recommendation]) -> None:
    console.print()
    console.print(
        Panel.fit(
            f"[bold]RepoBoost recommendations[/bold]\nPath: {path.resolve()}",
            title="Recommend",
            border_style="blue",
        )
    )

    if not recommendations:
        console.print("[bold green]No recommendations found. This repository looks strong.[/bold green]")
        console.print()
        return

    table = Table(title="Recommended next steps")
    table.add_column("Priority")
    table.add_column("Category")
    table.add_column("Recommendation")
    table.add_column("Action")

    for recommendation in recommendations:
        table.add_row(
            recommendation.priority,
            recommendation.category,
            recommendation.title,
            recommendation.action,
        )

    console.print(table)
    console.print()


def _render_ci_workflow(path: Path, workflow: CIWorkflow) -> None:
    console.print()
    console.print(
        Panel.fit(
            f"[bold]GitHub Actions workflow[/bold]\n"
            f"Path: {path.resolve()}\n"
            f"Required score: {workflow.fail_under}%\n"
            f"Python: {workflow.python_version}",
            title="CI",
            border_style="blue",
        )
    )

    console.print(workflow.content)


def _format_list(items: list[str]) -> str:
    if not items:
        return "None detected"
    return ", ".join(items)


def _write_json_report(report: ScanReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_text_file(content: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def _rank_missing_checks(checks: list[CheckResult]) -> list[CheckResult]:
    severity_weight = {
        "high": 3,
        "medium": 2,
        "low": 1,
        "info": 0,
    }

    missing_checks = [check for check in checks if not check.passed]

    return sorted(
        missing_checks,
        key=lambda check: (
            severity_weight.get(check.severity, 0),
            check.max_score,
            check.name,
        ),
        reverse=True,
    )


if __name__ == "__main__":
    app()