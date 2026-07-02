from __future__ import annotations

from dataclasses import dataclass


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


@dataclass(frozen=True)
class ScoringPreset:
    name: str
    description: str
    weights: dict[str, int]
    disabled_checks: list[str]
    recommendation_focus: list[str]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "weights": self.weights,
            "disabled_checks": self.disabled_checks,
            "recommendation_focus": self.recommendation_focus,
        }


PRESETS = {
    "default": ScoringPreset(
        name="default",
        description="Balanced scoring for general repositories.",
        weights=DEFAULT_WEIGHTS,
        disabled_checks=[],
        recommendation_focus=[
            "documentation",
            "automation",
            "distribution",
            "code-quality",
        ],
    ),
    "python-cli": ScoringPreset(
        name="python-cli",
        description="Best for Python command-line tools and installable packages.",
        weights={
            "readme": 18,
            "license": 12,
            "gitignore": 8,
            "installation": 12,
            "usage": 12,
            "screenshots": 6,
            "demo_link": 4,
            "badges": 6,
            "contributing": 6,
            "tests": 10,
            "ci": 6,
        },
        disabled_checks=[],
        recommendation_focus=[
            "documentation",
            "automation",
            "distribution",
            "code-quality",
        ],
    ),
    "web-app": ScoringPreset(
        name="web-app",
        description="Best for deployed web apps, dashboards, and frontend/backend projects.",
        weights={
            "readme": 14,
            "license": 8,
            "gitignore": 8,
            "installation": 8,
            "usage": 10,
            "screenshots": 14,
            "demo_link": 14,
            "badges": 5,
            "contributing": 5,
            "tests": 6,
            "ci": 8,
        },
        disabled_checks=[],
        recommendation_focus=[
            "documentation",
            "automation",
            "code-quality",
        ],
    ),
    "machine-learning": ScoringPreset(
        name="machine-learning",
        description="Best for ML, computer vision, data science, and experiment-based repositories.",
        weights={
            "readme": 16,
            "license": 8,
            "gitignore": 6,
            "installation": 8,
            "usage": 12,
            "screenshots": 16,
            "demo_link": 8,
            "badges": 4,
            "contributing": 4,
            "tests": 14,
            "ci": 4,
        },
        disabled_checks=[],
        recommendation_focus=[
            "documentation",
            "automation",
            "code-quality",
            "machine-learning",
            "computer-vision",
            "reinforcement-learning",
        ],
    ),
    "portfolio-project": ScoringPreset(
        name="portfolio-project",
        description="Best for projects that should look strong to recruiters, supervisors, or visitors.",
        weights={
            "readme": 16,
            "license": 8,
            "gitignore": 6,
            "installation": 8,
            "usage": 10,
            "screenshots": 16,
            "demo_link": 14,
            "badges": 6,
            "contributing": 4,
            "tests": 6,
            "ci": 6,
        },
        disabled_checks=[],
        recommendation_focus=[
            "documentation",
            "automation",
            "distribution",
            "code-quality",
        ],
    ),
    "docs-only": ScoringPreset(
        name="docs-only",
        description="Best for documentation-first repositories without code execution requirements.",
        weights={
            "readme": 45,
            "license": 15,
            "gitignore": 10,
            "installation": 15,
            "usage": 10,
            "screenshots": 0,
            "demo_link": 0,
            "badges": 5,
            "contributing": 0,
            "tests": 0,
            "ci": 0,
        },
        disabled_checks=[
            "screenshots",
            "demo_link",
            "contributing",
            "tests",
            "ci",
        ],
        recommendation_focus=[
            "documentation",
        ],
    ),
}


def list_presets() -> list[ScoringPreset]:
    return sorted(PRESETS.values(), key=lambda preset: preset.name)


def get_preset(name: str) -> ScoringPreset | None:
    normalized_name = normalize_preset_name(name)
    return PRESETS.get(normalized_name)


def require_preset(name: str) -> ScoringPreset:
    preset = get_preset(name)

    if preset is None:
        available = ", ".join(sorted(PRESETS))
        raise ValueError(
            f"Unknown preset '{name}'. Available presets: {available}"
        )

    return preset


def normalize_preset_name(name: str) -> str:
    return name.strip().lower().replace("_", "-").replace(" ", "-")