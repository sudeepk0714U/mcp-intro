from pathlib import Path
import json


def analyze_project(project_path: str):

    project = Path(project_path)

    result = {

        "project_name": project.name,

        "framework": "Unknown",

        "language": "Unknown",

        "package_manager": "Unknown",

        "entrypoint": None,

        "dockerfile_exists": False,

        "github_actions_exists": False,

        "requirements_exists": False,

        "pyproject_exists": False,

        "uv_lock_exists": False,

        "package_json_exists": False,

        "recommended_deployment": "Unknown"
    }

    # ======================================
    # PYTHON PROJECT DETECTION
    # ======================================

    requirements_file = project / "requirements.txt"

    if requirements_file.exists():

        result["requirements_exists"] = True

        result["language"] = "Python"

        result["package_manager"] = "pip"

    pyproject_file = project / "pyproject.toml"

    if pyproject_file.exists():

        result["pyproject_exists"] = True

        result["language"] = "Python"

        result["package_manager"] = "uv"

    uv_lock_file = project / "uv.lock"

    if uv_lock_file.exists():

        result["uv_lock_exists"] = True

    # ======================================
    # NODE PROJECT DETECTION
    # ======================================

    package_json = project / "package.json"

    if package_json.exists():

        result["package_json_exists"] = True

        result["language"] = "JavaScript"

        try:

            pkg = json.loads(
                package_json.read_text(
                    encoding="utf-8"
                )
            )

            deps = {
                **pkg.get(
                    "dependencies",
                    {}
                ),
                **pkg.get(
                    "devDependencies",
                    {}
                )
            }

            if "next" in deps:

                result["framework"] = "Next.js"

                result[
                    "recommended_deployment"
                ] = "AWS ECS Fargate"

            elif "react" in deps:

                result["framework"] = "React"

                result[
                    "recommended_deployment"
                ] = "S3 + CloudFront"

        except Exception:
            pass

    # ======================================
    # PYTHON FRAMEWORK DETECTION
    # ======================================

    for py_file in project.rglob("*.py"):

        try:

            content = py_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            if (
                "from fastapi import FastAPI"
                in content
            ):

                result["framework"] = "FastAPI"

                result["entrypoint"] = (
                    py_file.name
                )

                result[
                    "recommended_deployment"
                ] = "AWS ECS Fargate"

                break

            if (
                "from flask import Flask"
                in content
            ):

                result["framework"] = "Flask"

                result["entrypoint"] = (
                    py_file.name
                )

                result[
                    "recommended_deployment"
                ] = "AWS ECS Fargate"

                break

        except Exception:
            pass

    # ======================================
    # SCOUT AGENT DETECTION
    # ======================================

    scout_client = (
        project
        /
        "scout"
        /
        "client.py"
    )

    if scout_client.exists():

        result["framework"] = "LangGraph Agent"

        result["entrypoint"] = (
            "python -m scout.client"
        )

        result[
            "recommended_deployment"
        ] = "AWS ECS Fargate"

    # ======================================
    # DEPLOYMENT FILES
    # ======================================

    result["dockerfile_exists"] = (
        project / "Dockerfile"
    ).exists()

    result["github_actions_exists"] = (
        project
        /
        ".github"
        /
        "workflows"
    ).exists()

    return result