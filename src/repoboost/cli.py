from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from repoboost import __version__
from repoboost.scanner import scan_project


app = typer.Typer(
    help="RepoBoost audits a repository and suggests practical improvements for better open-source presentation."
)

console = Console()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show RepoBoost version.",
    )
) -> None:
    if version:
        console.print(f"RepoBoost {__version__}")
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
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print the report as JSON.",
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
    Scan a repository and print a RepoBoost score.
    """
    report = scan_project(path)

    if json_output:
        console.print_json(data=report.to_dict())
    else:
        _render_report(report)

    if fail_under is not None and report.percentage < fail_under:
        console.print(
            f"[bold red]RepoBoost score {report.percentage}% is below the required threshold of {fail_under}%.[/bold red]"
        )
        raise typer.Exit(code=1)


def _render_report(report) -> None:
    title = f"RepoBoost Score: {report.score}/{report.max_score} — Grade {report.grade}"

    if report.percentage == 100:
        summary = "Excellent. This repository passes all RepoBoost checks."
    elif report.percentage >= 75:
        summary = "This repository is already presented well. Improve the remaining items to make it stronger."
    elif report.percentage >= 50:
        summary = "This repository has a good base, but several presentation details need improvement."
    else:
        summary = "This repository needs important presentation improvements before sharing widely."

    console.print()
    console.print(
        Panel.fit(
            f"[bold]{title}[/bold]\n{summary}\n\nPath: {report.path}",
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


if __name__ == "__main__":
    app()