from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


CONFIG_FILENAME = ".repoboost.toml"

CHECK_KEYS = [
    "readme",
    "license",
    "gitignore",
    "installation",
    "usage",
    "screenshots",
    "demo_link",
    "badges",
    "contributing",
    "tests",
    "ci",
]

DEFAULT_WEIGHTS = {
    "readme": 18,
    "license": 12,
    "gitignore": 8,
    "installation": 10,
    "usage": 10,
    "screenshots": 10,
    "demo_link": 8,
    "badges": 6,
    "contributing": 6,
    "tests": 6,
    "ci": 6,
}


@dataclass
class RepoBoostConfig:
    profile: str = "default"
    fail_under: int | None = None
    weights: dict[str, int] = field(default_factory=lambda: DEFAULT_WEIGHTS.copy())
    disabled_checks: set[str] = field(default_factory=set)
    recommendation_focus: list[str] = field(default_factory=list)
    source_path: str | None = None

    def to_dict(self) -> dict:
        return {
            "profile": self.profile,
            "fail_under": self.fail_under,
            "weights": self.weights,
            "disabled_checks": sorted(self.disabled_checks),
            "recommendation_focus": self.recommendation_focus,
            "source_path": self.source_path,
        }


def load_repoboost_config(
    root: str | Path,
    config_path: str | Path | None = None,
) -> RepoBoostConfig:
    root_path = Path(root).resolve()

    if config_path is not None:
        resolved_config_path = Path(config_path).resolve()
    else:
        resolved_config_path = root_path / CONFIG_FILENAME

    if not resolved_config_path.exists():
        return RepoBoostConfig()

    data = tomllib.loads(resolved_config_path.read_text(encoding="utf-8"))

    return _parse_config_data(data, resolved_config_path)


def generate_config_template(profile: str = "python-cli") -> str:
    return f"""profile = "{profile}"
fail_under = 90
disabled_checks = []

[weights]
readme = 18
license = 12
gitignore = 8
installation = 10
usage = 10
screenshots = 10
demo_link = 8
badges = 6
contributing = 6
tests = 6
ci = 6

[recommendations]
focus = [
  "documentation",
  "automation",
  "distribution",
  "code-quality"
]
"""


def normalize_check_key(value: str) -> str:
    normalized = value.strip().lower()
    normalized = normalized.replace("-", "_")
    normalized = normalized.replace(" ", "_")
    normalized = normalized.replace(".", "")
    normalized = normalized.replace("screenshots_or_media", "screenshots")
    normalized = normalized.replace("ci_workflow", "ci")
    normalized = normalized.replace("github_actions", "ci")

    aliases = {
        "readme_md": "readme",
        "license_file": "license",
        "git_ignore": "gitignore",
        "demo": "demo_link",
        "media": "screenshots",
        "screenshot": "screenshots",
        "contributing_guide": "contributing",
        "test": "tests",
        "workflow": "ci",
    }

    return aliases.get(normalized, normalized)


def _parse_config_data(data: dict[str, Any], source_path: Path) -> RepoBoostConfig:
    profile = str(data.get("profile", "custom"))

    fail_under = data.get("fail_under")
    if fail_under is not None:
        fail_under = int(fail_under)

    disabled_checks = {
        normalize_check_key(str(item))
        for item in data.get("disabled_checks", [])
    }

    raw_weights = data.get("weights", {})
    weights = DEFAULT_WEIGHTS.copy()

    for key, value in raw_weights.items():
        normalized_key = normalize_check_key(str(key))

        if normalized_key not in CHECK_KEYS:
            continue

        parsed_value = int(value)

        if parsed_value < 0:
            raise ValueError(f"Weight cannot be negative: {key}")

        weights[normalized_key] = parsed_value

    recommendations = data.get("recommendations", {})
    recommendation_focus = [
        str(item)
        for item in recommendations.get("focus", [])
    ]

    return RepoBoostConfig(
        profile=profile,
        fail_under=fail_under,
        weights=weights,
        disabled_checks=disabled_checks,
        recommendation_focus=recommendation_focus,
        source_path=str(source_path),
    )