from repoboost.topics import suggest_topics


def test_suggest_topics_for_python_cli_project(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        """
# RepoBoost

RepoBoost is a CLI developer tool for GitHub repository audit and README quality checks.

It helps open-source projects improve documentation and repository presentation.
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
    "rich"
]
""",
        encoding="utf-8",
    )

    license_file = tmp_path / "LICENSE"
    license_file.write_text("MIT License", encoding="utf-8")

    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    ci_file = workflows_dir / "ci.yml"
    ci_file.write_text("name: CI\n", encoding="utf-8")

    topics = [suggestion.topic for suggestion in suggest_topics(tmp_path)]

    assert "python" in topics
    assert "cli" in topics
    assert "github" in topics
    assert "github-actions" in topics
    assert "open-source" in topics
    assert "documentation" in topics
    assert "repository-audit" in topics
    assert "developer-tools" in topics


def test_suggest_topics_for_react_typescript_project(tmp_path):
    package_json = tmp_path / "package.json"
    package_json.write_text(
        """
{
  "name": "demo-app",
  "description": "A React TypeScript portfolio project",
  "dependencies": {
    "react": "^19.0.0",
    "typescript": "^5.0.0"
  }
}
""",
        encoding="utf-8",
    )

    topics = [suggestion.topic for suggestion in suggest_topics(tmp_path)]

    assert "javascript" in topics
    assert "typescript" in topics
    assert "react" in topics
    assert "portfolio" in topics