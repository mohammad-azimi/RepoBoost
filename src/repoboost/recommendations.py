from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from repoboost.config import load_repoboost_config
from repoboost.project import ProjectProfile, inspect_project
from repoboost.scanner import ScanReport, scan_project
from repoboost.topics import suggest_topics


@dataclass
class Recommendation:
    title: str
    priority: str
    category: str
    reason: str
    action: str

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "priority": self.priority,
            "category": self.category,
            "reason": self.reason,
            "action": self.action,
        }


def generate_recommendations(
    path: str | Path,
    limit: int | None = None,
    config_path: str | Path | None = None,
) -> list[Recommendation]:
    root = Path(path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    config = load_repoboost_config(root, config_path=config_path)
    report = scan_project(root, config_path=config_path)
    profile = inspect_project(root)

    recommendations: list[Recommendation] = []

    recommendations.extend(_recommend_from_scan(report))
    recommendations.extend(_recommend_from_project_profile(profile))
    recommendations.extend(_recommend_topics(root))
    recommendations.extend(_recommend_config_usage(root, report))

    recommendations = _deduplicate_recommendations(recommendations)
    recommendations = _filter_by_focus(recommendations, config.recommendation_focus)
    recommendations = _sort_recommendations(recommendations)

    if limit is not None:
        return recommendations[:limit]

    return recommendations


def _recommend_from_scan(report: ScanReport) -> list[Recommendation]:
    recommendations: list[Recommendation] = []

    for check in report.checks:
        if check.passed:
            continue

        recommendations.append(
            Recommendation(
                title=f"Fix missing {check.name}",
                priority=_priority_from_check(check.max_score, check.severity),
                category="presentation",
                reason=f"{check.message} This improvement is worth up to {check.max_score} points.",
                action=check.suggestion,
            )
        )

    return recommendations


def _recommend_from_project_profile(profile: ProjectProfile) -> list[Recommendation]:
    recommendations: list[Recommendation] = []

    if "python" in profile.languages and "cli" in profile.project_types:
        recommendations.append(
            Recommendation(
                title="Keep PyPI installation visible near the top",
                priority="high",
                category="distribution",
                reason="This looks like a Python CLI package, so the fastest install command should be immediately visible.",
                action='Keep "pip install repoboost" near the top of the README and in release notes.',
            )
        )

    if "cli" in profile.project_types:
        recommendations.append(
            Recommendation(
                title="Add more real command examples",
                priority="medium",
                category="documentation",
                reason="CLI tools are easier to adopt when users can copy practical commands directly.",
                action="Add examples for scan, doctor, topics, inspect, recommend, badge, ci, JSON output, and custom config usage.",
            )
        )

    if "repository-tool" in profile.project_types:
        recommendations.append(
            Recommendation(
                title="Add before/after repository examples",
                priority="medium",
                category="documentation",
                reason="Repository audit tools become more convincing when users can see the improvement before and after applying suggestions.",
                action="Add one small demo repository example with a low score, then show how the score improves after fixes.",
            )
        )

    if "python" in profile.languages and "ruff" not in profile.tools:
        recommendations.append(
            Recommendation(
                title="Add Ruff linting",
                priority="medium",
                category="code-quality",
                reason="Ruff can improve code style and catch common Python issues quickly.",
                action="Add Ruff as a development dependency and document the command for running it.",
            )
        )

    if "python" in profile.languages and "pre-commit" not in profile.tools:
        recommendations.append(
            Recommendation(
                title="Add pre-commit hooks",
                priority="low",
                category="code-quality",
                reason="Pre-commit hooks help keep formatting and checks consistent before every commit.",
                action="Add a .pre-commit-config.yaml file with useful Python checks.",
            )
        )

    if "machine-learning" in profile.project_types:
        recommendations.append(
            Recommendation(
                title="Add evaluation results",
                priority="high",
                category="machine-learning",
                reason="Machine learning projects need clear metrics so visitors can understand model quality.",
                action="Add a results section with metrics, dataset notes, and reproducible evaluation commands.",
            )
        )

    if "reinforcement-learning" in profile.project_types:
        recommendations.append(
            Recommendation(
                title="Add training and evaluation curves",
                priority="high",
                category="reinforcement-learning",
                reason="Reinforcement learning projects are easier to understand when learning progress is visible.",
                action="Add reward curves, evaluation tables, and a short explanation of the environment.",
            )
        )

    if "computer-vision" in profile.project_types:
        recommendations.append(
            Recommendation(
                title="Add visual examples",
                priority="high",
                category="computer-vision",
                reason="Computer vision projects need visual outputs to show what the model or pipeline does.",
                action="Add before/after images, predictions, or sample outputs to the README.",
            )
        )

    return recommendations


def _recommend_topics(root: Path) -> list[Recommendation]:
    suggestions = suggest_topics(root)

    if not suggestions:
        return []

    topic_list = ", ".join(suggestion.topic for suggestion in suggestions[:10])

    return [
        Recommendation(
            title="Add GitHub topics to improve discoverability",
            priority="medium",
            category="discoverability",
            reason="GitHub topics help people find the repository through search and topic pages.",
            action=f"Use these suggested topics: {topic_list}",
        )
    ]


def _recommend_config_usage(root: Path, report: ScanReport) -> list[Recommendation]:
    if report.config_path:
        return [
            Recommendation(
                title="Review custom scoring configuration over time",
                priority="low",
                category="configuration",
                reason=f"This repository uses the '{report.profile}' scoring profile from {report.config_path}.",
                action="Keep the weights aligned with the repository type as the project grows.",
            )
        ]

    config_file = root / ".repoboost.toml"

    if config_file.exists():
        return []

    return [
        Recommendation(
            title="Add a RepoBoost config for project-specific scoring",
            priority="low",
            category="configuration",
            reason="Different repository types may need different scoring priorities.",
            action='Run "repoboost init-config ." and adjust the weights in .repoboost.toml.',
        )
    ]


def _filter_by_focus(
    recommendations: list[Recommendation],
    focus_categories: list[str],
) -> list[Recommendation]:
    if not focus_categories:
        return recommendations

    allowed_categories = {
        category.strip().lower()
        for category in focus_categories
    }

    always_keep_categories = {
        "presentation",
        "configuration",
    }

    filtered: list[Recommendation] = []

    for recommendation in recommendations:
        category = recommendation.category.strip().lower()

        if category in allowed_categories or category in always_keep_categories:
            filtered.append(recommendation)

    return filtered


def _priority_from_check(max_score: int, severity: str) -> str:
    if severity == "high" or max_score >= 10:
        return "high"

    if severity == "medium" or max_score >= 6:
        return "medium"

    return "low"


def _deduplicate_recommendations(recommendations: list[Recommendation]) -> list[Recommendation]:
    seen: set[str] = set()
    unique: list[Recommendation] = []

    for recommendation in recommendations:
        key = recommendation.title.strip().lower()

        if key in seen:
            continue

        seen.add(key)
        unique.append(recommendation)

    return unique


def _sort_recommendations(recommendations: list[Recommendation]) -> list[Recommendation]:
    priority_weight = {
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    return sorted(
        recommendations,
        key=lambda recommendation: (
            priority_weight.get(recommendation.priority, 0),
            recommendation.category,
            recommendation.title,
        ),
        reverse=True,
    )