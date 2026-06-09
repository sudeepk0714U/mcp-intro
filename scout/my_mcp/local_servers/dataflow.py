import pandas as pd
from mcp.server.fastmcp import FastMCP
from typing import Optional
import duckdb
import os
from dotenv import load_dotenv
import subprocess
import tempfile
import requests

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("dataflow")


class DataFlowSession:
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.working_dir = os.environ.get("MCP_FILESYSTEM_DIR", None)
        self.current_project_dir: Optional[str] = None
        self.github_token = os.environ.get("MCP_GITHUB_PAT", None)

    async def load_data(self, file_path: str) -> str:
        try:
            self.data = pd.read_csv(file_path)
            return f"Data loaded from {file_path}. Shape: {self.data.shape}"
        except Exception as e:
            return f"Error loading data: {str(e)}"

    async def query_data(self, query: str) -> str:
        if self.data is None:
            return "No data loaded."

        try:
            con = duckdb.connect(database=':memory:')
            con.register('data', self.data)
            result = con.execute(query).fetchdf()
            return result.to_string()
        except Exception as e:
            return f"Error executing query: {str(e)}"

    async def create_new_project(self, project_name: str) -> str:
        try:
            project_dir = os.path.join(self.working_dir, project_name)

            if os.path.exists(project_dir):
                raise ValueError(f"Project {project_name} already exists.")

            os.makedirs(project_dir)
            original_dir = os.getcwd()
            os.chdir(project_dir)

            try:
                subprocess.run(["uv", "init", "."], check=True)
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["mkdir", "data"], check=True)
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

                self.current_project_dir = project_dir

                return f"Project {project_name} created at {project_dir}"
            finally:
                os.chdir(original_dir)

        except Exception as e:
            return f"Error creating project: {str(e)}"

    async def run_code(self, code: str, project_name: Optional[str] = None) -> str:
        try:
            if project_name:
                project_dir = os.path.join(self.working_dir, project_name)
                if not os.path.exists(project_dir):
                    return f"Error: Project {project_name} does not exist."
                work_dir = project_dir
            elif self.current_project_dir:
                work_dir = self.current_project_dir
            else:
                work_dir = self.working_dir or os.getcwd()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=work_dir) as f:
                f.write(code)
                temp_file = f.name

            try:
                original_dir = os.getcwd()
                os.chdir(work_dir)

                try:
                    if os.path.exists(os.path.join(work_dir, 'pyproject.toml')):
                        result = subprocess.run(
                            ["uv", "run", temp_file],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                    else:
                        result = subprocess.run(
                            ["python", temp_file],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                    output = []
                    if result.stdout:
                        output.append(f"STDOUT:\n{result.stdout}")
                    if result.stderr:
                        output.append(f"STDERR:\n{result.stderr}")
                    if result.returncode != 0:
                        output.append(f"\nExit code: {result.returncode}")

                    return "\n\n".join(output) if output else "Code executed successfully with no output."

                finally:
                    os.chdir(original_dir)

            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out after 30 seconds."
        except Exception as e:
            return f"Error running code: {str(e)}"

    async def install_dependency(self, package: str, project_name: Optional[str] = None) -> str:
        try:
            if project_name:
                project_dir = os.path.join(self.working_dir, project_name)
                if not os.path.exists(project_dir):
                    return f"Error: Project {project_name} does not exist."
            elif self.current_project_dir:
                project_dir = self.current_project_dir
            else:
                return "Error: No active project. Create a project first."

            original_dir = os.getcwd()
            os.chdir(project_dir)

            try:
                result = subprocess.run(
                    ["uv", "add", package],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return f"Successfully installed {package}\n{result.stdout}"
            finally:
                os.chdir(original_dir)

        except subprocess.CalledProcessError as e:
            return f"Error installing {package}: {e.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def github_push(
        self,
        commit_message: str,
        project_name: Optional[str] = None,
        repo_name: Optional[str] = None,
        private: bool = True,
        branch: str = "main",
        create_repo: bool = False,
    ) -> str:
        """Stage all changes, commit, and push to GitHub. Optionally create the remote repo first."""
        try:
            token = self.github_token
            if not token:
                return (
                    "Error: GITHUB_TOKEN not set. "
                    "Add GITHUB_TOKEN=<your_pat> to your .env file."
                )

            # Resolve project directory
            if project_name:
                project_dir = os.path.join(self.working_dir, project_name)
                if not os.path.exists(project_dir):
                    return f"Error: Project '{project_name}' does not exist."
            elif self.current_project_dir:
                project_dir = self.current_project_dir
            else:
                return "Error: No active project. Create or specify a project first."

            # Determine repo name (default to the folder name)
            effective_repo_name = repo_name or os.path.basename(project_dir)

            original_dir = os.getcwd()
            os.chdir(project_dir)

            try:
                output_lines = []

                # ── 1. Get authenticated GitHub username ──────────────────────────
                user_resp = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github+json",
                    },
                    timeout=10,
                )
                if user_resp.status_code != 200:
                    return f"Error fetching GitHub user: {user_resp.json().get('message', user_resp.text)}"
                github_username = user_resp.json()["login"]

                # ── 2. Optionally create the remote repo ──────────────────────────
                if create_repo:
                    create_resp = requests.post(
                        "https://api.github.com/user/repos",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Accept": "application/vnd.github+json",
                        },
                        json={
                            "name": effective_repo_name,
                            "private": private,
                            "auto_init": False,
                        },
                        timeout=10,
                    )
                    if create_resp.status_code == 201:
                        output_lines.append(
                            f"✅ Created GitHub repo: {github_username}/{effective_repo_name} "
                            f"({'private' if private else 'public'})"
                        )
                    elif create_resp.status_code == 422:
                        output_lines.append(
                            f"ℹ️  Repo '{effective_repo_name}' already exists on GitHub — skipping creation."
                        )
                    else:
                        return (
                            f"Error creating repo: "
                            f"{create_resp.json().get('message', create_resp.text)}"
                        )

                # ── 3. Ensure remote 'origin' is set ─────────────────────────────
                remote_url = (
                    f"https://{github_username}:{token}@github.com/"
                    f"{github_username}/{effective_repo_name}.git"
                )
                remote_check = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True, text=True,
                )
                if remote_check.returncode != 0:
                    # No remote yet — add it
                    subprocess.run(
                        ["git", "remote", "add", "origin", remote_url],
                        check=True,
                    )
                    output_lines.append("✅ Remote 'origin' added.")
                else:
                    # Update to include token (handles token rotation)
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", remote_url],
                        check=True,
                    )

                # ── 4. Configure git identity if missing ──────────────────────────
                for cfg_key, cfg_val in [
                    ("user.email", f"{github_username}@users.noreply.github.com"),
                    ("user.name", github_username),
                ]:
                    check = subprocess.run(
                        ["git", "config", cfg_key],
                        capture_output=True, text=True,
                    )
                    if not check.stdout.strip():
                        subprocess.run(["git", "config", cfg_key, cfg_val], check=True)

                # ── 5. Stage all changes ──────────────────────────────────────────
                subprocess.run(["git", "add", "-A"], check=True)
                output_lines.append("✅ Staged all changes.")

                # ── 6. Commit (skip if nothing to commit) ─────────────────────────
                status = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True, text=True,
                )
                # Also check for staged but not-yet-committed changes
                diff_cached = subprocess.run(
                    ["git", "diff", "--cached", "--name-only"],
                    capture_output=True, text=True,
                )
                if diff_cached.stdout.strip():
                    commit_result = subprocess.run(
                        ["git", "commit", "-m", commit_message],
                        capture_output=True, text=True,
                    )
                    if commit_result.returncode != 0:
                        return f"Error committing: {commit_result.stderr}"
                    output_lines.append(f"✅ Committed: \"{commit_message}\"")
                else:
                    output_lines.append("ℹ️  Nothing new to commit — working tree clean.")

                # ── 7. Push ───────────────────────────────────────────────────────
                push_result = subprocess.run(
                    ["git", "push", "-u", "origin", branch],
                    capture_output=True, text=True,
                )
                if push_result.returncode != 0:
                    # Attempt to set upstream and push again (first push edge-case)
                    retry = subprocess.run(
                        ["git", "push", "--set-upstream", "origin", branch],
                        capture_output=True, text=True,
                    )
                    if retry.returncode != 0:
                        return (
                            f"Error pushing to GitHub:\n"
                            f"STDOUT: {push_result.stdout}\n"
                            f"STDERR: {push_result.stderr}\n"
                            f"Retry STDERR: {retry.stderr}"
                        )
                    output_lines.append(push_result.stdout or retry.stdout)
                else:
                    output_lines.append(push_result.stdout or "✅ Pushed successfully.")

                output_lines.append(
                    f"\n🔗 https://github.com/{github_username}/{effective_repo_name}/tree/{branch}"
                )
                return "\n".join(output_lines)

            finally:
                os.chdir(original_dir)

        except subprocess.CalledProcessError as e:
            return f"Git error: {e.stderr or str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"


session = DataFlowSession()


# Add roots support
@mcp.tool()
def get_working_directory():
    """Expose the working directory as a root."""
    working_dir = os.environ.get("MCP_FILESYSTEM_DIR", os.getcwd())
    return {
        "uri": f"file://{working_dir}",
        "name": "DataFlow Working Directory"
    }


@mcp.tool()
async def dataflow_load_data(file_path: str) -> str:
    """Load data from a file into the session.

    Args:
        file_path: The absolute path to the file.
    """
    return await session.load_data(file_path)


@mcp.tool()
async def dataflow_query_data(sql_query: str) -> str:
    """Query the loaded data. The data must first be loaded using the dataflow_load_data tool. The data is in the table `data`.

    Args:
        sql_query: A valid SQL query.
    """
    return await session.query_data(sql_query)


@mcp.tool()
async def dataflow_create_new_project(project_name: str) -> str:
    """Create a new project. This will create a new directory with the project name and initialize a git repository.

    Args:
        project_name: The name of the project.
    """
    return await session.create_new_project(project_name)


@mcp.tool()
async def dataflow_run_code(code: str, project_name: str = None) -> str:
    """Run Python code in a project environment or the current working directory.

    The code will be executed in the context of the specified project (if provided) or the most recently created project.
    Use this to test scripts, run analyses, or execute any Python code.

    Args:
        code: The Python code to execute.
        project_name: Optional name of the project to run the code in. If not provided, uses the current project.
    """
    return await session.run_code(code, project_name)


@mcp.tool()
async def dataflow_install_package(package: str, project_name: str = None) -> str:
    """Install a Python package in a project using uv.

    Args:
        package: The package name to install (e.g., 'requests', 'pandas==2.0.0').
        project_name: Optional name of the project. If not provided, uses the current project.
    """
    return await session.install_dependency(package, project_name)


@mcp.tool()
async def dataflow_github_push(
    commit_message: str,
    project_name: str = None,
    repo_name: str = None,
    private: bool = True,
    branch: str = "main",
    create_repo: bool = False,
) -> str:
    """Stage all changes, commit, and push the project to GitHub.

    Reads GITHUB_TOKEN from the environment (.env). Optionally creates the
    remote repository on GitHub before pushing.

    Args:
        commit_message: The git commit message.
        project_name:   Name of the local project folder to push. Defaults to
                        the current active project.
        repo_name:      Name for the GitHub repository. Defaults to the project
                        folder name.
        private:        Whether the GitHub repo should be private (default True).
                        Only used when create_repo=True.
        branch:         Branch to push to (default 'main').
        create_repo:    If True, create the GitHub repository via the API before
                        pushing. Safe to use even if the repo already exists.
    """
    return await session.github_push(
        commit_message=commit_message,
        project_name=project_name,
        repo_name=repo_name,
        private=private,
        branch=branch,
        create_repo=create_repo,
    )


if __name__ == "__main__":
    mcp.run(transport='stdio')