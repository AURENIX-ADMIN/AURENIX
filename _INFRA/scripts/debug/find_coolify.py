import paramiko


def find_coolify_paths(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        print("\n--- FINDING N8N DIRS ---")
        stdin, stdout, stderr = client.exec_command(
            "find /data/coolify/services -name '*n8n*' -type d"
        )
        print(stdout.read().decode().strip())

        print("\n--- FINDING VAULTWARDEN DIRS ---")
        stdin, stdout, stderr = client.exec_command(
            "find /data/coolify/services -name '*vaultwarden*' -type d"
        )
        print(stdout.read().decode().strip())

        print("\n--- RECENTLY MODIFIED .env FILES ---")
        stdin, stdout, stderr = client.exec_command(
            "find /data/coolify/services -name '.env' -mtime -30"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    find_coolify_paths("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
