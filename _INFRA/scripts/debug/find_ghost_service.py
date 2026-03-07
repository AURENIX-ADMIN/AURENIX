import paramiko


def find_ghost(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Search for ghost in all .env files in services
        cmd = "grep -r 'GHOST' /data/coolify/services/ | head -n 20"
        stdin, stdout, stderr = client.exec_command(cmd)
        print("--- GHOST REFERENCES ---")
        print(stdout.read().decode().strip())

        # 2. List all service directories
        print("\n--- SERVICE DIRS ---")
        stdin, stdout, stderr = client.exec_command("ls -F /data/coolify/services/")
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    find_ghost("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
