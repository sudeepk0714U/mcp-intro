from pathlib import Path


def generate_github_actions(
    project_path: str,
    framework: str,
    package_manager: str
):

    project = Path(project_path)

    workflow_dir = (
        project /
        ".github" /
        "workflows"
    )

    workflow_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    workflow_file = (
        workflow_dir /
        "ci-cd.yml"
    )

    if package_manager == "uv":

        workflow = """
name: Scout CI/CD

on:
  push:
    branches:
      - main

  pull_request:
    branches:
      - main

jobs:

  build:

    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v5

      - name: Setup Python
        run: uv python install 3.13

      - name: Install Dependencies
        run: uv sync

      - name: Docker Build
        run: docker build -t app .
"""

    else:

        workflow = """
name: CI

on:
  push:
    branches:
      - main
"""

    workflow_file.write_text(
        workflow
    )

    return {
        "success": True,
        "workflow_file": str(workflow_file)
    }