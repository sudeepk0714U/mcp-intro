from pathlib import Path
import yaml


def validate_github_actions(
    project_path: str
):

    workflow = (
        Path(project_path)
        /
        ".github"
        /
        "workflows"
        /
        "ci-cd.yml"
    )

    if not workflow.exists():

        return {
            "success": False,
            "error": "Workflow not found"
        }

    try:

        yaml.safe_load(
            workflow.read_text()
        )

        return {
            "success": True
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }