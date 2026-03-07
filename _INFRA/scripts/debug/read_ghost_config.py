import paramiko


def read_ghost_config(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        path = "/data/coolify/services/to8gos8g8c8gg0k8k8c0osgg"

        print("\n--- GHOST .env ---")
        stdin, stdout, stderr = client.exec_command(f"cat {path}/.env")
        print(stdout.read().decode().strip())

        print("\n--- GHOST docker-compose.yml ---")
        stdin, stdout, stderr = client.exec_command(f"cat {path}/docker-compose.yml")
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    read_ghost_config("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
