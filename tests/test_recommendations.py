from repoboost.recommendations import generate_recommendations


def test_generate_recommendations_for_empty_project(tmp_path):
    recommendations = generate_recommendations(tmp_path)

    titles = [recommendation.title for recommendation in recommendations]

    assert any("README" in title for title in titles)
    assert any(recommendation.category == "presentation" for recommendation in recommendations)
    assert any(recommendation.priority == "high" for recommendation in recommendations)


def test_generate_recommendations_for_python_cli_project(tmp_path):
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
    "rich",
    "pytest"
]
""",
        encoding="utf-8",
    )

    recommendations = generate_recommendations(tmp_path)

    titles = [recommendation.title for recommendation in recommendations]

    assert "Keep PyPI installation visible near the top" in titles
    assert "Add more real command examples" in titles
    assert "Add GitHub topics to improve discoverability" in titles