from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from repoboost.scanner import ScanReport, scan_project


@dataclass
class Badge:
    label: str
    message: str
    color: str
    url: str
    markdown: str

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "message": self.message,
            "color": self.color,
            "url": self.url,
            "markdown": self.markdown,
        }


def generate_badge(path: str | Path) -> Badge:
    report = scan_project(path)

    label = "RepoBoost"
    message = f"{report.grade} | {int(report.percentage)}%"
    color = _color_from_report(report)
    url = _build_shields_url(label, message, color)
    markdown = f"![{label}]({url})"

    return Badge(
        label=label,
        message=message,
        color=color,
        url=url,
        markdown=markdown,
    )


def _color_from_report(report: ScanReport) -> str:
    if report.percentage >= 90:
        return "brightgreen"
    if report.percentage >= 75:
        return "green"
    if report.percentage >= 60:
        return "yellow"
    if report.percentage >= 40:
        return "orange"
    return "red"


def _build_shields_url(label: str, message: str, color: str) -> str:
    encoded_label = quote(label, safe="")
    encoded_message = quote(message, safe="")
    encoded_color = quote(color, safe="")

    return f"https://img.shields.io/badge/{encoded_label}-{encoded_message}-{encoded_color}"