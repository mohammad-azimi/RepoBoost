from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re


README_FILES = ["README.md", "README.rst", "README.txt"]


@dataclass
class ProjectProfile:
    path: str
    project_types: list[str]
    languages: list[str]
    package_managers: list[str]
    frameworks: list[str]
    tools: list[str]
    important_files: dict[str, bool]

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "project_types": self.project_types,
            "languages": self.languages,
            "package_managers": self.package_managers,
            "frameworks": self.frameworks,
            "tools": self.tools,
            "important_files": self.important_files,
        }


def inspect_project(path: str | Path) -> ProjectProfile:
    root = Path(path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    corpus = _build_text_corpus(root)
    important_files = _detect_important_files(root)

    languages = _detect_languages(root, corpus)
    package_managers = _detect_package_managers(root, corpus)
    frameworks = _detect_frameworks(root, corpus)
    tools = _detect_tools(root, corpus)
    project_types = _detect_project_types(root, corpus, languages, frameworks, tools)

    return ProjectProfile(
        path=str(root),
        project_types=project_types,
        languages=languages,
        package_managers=package_managers,
        frameworks=frameworks,
        tools=tools,
        important_files=important_files,
    )


def _detect_languages(root: Path, corpus: str) -> list[str]:
    languages: list[str] = []

    if _has_any_file(root, ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"]) or _has_suffix(root, ".py"):
        languages.append("python")

    if _has_any_file(root, ["package.json"]) or _has_suffix(root, ".js"):
        languages.append("javascript")

    if _has_any_file(root, ["tsconfig.json"]) or _has_suffix(root, ".ts") or _contains(corpus, r"\btypescript\b"):
        languages.append("typescript")

    if _has_suffix(root, ".html"):
        languages.append("html")

    if _has_suffix(root, ".css"):
        languages.append("css")

    return languages


def _detect_package_managers(root: Path, corpus: str) -> list[str]:
    package_managers: list[str] = []

    if _has_any_file(root, ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"]):
        package_managers.append("pip")

    if _has_any_file(root, ["poetry.lock"]):
        package_managers.append("poetry")

    if _has_any_file(root, ["uv.lock"]):
        package_managers.append("uv")

    if _has_any_file(root, ["package-lock.json"]) or _contains(corpus, r"\bnpm\b"):
        package_managers.append("npm")

    if _has_any_file(root, ["yarn.lock"]):
        package_managers.append("yarn")

    if _has_any_file(root, ["pnpm-lock.yaml"]):
        package_managers.append("pnpm")

    return package_managers


def _detect_frameworks(root: Path, corpus: str) -> list[str]:
    frameworks: list[str] = []

    checks = {
        "typer": r"\btyper\b",
        "rich": r"\brich\b",
        "pytest": r"\bpytest\b",
        "react": r"\breact\b",
        "django": r"\bdjango\b",
        "flask": r"\bflask\b",
        "fastapi": r"\bfastapi\b",
        "pytorch": r"\btorch\b|\bpytorch\b",
        "tensorflow": r"\btensorflow\b",
        "scikit-learn": r"\bscikit-learn\b|\bsklearn\b",
        "opencv": r"\bopencv\b|\bcv2\b",
    }

    for name, pattern in checks.items():
        if _contains(corpus, pattern):
            frameworks.append(name)

    if (root / "manage.py").exists():
        _append_unique(frameworks, "django")

    return frameworks


def _detect_tools(root: Path, corpus: str) -> list[str]:
    tools: list[str] = []

    if (root / ".github" / "workflows").exists():
        tools.append("github-actions")

    if _has_any_file(root, ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]):
        tools.append("docker")

    if _has_any_file(root, ["pytest.ini"]) or (root / "tests").exists() or _contains(corpus, r"\bpytest\b"):
        tools.append("pytest")

    if _has_any_file(root, [".pre-commit-config.yaml"]):
        tools.append("pre-commit")

    if _has_any_file(root, ["ruff.toml"]) or _contains(corpus, r"\bruff\b"):
        tools.append("ruff")

    if _has_any_file(root, ["mypy.ini"]) or _contains(corpus, r"\bmypy\b"):
        tools.append("mypy")

    return tools


def _detect_project_types(
    root: Path,
    corpus: str,
    languages: list[str],
    frameworks: list[str],
    tools: list[str],
) -> list[str]:
    project_types: list[str] = []

    if _contains(corpus, r"\bcli\b|\bcommand-line\b|\bterminal\b|\bconsole\b|\btyper\b|\bclick\b|\bargparse\b"):
        project_types.append("cli")

    if any(name in frameworks for name in ["react", "django", "flask", "fastapi"]) or _has_suffix(root, ".html"):
        project_types.append("web")

    if _contains(corpus, r"\bdeveloper tool\b|\bdeveloper tools\b|\bdev tool\b|\bdevtools\b"):
        project_types.append("developer-tool")

    if _contains(corpus, r"\brepository\b|\brepo\b|\bgithub\b|\breadme\b|\bdocumentation\b"):
        project_types.append("repository-tool")

    if _contains(corpus, r"\bmachine learning\b|\bml\b|\bscikit-learn\b|\bpytorch\b|\btensorflow\b"):
        project_types.append("machine-learning")

    if _contains(corpus, r"\breinforcement learning\b|\bq-learning\b|\bppo\b|\bdqn\b"):
        project_types.append("reinforcement-learning")

    if _contains(corpus, r"\bcomputer vision\b|\bopencv\b|\bimage processing\b"):
        project_types.append("computer-vision")

    if "python" in languages and not project_types:
        project_types.append("python-project")

    if "javascript" in languages and not project_types:
        project_types.append("javascript-project")

    if "github-actions" in tools and "repository-tool" not in project_types:
        _append_unique(project_types, "automation-ready")

    return project_types


def _detect_important_files(root: Path) -> dict[str, bool]:
    return {
        "readme": _has_any_file(root, README_FILES),
        "license": _has_any_file(root, ["LICENSE", "LICENSE.md", "LICENSE.txt"]),
        "gitignore": _has_any_file(root, [".gitignore"]),
        "contributing": _has_any_file(root, ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"]),
        "pyproject": _has_any_file(root, ["pyproject.toml"]),
        "package_json": _has_any_file(root, ["package.json"]),
        "tests": (root / "tests").exists() or (root / "test").exists(),
        "github_actions": (root / ".github" / "workflows").exists(),
        "docker": _has_any_file(root, ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]),
    }


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
        "pytest.ini",
        "ruff.toml",
        "mypy.ini",
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


def _has_suffix(root: Path, suffix: str) -> bool:
    ignored_dirs = {
        ".git",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
    }

    for path in root.rglob("*"):
        try:
            relative_parts = set(path.relative_to(root).parts)
        except ValueError:
            continue

        if relative_parts.intersection(ignored_dirs):
            continue

        if path.is_file() and path.suffix.lower() == suffix:
            return True

    return False


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)