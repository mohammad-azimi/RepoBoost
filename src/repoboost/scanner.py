from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from repoboost.config import RepoBoostConfig, load_repoboost_config


@dataclass
class CheckResult:
    key: str
    name: str
    passed: bool
    score: int
    max_score: int
    severity: str
    message: str
    suggestion: str

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "passed": self.passed,
            "score": self.score,
            "max_score": self.max_score,
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass
class ScanReport:
    path: str
    score: int
    max_score: int
    percentage: float
    grade: str
    checks: list[CheckResult]
    profile: str = "default"
    config_path: str | None = None

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "grade": self.grade,
            "profile": self.profile,
            "config_path": self.config_path,
            "checks": [check.to_dict() for check in self.checks],
        }


@dataclass
class CheckDefinition:
    key: str
    name: str
    default_score: int
    severity: str
    evaluator: Callable[[Path], tuple[bool, str, str]]


def scan_project(
    path: str | Path,
    config_path: str | Path | None = None,
) -> ScanReport:
    root = Path(path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    config = load_repoboost_config(root, config_path=config_path)

    checks = _run_checks(root, config)
    score = sum(check.score for check in checks)
    max_score = sum(check.max_score for check in checks)
    percentage = round((score / max_score) * 100, 2) if max_score else 0.0
    grade = _grade_from_percentage(percentage)

    return ScanReport(
        path=str(root),
        score=score,
        max_score=max_score,
        percentage=percentage,
        grade=grade,
        checks=checks,
        profile=config.profile,
        config_path=config.source_path,
    )


def _run_checks(root: Path, config: RepoBoostConfig) -> list[CheckResult]:
    results: list[CheckResult] = []

    for definition in _check_definitions():
        if definition.key in config.disabled_checks:
            continue

        max_score = config.weights.get(definition.key, definition.default_score)

        if max_score == 0:
            continue

        passed, message, suggestion = definition.evaluator(root)
        score = max_score if passed else 0

        results.append(
            CheckResult(
                key=definition.key,
                name=definition.name,
                passed=passed,
                score=score,
                max_score=max_score,
                severity=definition.severity,
                message=message,
                suggestion=suggestion,
            )
        )

    return results


def _check_definitions() -> list[CheckDefinition]:
    return [
        CheckDefinition(
            key="readme",
            name="README",
            default_score=18,
            severity="high",
            evaluator=_check_readme,
        ),
        CheckDefinition(
            key="license",
            name="License",
            default_score=12,
            severity="high",
            evaluator=_check_license,
        ),
        CheckDefinition(
            key="gitignore",
            name=".gitignore",
            default_score=8,
            severity="medium",
            evaluator=_check_gitignore,
        ),
        CheckDefinition(
            key="installation",
            name="Installation",
            default_score=10,
            severity="high",
            evaluator=_check_installation,
        ),
        CheckDefinition(
            key="usage",
            name="Usage",
            default_score=10,
            severity="high",
            evaluator=_check_usage,
        ),
        CheckDefinition(
            key="screenshots",
            name="Screenshots or media",
            default_score=10,
            severity="medium",
            evaluator=_check_screenshots_or_media,
        ),
        CheckDefinition(
            key="demo_link",
            name="Demo link",
            default_score=8,
            severity="medium",
            evaluator=_check_demo_link,
        ),
        CheckDefinition(
            key="badges",
            name="Badges",
            default_score=6,
            severity="low",
            evaluator=_check_badges,
        ),
        CheckDefinition(
            key="contributing",
            name="Contributing guide",
            default_score=6,
            severity="low",
            evaluator=_check_contributing,
        ),
        CheckDefinition(
            key="tests",
            name="Tests",
            default_score=6,
            severity="medium",
            evaluator=_check_tests,
        ),
        CheckDefinition(
            key="ci",
            name="CI workflow",
            default_score=6,
            severity="medium",
            evaluator=_check_ci_workflow,
        ),
    ]


def _check_readme(root: Path) -> tuple[bool, str, str]:
    if _readme_path(root) is None:
        return (
            False,
            "No README file found.",
            "Add a README.md with a short pitch, features, installation, usage, screenshots, and roadmap.",
        )

    return (
        True,
        "Found README.md.",
        "Keep the first section clear: what it does, who it is for, and how to run it.",
    )


def _check_license(root: Path) -> tuple[bool, str, str]:
    license_files = [
        "LICENSE",
        "LICENSE.md",
        "LICENSE.txt",
        "COPYING",
    ]

    if any((root / filename).exists() for filename in license_files):
        return (
            True,
            "License file found.",
            "MIT is a good default for small developer tools.",
        )

    return (
        False,
        "No license file found.",
        "Add a LICENSE file so other developers know how they can use the project.",
    )


def _check_gitignore(root: Path) -> tuple[bool, str, str]:
    if (root / ".gitignore").exists:
        if (root / ".gitignore").exists():
            return (
                True,
                ".gitignore file found.",
                "Make sure it ignores virtual environments, cache files, build outputs, and secrets.",
            )

    return (
        False,
        "No .gitignore file found.",
        "Add a .gitignore file to avoid uploading cache files, virtual environments, and local settings.",
    )


def _check_installation(root: Path) -> tuple[bool, str, str]:
    readme = _readme_text(root)

    if _contains_any(
        readme,
        [
            "## installation",
            "# installation",
            "pip install",
            "npm install",
            "poetry install",
            "uv pip install",
            "how to install",
        ],
    ):
        return (
            True,
            "Installation instructions detected.",
            "Keep installation short and copy-paste friendly.",
        )

    return (
        False,
        "No clear installation section detected.",
        "Add a section showing the exact command needed to install or run the project.",
    )


def _check_usage(root: Path) -> tuple[bool, str, str]:
    readme = _readme_text(root)

    if _contains_any(
        readme,
        [
            "## usage",
            "# usage",
            "quickstart",
            "quick start",
            "getting started",
            "example",
            "```bash",
            "```cmd",
            "```python",
        ],
    ):
        return (
            True,
            "Usage example detected.",
            "Show the fastest possible example near the top of the README.",
        )

    return (
        False,
        "No clear usage example detected.",
        "Add at least one command or code example that shows the project working.",
    )


def _check_screenshots_or_media(root: Path) -> tuple[bool, str, str]:
    readme = _readme_text(root)

    image_patterns = [
        r"!\[.*?\]\(.*?\)",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        "screenshot",
        "demo image",
    ]

    if any(re.search(pattern, readme, flags=re.IGNORECASE) for pattern in image_patterns):
        return (
            True,
            "Screenshot, image, GIF, or visual media detected.",
            "Use one strong screenshot or GIF near the top of the README.",
        )

    media_directories = [
        root / "assets",
        root / "docs",
        root / "images",
        root / "screenshots",
    ]

    for directory in media_directories:
        if not directory.exists():
            continue

        if any(file.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg"} for file in directory.rglob("*")):
            return (
                True,
                "Screenshot, image, GIF, or visual media detected.",
                "Use one strong screenshot or GIF near the top of the README.",
            )

    return (
        False,
        "No screenshots or visual media detected.",
        "Add a screenshot, GIF, or demo image to make the repository easier to understand quickly.",
    )


def _check_demo_link(root: Path) -> tuple[bool, str, str]:
    readme = _readme_text(root)

    if _contains_any(
        readme,
        [
            "live demo",
            "demo:",
            "try it",
            "preview",
            "https://",
            "http://",
        ],
    ):
        return (
            True,
            "Demo or live link detected.",
            "Put the demo link near the top so visitors can try the project quickly.",
        )

    return (
        False,
        "No clear demo or live link detected.",
        "If the project has a web page, app, video, or notebook preview, add the link to the README.",
    )


def _check_badges(root: Path) -> tuple[bool, str, str]:
    readme = _readme_text(root)

    if "img.shields.io" in readme or re.search(r"!\[.*?\]\(.*?badge.*?\)", readme, re.IGNORECASE):
        return (
            True,
            "README badges detected.",
            "Use only useful badges: license, tests, package version, or deployment.",
        )

    return (
        False,
        "No README badges detected.",
        "Add small badges for license, tests, or package version after the project title.",
    )


def _check_contributing(root: Path) -> tuple[bool, str, str]:
    files = [
        "CONTRIBUTING.md",
        "CONTRIBUTING.txt",
        ".github/CONTRIBUTING.md",
    ]

    if any((root / filename).exists() for filename in files):
        return (
            True,
            "Contributing guide found.",
            "Keep contribution steps simple for beginners.",
        )

    return (
        False,
        "No contributing guide found.",
        "Add CONTRIBUTING.md if you want other developers to contribute.",
    )


def _check_tests(root: Path) -> tuple[bool, str, str]:
    test_indicators = [
        root / "tests",
        root / "test",
        root / "pytest.ini",
    ]

    if any(path.exists() for path in test_indicators):
        return (
            True,
            "Test files or test directory detected.",
            "Mention how to run tests in the README.",
        )

    if any(root.rglob("test_*.py")) or any(root.rglob("*_test.py")):
        return (
            True,
            "Test files or test directory detected.",
            "Mention how to run tests in the README.",
        )

    return (
        False,
        "No test files detected.",
        "Add a small tests directory and one basic test to build trust.",
    )


def _check_ci_workflow(root: Path) -> tuple[bool, str, str]:
    workflow_dir = root / ".github" / "workflows"

    if workflow_dir.exists() and any(workflow_dir.glob("*.yml")) or workflow_dir.exists() and any(workflow_dir.glob("*.yaml")):
        return (
            True,
            "GitHub Actions workflow detected.",
            "Use CI to run tests automatically on every push.",
        )

    return (
        False,
        "No GitHub Actions workflow detected.",
        "Add a simple CI workflow that installs dependencies and runs tests.",
    )


def _readme_path(root: Path) -> Path | None:
    for filename in ["README.md", "README.rst", "README.txt", "readme.md"]:
        path = root / filename

        if path.exists():
            return path

    return None


def _readme_text(root: Path) -> str:
    path = _readme_path(root)

    if path is None:
        return ""

    return path.read_text(encoding="utf-8", errors="ignore").lower()


def _contains_any(text: str, values: list[str]) -> bool:
    return any(value.lower() in text for value in values)


def _grade_from_percentage(percentage: float) -> str:
    if percentage >= 90:
        return "A"
    if percentage >= 75:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 40:
        return "D"
    return "F"