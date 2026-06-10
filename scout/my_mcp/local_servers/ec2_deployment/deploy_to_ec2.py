import paramiko


def deploy_to_ec2(
    host: str,
    username: str,
    key_path: str,
    image_name: str,
    container_name: str = "app",
    port: str = "80:8000"
):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, key_filename=key_path)

    commands = [
        f"docker stop {container_name} || true",
        f"docker rm {container_name} || true",
        f"docker pull {image_name}",
        f"docker run -d --name {container_name} --restart always -p {port} {image_name}"
    ]

    outputs = []
    for cmd in commands:
        _, stdout, stderr = ssh.exec_command(cmd)
        outputs.append({
            "command": cmd,
            "stdout": stdout.read().decode(),
            "stderr": stderr.read().decode()
        })

    ssh.close()
    return outputs