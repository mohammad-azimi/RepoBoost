from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CIWorkflow:
    name: str
    fail_under: int
    python_version: str
    content: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "fail_under": self.fail_under,
            "python_version": self.python_version,
            "content": self.content,
        }


def generate_ci_workflow(
    fail_under: int = 80,
    python_version: str = "3.12",
) -> CIWorkflow:
    content = f"""name: RepoBoost

on:
  push:
    branches:
      - main
      - master
  pull_request:

jobs:
  repoboost:
    name: Run RepoBoost
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "{python_version}"

      - name: Install RepoBoost
        run: |
          python -m pip install --upgrade pip
          pip install repoboost

      - name: Run RepoBoost scan
        run: repoboost scan . --fail-under {fail_under}
"""

    return CIWorkflow(
        name="RepoBoost",
        fail_under=fail_under,
        python_version=python_version,
        content=content,
    )