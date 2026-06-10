import requests


def verify_deployment(
    url: str
):

    try:

        response = requests.get(
            f"{url}/health",
            timeout=10
        )

        return {
            "status_code": response.status_code,
            "response": response.json(),
            "success": response.status_code == 200
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }