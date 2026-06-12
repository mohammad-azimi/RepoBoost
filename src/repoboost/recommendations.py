from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from repoboost.project import ProjectProfile, inspect_project
from repoboost.scanner import CheckResult, ScanReport, scan_project
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


def generate_recommendations(path: str | Path, limit: int | None = None) -> list[Recommendation]:
    root = Path(path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    report = scan_project(root)
    profile = inspect_project(root)

    recommendations: list[Recommendation] = []

    recommendations.extend(_recommend_from_scan(report))
    recommendations.extend(_recommend_from_project_profile(profile))
    recommendations.extend(_recommend_topics(root))

    recommendations = _deduplicate_recommendations(recommendations)
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
                priority=_priority_from_severity(check.severity),
                category="presentation",
                reason=check.message,
                action=check.suggestion,
            )
        )

    return recommendations


def _recommend_from_project_profile(profile: ProjectProfile) -> list[Recommendation]:
    recommendations: list[Recommendation] = []

    if "python" in profile.languages and "cli" in profile.project_types:
        recommendations.append(
            Recommendation(
                title="Publish the CLI package to PyPI",
                priority="high",
                category="distribution",
                reason="This looks like a Python command-line tool, so users should be able to install it easily.",
                action='Prepare the package for release and document installation with "pip install repoboost".',
            )
        )

    if "cli" in profile.project_types:
        recommendations.append(
            Recommendation(
                title="Add real command examples for common use cases",
                priority="medium",
                category="documentation",
                reason="CLI tools get adopted faster when users can copy and run useful commands immediately.",
                action="Add examples for scanning a repository, saving a JSON report, using fail-under, and suggesting topics.",
            )
        )

    if "repository-tool" in profile.project_types:
        recommendations.append(
            Recommendation(
                title="Add a GitHub Actions usage example",
                priority="medium",
                category="automation",
                reason="Repository tools are more useful when they can run automatically in CI pipelines.",
                action="Add a README section showing how to run RepoBoost inside a GitHub Actions workflow.",
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

    if "web" in profile.project_types and not profile.important_files.get("docker", False):
        recommendations.append(
            Recommendation(
                title="Add deployment instructions",
                priority="medium",
                category="deployment",
                reason="Web projects are easier to trust when visitors can find a live demo or deployment guide.",
                action="Add a short section explaining how to run or deploy the project.",
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


def _priority_from_severity(severity: str) -> str:
    if severity == "high":
        return "high"
    if severity == "medium":
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