import paramiko


def verify_mounts(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. n8n check
        print("\n--- n8n VOLUME CHECK ---")
        stdin, stdout, stderr = client.exec_command(
            "docker exec n8n-ps48skwo848408oo8gg04k8k ls -la /data/shared"
        )
        print(stdout.read().decode().strip())

        # 2. FileBrowser check
        print("\n--- FileBrowser VOLUME CHECK ---")
        stdin, stdout, stderr = client.exec_command(
            "docker exec filebrowser-fsokwsssck0c0gw448w0wkcw ls -la /srv/agencia"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    verify_mounts("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
