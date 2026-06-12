from repoboost.project import inspect_project


def test_inspect_python_cli_project(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        """
# RepoBoost

RepoBoost is a CLI developer tool for GitHub repository audit and README quality checks.
It uses Typer, Rich, and Pytest.
""",
        encoding="utf-8",
    )

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
name = "repoboost"
dependencies = [
    "typer",
    "rich",
    "pytest"
]
""",
        encoding="utf-8",
    )

    license_file = tmp_path / "LICENSE"
    license_file.write_text("MIT License", encoding="utf-8")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    ci_file = workflows_dir / "ci.yml"
    ci_file.write_text("name: CI\n", encoding="utf-8")

    profile = inspect_project(tmp_path)

    assert "python" in profile.languages
    assert "pip" in profile.package_managers
    assert "cli" in profile.project_types
    assert "developer-tool" in profile.project_types
    assert "repository-tool" in profile.project_types
    assert "typer" in profile.frameworks
    assert "rich" in profile.frameworks
    assert "pytest" in profile.frameworks
    assert "github-actions" in profile.tools
    assert profile.important_files["readme"] is True
    assert profile.important_files["license"] is True
    assert profile.important_files["tests"] is True
    assert profile.important_files["github_actions"] is True


def test_inspect_react_typescript_project(tmp_path):
    package_json = tmp_path / "package.json"
    package_json.write_text(
        """
{
  "name": "portfolio-app",
  "description": "A React TypeScript portfolio website",
  "dependencies": {
    "react": "^19.0.0",
    "typescript": "^5.0.0"
  }
}
""",
        encoding="utf-8",
    )

    tsconfig = tmp_path / "tsconfig.json"
    tsconfig.write_text("{}", encoding="utf-8")

    profile = inspect_project(tmp_path)

    assert "javascript" in profile.languages
    assert "typescript" in profile.languages
    assert "react" in profile.frameworks
    assert "web" in profile.project_types
    assert profile.important_files["package_json"] is True