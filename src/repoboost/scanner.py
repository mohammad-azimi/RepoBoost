from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


README_FILES = ["README.md", "README.rst", "README.txt"]
LICENSE_FILES = ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"]
GITIGNORE_FILES = [".gitignore"]
CONTRIBUTING_FILES = [
    "CONTRIBUTING.md",
    "CONTRIBUTING.txt",
    ".github/CONTRIBUTING.md",
]
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


@dataclass
class CheckResult:
    name: str
    passed: bool
    score: int
    max_score: int
    message: str
    suggestion: str
    severity: str = "info"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "score": self.score,
            "max_score": self.max_score,
            "message": self.message,
            "suggestion": self.suggestion,
            "severity": self.severity,
        }


@dataclass
class ScanReport:
    path: str
    score: int
    max_score: int
    grade: str
    checks: list[CheckResult]

    @property
    def percentage(self) -> float:
        if self.max_score == 0:
            return 0.0
        return round((self.score / self.max_score) * 100, 2)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "grade": self.grade,
            "checks": [check.to_dict() for check in self.checks],
        }


def scan_project(path: str | Path) -> ScanReport:
    root = Path(path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    readme_path, readme_text = _read_readme(root)

    checks = [
        _check_readme(readme_path),
        _check_license(root),
        _check_gitignore(root),
        _check_install_section(readme_text),
        _check_usage_section(readme_text),
        _check_screenshots(root, readme_text),
        _check_demo_link(readme_text),
        _check_badges(readme_text),
        _check_contributing(root),
        _check_tests(root),
        _check_ci(root),
    ]

    score = sum(check.score for check in checks)
    max_score = sum(check.max_score for check in checks)
    grade = grade_from_percentage((score / max_score) * 100 if max_score else 0)

    return ScanReport(
        path=str(root),
        score=score,
        max_score=max_score,
        grade=grade,
        checks=checks,
    )


def grade_from_percentage(percentage: float) -> str:
    if percentage >= 90:
        return "A"
    if percentage >= 75:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 40:
        return "D"
    return "F"


def _check_readme(readme_path: Path | None) -> CheckResult:
    max_score = 18

    if readme_path:
        return CheckResult(
            name="README",
            passed=True,
            score=max_score,
            max_score=max_score,
            message=f"Found {readme_path.name}.",
            suggestion="Keep the first section clear: what it does, who it is for, and how to run it.",
        )

    return CheckResult(
        name="README",
        passed=False,
        score=0,
        max_score=max_score,
        message="No README file found.",
        suggestion="Add a README.md with a short pitch, features, installation, usage, screenshots, and roadmap.",
        severity="high",
    )


def _check_license(root: Path) -> CheckResult:
    max_score = 12

    if _find_first_file(root, LICENSE_FILES):
        return CheckResult(
            name="License",
            passed=True,
            score=max_score,
            max_score=max_score,
            message="License file found.",
            suggestion="MIT is a good default for small developer tools.",
        )

    return CheckResult(
        name="License",
        passed=False,
        score=0,
        max_score=max_score,
        message="No license file found.",
        suggestion="Add a LICENSE file so other developers know how they can use the project.",
        severity="high",
    )


def _check_gitignore(root: Path) -> CheckResult:
    max_score = 8

    if _find_first_file(root, GITIGNORE_FILES):
        return CheckResult(
            name=".gitignore",
            passed=True,
            score=max_score,
            max_score=max_score,
            message=".gitignore file found.",
            suggestion="Make sure it ignores virtual environments, cache files, build outputs, and secrets.",
        )

    return CheckResult(
        name=".gitignore",
        passed=False,
        score=0,
        max_score=max_score,
        message="No .gitignore file found.",
        suggestion="Add a .gitignore file to avoid uploading cache files, virtual environments, and local settings.",
        severity="medium",
    )


def _check_install_section(readme_text: str) -> CheckResult:
    max_score = 10

    patterns = [
        r"\binstallation\b",
        r"\binstall\b",
        r"\bsetup\b",
        r"\bgetting started\b",
        r"\bquickstart\b",
        r"pip install",
        r"npm install",
        r"poetry install",
        r"uv pip install",
    ]

    if _contains_any(readme_text, patterns):
        return CheckResult(
            name="Installation",
            passed=True,
            score=max_score,
            max_score=max_score,
            message="Installation instructions detected.",
            suggestion="Keep installation short and copy-paste friendly.",
        )

    return CheckResult(
        name="Installation",
        passed=False,
        score=0,
        max_score=max_score,
        message="No clear installation section detected.",
        suggestion="Add a section showing the exact command needed to install or run the project.",
        severity="high",
    )


def _check_usage_section(readme_text: str) -> CheckResult:
    max_score = 10

    patterns = [
        r"\busage\b",
        r"\bexample\b",
        r"\bexamples\b",
        r"\bhow to use\b",
        r"\bcommand\b",
        r"\bcli\b",
        r"python\s+\S+\.py",
        r"repoboost\s+scan",
    ]

    if _contains_any(readme_text, patterns):
        return CheckResult(
            name="Usage",
            passed=True,
            score=max_score,
            max_score=max_score,
            message="Usage example detected.",
            suggestion="Show the fastest possible example near the top of the README.",
        )

    return CheckResult(
        name="Usage",
        passed=False,
        score=0,
        max_score=max_score,
        message="No clear usage example detected.",
        suggestion="Add at least one command or code example that shows the project working.",
        severity="high",
    )


def _check_screenshots(root: Path, readme_text: str) -> CheckResult:
    max_score = 10

    markdown_image = re.search(
        r"!\[[^\]]*\]\([^)]+\.(png|jpg|jpeg|gif|webp|svg)(\?[^)]*)?\)",
        readme_text,
        flags=re.IGNORECASE,
    )

    project_images = [
        path
        for path in _safe_rglob(root)
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]

    if markdown_image or project_images:
        return CheckResult(
            name="Screenshots or media",
            passed=True,
            score=max_score,
            max_score=max_score,
            message="Screenshot, image, GIF, or visual media detected.",
            suggestion="Use one strong screenshot or GIF near the top of the README.",
        )

    return CheckResult(
        name="Screenshots or media",
        passed=False,
        score=0,
        max_score=max_score,
        message="No screenshots or visual media detected.",
        suggestion="Add a screenshot, GIF, or demo image to make the repository easier to understand quickly.",
        severity="medium",
    )


def _check_demo_link(readme_text: str) -> CheckResult:
    max_score = 8

    has_url = bool(re.search(r"https?://", readme_text, flags=re.IGNORECASE))
    has_demo_word = _contains_any(
        readme_text,
        [
            r"\bdemo\b",
            r"\blive\b",
            r"\bpreview\b",
            r"\bwebsite\b",
            r"\bdeployment\b",
        ],
    )

    if has_url and has_demo_word:
        return CheckResult(
            name="Demo link",
            passed=True,
            score=max_score,
            max_score=max_score,
            message="Demo or live link detected.",
            suggestion="Put the demo link near the top so visitors can try the project quickly.",
        )

    return CheckResult(
        name="Demo link",
        passed=False,
        score=0,
        max_score=max_score,
        message="No clear demo or live link detected.",
        suggestion="If the project has a web page, app, video, or notebook preview, add the link to the README.",
        severity="medium",
    )


def _check_badges(readme_text: str) -> CheckResult:
    max_score = 6

    has_badge = bool(
        re.search(
            r"!\[[^\]]*\]\(https?://[^)]*(badge|shields\.io|actions|workflow|pypi|npm)[^)]*\)",
            readme_text,
            flags=re.IGNORECASE,
        )
    )

    if has_badge:
        return CheckResult(
            name="Badges",
            passed=True,
            score=max_score,
            max_score=max_score,
            message="README badges detected.",
            suggestion="Use only useful badges: license, tests, package version, or deployment.",
        )

    return CheckResult(
        name="Badges",
        passed=False,
        score=0,
        max_score=max_score,
        message="No README badges detected.",
        suggestion="Add small badges for license, tests, or package version after the project title.",
        severity="low",
    )


def _check_contributing(root: Path) -> CheckResult:
    max_score = 6

    if _find_first_file(root, CONTRIBUTING_FILES):
        return CheckResult(
            name="Contributing guide",
            passed=True,
            score=max_score,
            max_score=max_score,
            message="Contributing guide found.",
            suggestion="Keep contribution steps simple for beginners.",
        )

    return CheckResult(
        name="Contributing guide",
        passed=False,
        score=0,
        max_score=max_score,
        message="No contributing guide found.",
        suggestion="Add CONTRIBUTING.md if you want other developers to contribute.",
        severity="low",
    )


def _check_tests(root: Path) -> CheckResult:
    max_score = 6

    test_markers = [
        root / "tests",
        root / "test",
    ]

    has_test_dir = any(path.exists() and path.is_dir() for path in test_markers)

    has_test_file = any(
        path.is_file()
        and (
            path.name.startswith("test_")
            or path.name.endswith("_test.py")
            or path.name.endswith(".test.js")
            or path.name.endswith(".spec.js")
            or path.name.endswith(".test.ts")
            or path.name.endswith(".spec.ts")
        )
        for path in _safe_rglob(root)
    )

    if has_test_dir or has_test_file:
        return CheckResult(
            name="Tests",
            passed=True,
            score=max_score,
            max_score=max_score,
            message="Test files or test directory detected.",
            suggestion="Mention how to run tests in the README.",
        )

    return CheckResult(
        name="Tests",
        passed=False,
        score=0,
        max_score=max_score,
        message="No test files detected.",
        suggestion="Add a small tests directory and one basic test to build trust.",
        severity="medium",
    )


def _check_ci(root: Path) -> CheckResult:
    max_score = 6
    workflows_dir = root / ".github" / "workflows"

    if workflows_dir.exists() and any(workflows_dir.glob("*.yml")) or workflows_dir.exists() and any(workflows_dir.glob("*.yaml")):
        return CheckResult(
            name="CI workflow",
            passed=True,
            score=max_score,
            max_score=max_score,
            message="GitHub Actions workflow detected.",
            suggestion="Use CI to run tests automatically on every push.",
        )

    return CheckResult(
        name="CI workflow",
        passed=False,
        score=0,
        max_score=max_score,
        message="No GitHub Actions workflow detected.",
        suggestion="Add a simple CI workflow that installs dependencies and runs tests.",
        severity="low",
    )


def _read_readme(root: Path) -> tuple[Path | None, str]:
    readme_path = _find_first_file(root, README_FILES)

    if not readme_path:
        return None, ""

    try:
        return readme_path, readme_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return readme_path, ""


def _find_first_file(root: Path, names: Iterable[str]) -> Path | None:
    for name in names:
        candidate = root / name
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _contains_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _safe_rglob(root: Path):
    for path in root.rglob("*"):
        try:
            relative_parts = set(path.relative_to(root).parts)
        except ValueError:
            continue

        if relative_parts.intersection(IGNORED_DIRS):
            continue

        yield path