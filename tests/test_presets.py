from typer.testing import CliRunner

from repoboost.cli import app
from repoboost.config import generate_config_template, load_repoboost_config
from repoboost.presets import get_preset, list_presets


runner = CliRunner()


def test_list_presets_contains_expected_presets():
    preset_names = [
        preset.name
        for preset in list_presets()
    ]

    assert "default" in preset_names
    assert "python-cli" in preset_names
    assert "web-app" in preset_names
    assert "machine-learning" in preset_names
    assert "portfolio-project" in preset_names
    assert "docs-only" in preset_names


def test_get_preset_normalizes_names():
    preset = get_preset("machine_learning")

    assert preset is not None
    assert preset.name == "machine-learning"


def test_generate_config_template_uses_selected_preset():
    template = generate_config_template(
        profile="web-app",
        preset_name="web-app",
    )

    assert 'profile = "web-app"' in template
    assert 'preset = "web-app"' in template
    assert "screenshots = 14" in template
    assert "demo_link = 14" in template


def test_load_config_applies_selected_preset(tmp_path):
    config_file = tmp_path / ".repoboost.toml"
    config_file.write_text(
        """
profile = "machine-learning"
preset = "machine-learning"
disabled_checks = []

[weights]
readme = 20
""",
        encoding="utf-8",
    )

    config = load_repoboost_config(tmp_path)

    assert config.profile == "machine-learning"
    assert config.preset == "machine-learning"
    assert config.weights["readme"] == 20
    assert config.weights["screenshots"] == 16
    assert "machine-learning" in config.recommendation_focus


def test_cli_presets_lists_presets():
    result = runner.invoke(
        app,
        ["presets"],
    )

    assert result.exit_code == 0
    assert "Built-in scoring presets" in result.output
    assert "python-cli" in result.output
    assert "web-app" in result.output


def test_cli_presets_prints_json():
    result = runner.invoke(
        app,
        ["presets", "--json"],
    )

    assert result.exit_code == 0
    assert '"presets"' in result.output
    assert '"python-cli"' in result.output


def test_cli_init_config_uses_preset(tmp_path):
    result = runner.invoke(
        app,
        [
            "init-config",
            str(tmp_path),
            "--preset",
            "portfolio-project",
        ],
    )

    config_file = tmp_path / ".repoboost.toml"

    assert result.exit_code == 0
    assert config_file.exists()

    content = config_file.read_text(encoding="utf-8")

    assert 'profile = "portfolio-project"' in content
    assert 'preset = "portfolio-project"' in content
    assert "screenshots = 16" in content
    assert "demo_link = 14" in content


def test_cli_init_config_rejects_unknown_preset(tmp_path):
    result = runner.invoke(
        app,
        [
            "init-config",
            str(tmp_path),
            "--preset",
            "unknown-preset",
        ],
    )

    assert result.exit_code == 1
    assert "Unknown preset" in result.output