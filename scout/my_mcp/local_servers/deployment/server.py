from mcp.server.fastmcp import FastMCP

from analyse_project import analyze_project as analyze_project_impl
from generate_docker import (
    generate_docker as generate_docker_impl
)
from validate_docker import (
    validate_docker as validate_docker_impl
)
from generate_github_actions import (
    generate_github_actions as generate_github_actions_impl
)

from validate_github_actions import (
    validate_github_actions as validate_github_actions_impl
)

mcp = FastMCP("deployment")
@mcp.tool()
def analyze_project(
    project_path: str
):
    return analyze_project_impl(
        project_path
    )

@mcp.tool()
def generate_docker(
    project_path: str,
    framework: str
):
    return generate_docker_impl(
        project_path,
        framework
    )

@mcp.tool()
def validate_docker(
    project_path: str
):

    return validate_docker_impl(
        project_path
    )

@mcp.tool()
def generate_github_actions(
    project_path: str,
    framework: str,
    package_manager: str
):

    return generate_github_actions_impl(
        project_path,
        framework,
        package_manager
    )

@mcp.tool()
def validate_github_actions(
    project_path: str
):
    return validate_github_actions_impl(
        project_path
    )

if __name__ == "__main__":
    mcp.run()