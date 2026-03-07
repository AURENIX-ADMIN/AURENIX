import paramiko


def debug_n8n(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        print("\n--- DOCKER INSPECT N8N MOUNTS ---")
        stdin, stdout, stderr = client.exec_command(
            "docker inspect n8n-ps48skwo848408oo8gg04k8k --format '{{json .Mounts}}'"
        )
        print(stdout.read().decode().strip())

        print("\n--- N8N CONTAINER LOGS (Last 20 lines) ---")
        stdin, stdout, stderr = client.exec_command(
            "docker logs --tail 20 n8n-ps48skwo848408oo8gg04k8k"
        )
        print(stdout.read().decode().strip())
        print(stderr.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    debug_n8n("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
