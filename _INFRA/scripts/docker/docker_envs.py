import paramiko
import json


def get_docker_envs(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # Get all container names
        stdin, stdout, stderr = client.exec_command("docker ps --format '{{.Names}}'")
        containers = stdout.read().decode().strip().split("\n")

        all_envs = {}
        for container in containers:
            if not container:
                continue
            cmd = f"docker inspect {container} --format '{{{{json .Config.Env}}}}'"
            stdin, stdout, stderr = client.exec_command(cmd)
            env_json = stdout.read().decode().strip()
            if env_json:
                all_envs[container] = json.loads(env_json)

        print(json.dumps(all_envs, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    get_docker_envs("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
