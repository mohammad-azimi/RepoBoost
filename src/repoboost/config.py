from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from repoboost.presets import (
    CHECK_KEYS,
    DEFAULT_WEIGHTS,
    get_preset,
    require_preset,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


CONFIG_FILENAME = ".repoboost.toml"


@dataclass
class RepoBoostConfig:
    profile: str = "default"
    preset: str = "default"
    fail_under: int | None = None
    weights: dict[str, int] = field(default_factory=lambda: DEFAULT_WEIGHTS.copy())
    disabled_checks: set[str] = field(default_factory=set)
    recommendation_focus: list[str] = field(default_factory=list)
    source_path: str | None = None

    def to_dict(self) -> dict:
        return {
            "profile": self.profile,
            "preset": self.preset,
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
        default_preset = require_preset("default")

        return RepoBoostConfig(
            profile="default",
            preset=default_preset.name,
            weights=default_preset.weights.copy(),
            disabled_checks=set(default_preset.disabled_checks),
            recommendation_focus=list(default_preset.recommendation_focus),
        )

    data = tomllib.loads(resolved_config_path.read_text(encoding="utf-8"))

    return _parse_config_data(data, resolved_config_path)


def generate_config_template(
    profile: str = "python-cli",
    preset_name: str = "python-cli",
) -> str:
    preset = require_preset(preset_name)
    profile_name = profile or preset.name

    weights_text = "\n".join(
        f"{key} = {preset.weights[key]}"
        for key in CHECK_KEYS
    )

    disabled_checks_text = _format_toml_string_list(preset.disabled_checks)
    focus_text = _format_toml_string_list(preset.recommendation_focus, multiline=True)

    return f"""profile = "{profile_name}"
preset = "{preset.name}"
fail_under = 90
disabled_checks = {disabled_checks_text}

[weights]
{weights_text}

[recommendations]
focus = {focus_text}
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
    preset_name = str(data.get("preset", profile))

    preset = get_preset(preset_name)

    if preset is None:
        preset = require_preset("default")

    fail_under = data.get("fail_under")
    if fail_under is not None:
        fail_under = int(fail_under)

    if "disabled_checks" in data:
        disabled_checks = {
            normalize_check_key(str(item))
            for item in data.get("disabled_checks", [])
        }
    else:
        disabled_checks = set(preset.disabled_checks)

    raw_weights = data.get("weights", {})
    weights = preset.weights.copy()

    for key, value in raw_weights.items():
        normalized_key = normalize_check_key(str(key))

        if normalized_key not in CHECK_KEYS:
            continue

        parsed_value = int(value)

        if parsed_value < 0:
            raise ValueError(f"Weight cannot be negative: {key}")

        weights[normalized_key] = parsed_value

    recommendations = data.get("recommendations", {})

    if "focus" in recommendations:
        recommendation_focus = [
            str(item)
            for item in recommendations.get("focus", [])
        ]
    else:
        recommendation_focus = list(preset.recommendation_focus)

    return RepoBoostConfig(
        profile=profile,
        preset=preset.name,
        fail_under=fail_under,
        weights=weights,
        disabled_checks=disabled_checks,
        recommendation_focus=recommendation_focus,
        source_path=str(source_path),
    )


def _format_toml_string_list(
    values: list[str],
    multiline: bool = False,
) -> str:
    if not values:
        return "[]"

    if not multiline:
        quoted_values = ", ".join(f'"{value}"' for value in values)
        return f"[{quoted_values}]"

    lines = ["["]

    for value in values:
        lines.append(f'  "{value}",')

    lines.append("]")

    return "\n".join(lines)