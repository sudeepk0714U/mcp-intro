import paramiko


def rollback_deployment(
    host: str,
    username: str,
    key_path: str,
    previous_image: str,
    container_name: str = "app"
):

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    ssh.connect(
        hostname=host,
        username=username,
        key_filename=key_path
    )

    commands = [

        f"docker stop {container_name}",

        f"docker rm {container_name}",

        f"""
docker run -d \
--name {container_name} \
-p 80:8000 \
{previous_image}
"""
    ]

    for cmd in commands:

        ssh.exec_command(cmd)

    ssh.close()

    return {
        "success": True
    }