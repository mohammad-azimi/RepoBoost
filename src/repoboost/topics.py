from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re


README_FILES = ["README.md", "README.rst", "README.txt"]


@dataclass
class TopicSuggestion:
    topic: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "reason": self.reason,
        }


def suggest_topics(path: str | Path) -> list[TopicSuggestion]:
    root = Path(path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    corpus = _build_text_corpus(root)
    suggestions: dict[str, str] = {}

    def add(topic: str, reason: str) -> None:
        if topic not in suggestions:
            suggestions[topic] = reason

    if _has_any_file(root, ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"]):
        add("python", "Python project files were detected.")

    if _has_any_file(root, ["package.json"]):
        add("javascript", "A package.json file was detected.")

    if _has_any_file(root, ["tsconfig.json"]) or _contains(corpus, r"\btypescript\b"):
        add("typescript", "TypeScript configuration or keywords were detected.")

    if _contains(corpus, r"\breact\b"):
        add("react", "React keywords were detected.")

    if _contains(corpus, r"\btyper\b|\bclick\b|\bargparse\b|\bcommand-line\b|\bcli\b"):
        add("cli", "Command-line interface tooling or keywords were detected.")

    if _contains(corpus, r"\brich\b|\bterminal\b|\bconsole\b"):
        add("terminal", "Terminal output tooling or keywords were detected.")

    if _contains(corpus, r"\bgithub\b") or (root / ".github").exists():
        add("github", "GitHub-related files or keywords were detected.")

    if (root / ".github" / "workflows").exists():
        add("github-actions", "GitHub Actions workflow files were detected.")

    if _has_any_file(root, ["LICENSE", "LICENSE.md", "LICENSE.txt"]):
        add("open-source", "A license file was detected.")

    if _has_any_file(root, README_FILES):
        add("documentation", "README documentation was detected.")

    if _contains(corpus, r"\breadme\b"):
        add("readme", "README-related keywords were detected.")

    if _contains(corpus, r"\brepository\b|\brepositories\b|\brepo\b|\brepos\b"):
        add("repository", "Repository-related keywords were detected.")

    if _contains(corpus, r"\baudit\b|\bscore\b|\bquality\b|\bcheck\b|\bscanner\b"):
        add("repository-audit", "Repository audit or scoring keywords were detected.")

    if _contains(corpus, r"\bdeveloper tool\b|\bdeveloper tools\b|\bdev tool\b|\bdevtools\b"):
        add("developer-tools", "Developer-tooling keywords were detected.")

    if _contains(corpus, r"\bportfolio\b"):
        add("portfolio", "Portfolio-related keywords were detected.")

    if _contains(corpus, r"\bmachine learning\b|\bml\b|\bscikit-learn\b|\bsklearn\b"):
        add("machine-learning", "Machine learning keywords were detected.")

    if _contains(corpus, r"\breinforcement learning\b|\brl\b|\bq-learning\b|\bppo\b|\bdqn\b"):
        add("reinforcement-learning", "Reinforcement learning keywords were detected.")

    if _contains(corpus, r"\bcomputer vision\b|\bopencv\b|\bimage processing\b"):
        add("computer-vision", "Computer vision keywords were detected.")

    if _contains(corpus, r"\bdjango\b"):
        add("django", "Django keywords were detected.")

    if _contains(corpus, r"\bflask\b"):
        add("flask", "Flask keywords were detected.")

    if _contains(corpus, r"\bfastapi\b"):
        add("fastapi", "FastAPI keywords were detected.")

    if _has_any_file(root, ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]):
        add("docker", "Docker files were detected.")

    return [
        TopicSuggestion(topic=topic, reason=reason)
        for topic, reason in suggestions.items()
    ]


def _build_text_corpus(root: Path) -> str:
    parts: list[str] = []

    for filename in README_FILES:
        path = root / filename
        if path.exists() and path.is_file():
            parts.append(_read_text(path))

    for filename in [
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        "setup.cfg",
        "package.json",
        "tsconfig.json",
    ]:
        path = root / filename
        if path.exists() and path.is_file():
            parts.append(_read_text(path))

    package_json = root / "package.json"
    if package_json.exists() and package_json.is_file():
        parts.append(_read_package_json(package_json))

    return "\n".join(parts).lower()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _read_package_json(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    parts: list[str] = []

    for key in ["name", "description"]:
        value = data.get(key)
        if isinstance(value, str):
            parts.append(value)

    for key in ["dependencies", "devDependencies"]:
        value = data.get(key)
        if isinstance(value, dict):
            parts.extend(value.keys())

    return "\n".join(parts)


def _contains(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, flags=re.IGNORECASE))


def _has_any_file(root: Path, names: list[str]) -> bool:
    return any((root / name).exists() for name in names)