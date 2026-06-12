from repoboost.ci import generate_ci_workflow


def test_generate_ci_workflow_defaults():
    workflow = generate_ci_workflow()

    assert workflow.name == "RepoBoost"
    assert workflow.fail_under == 80
    assert workflow.python_version == "3.12"
    assert "name: RepoBoost" in workflow.content
    assert "pip install repoboost" in workflow.content
    assert "repoboost scan . --fail-under 80" in workflow.content


def test_generate_ci_workflow_custom_options():
    workflow = generate_ci_workflow(
        fail_under=90,
        python_version="3.11",
    )

    assert workflow.fail_under == 90
    assert workflow.python_version == "3.11"
    assert 'python-version: "3.11"' in workflow.content
    assert "repoboost scan . --fail-under 90" in workflow.content