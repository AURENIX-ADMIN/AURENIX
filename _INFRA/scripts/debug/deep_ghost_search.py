import paramiko


def deep_ghost_search(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Search for ANY container with ghost
        print("\n--- SEARCHING FOR GHOST CONTAINERS ---")
        stdin, stdout, stderr = client.exec_command("docker ps -a | grep ghost")
        print(stdout.read().decode().strip())

        # 2. Search for ghost in docker logs (if any)
        print("\n--- SEARCHING FOR GHOST IN DOCKER LOGS ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps -a --format '{{.Names}}' | xargs -I {} docker logs --tail 1 {} 2>&1 | grep ghost"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    deep_ghost_search("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
