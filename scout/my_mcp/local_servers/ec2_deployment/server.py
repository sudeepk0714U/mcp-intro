import os
from mcp.server.fastmcp import FastMCP
from deploy_to_ec2 import deploy_to_ec2
from verify_deployment import verify_deployment
from rollback_deployment import rollback_deployment

mcp = FastMCP("ec2-deployment")

EC2_HOST = os.getenv("EC2_HOST")
EC2_USER = os.getenv("EC2_USER")
EC2_KEY_PATH = os.getenv("EC2_KEY_PATH")


@mcp.tool()
def deploy(image_name: str, container_name: str = "app", port: str = "80:8000"):
    """Deploy any Docker image to EC2.
    image_name: full image path e.g. ghcr.io/sudeepk0714u/todo-app:latest
    container_name: name for the container e.g. todo-app
    port: port mapping e.g. 80:8000 or 8080:8000
    """
    return deploy_to_ec2(
        EC2_HOST, EC2_USER, EC2_KEY_PATH,
        image_name, container_name, port
    )


@mcp.tool()
def verify(app_name: str):
    """Verify a deployed app is running.
    app_name: used to hit http://EC2_HOST/<app_name>/health
    """
    return verify_deployment(f"http://{EC2_HOST}")


@mcp.tool()
def rollback(previous_image: str, container_name: str = "app"):
    """Rollback any container to a previous image.
    previous_image: e.g. ghcr.io/sudeepk0714u/todo-app:v1.0
    container_name: name of the container to rollback
    """
    return rollback_deployment(
        EC2_HOST, EC2_USER, EC2_KEY_PATH,
        previous_image, container_name
    )


@mcp.tool()
def list_containers():
    """List all running Docker containers on EC2."""
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=EC2_HOST, username=EC2_USER, key_filename=EC2_KEY_PATH)
    _, stdout, _ = ssh.exec_command("docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'")
    output = stdout.read().decode()
    ssh.close()
    return {"containers": output}


@mcp.tool()
def stop_container(container_name: str):
    """Stop a running container on EC2 by name."""
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=EC2_HOST, username=EC2_USER, key_filename=EC2_KEY_PATH)
    _, stdout, stderr = ssh.exec_command(f"docker stop {container_name}")
    output = stdout.read().decode()
    ssh.close()
    return {"stopped": container_name, "output": output}


if __name__ == "__main__":
    mcp.run()