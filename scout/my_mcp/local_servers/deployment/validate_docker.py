from pathlib import Path
import subprocess


def validate_docker(
    project_path: str
):

    project = Path(project_path)

    dockerfile = project / "Dockerfile"

    if not dockerfile.exists():

        return {
            "success": False,
            "error": "Dockerfile not found"
        }

    try:

        result = subprocess.run(
            [
                "docker",
                "build",
                "."
            ],
            cwd=str(project),
            capture_output=True,
            text=True,
            timeout=600
        )

        return {

            "success":
                result.returncode == 0,

            "exit_code":
                result.returncode,

            "stdout":
                result.stdout[-5000:],

            "stderr":
                result.stderr[-5000:]
        }

    except subprocess.TimeoutExpired:

        return {

            "success": False,

            "error":
                "Docker build timed out"
        }

    except Exception as e:

        return {

            "success": False,

            "error":
                str(e)
        }