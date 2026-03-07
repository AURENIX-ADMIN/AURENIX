import paramiko


def global_find_compose(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        print("\n--- FINDING ALL docker-compose.yml ---")
        stdin, stdout, stderr = client.exec_command(
            "find /data/coolify/services -name 'docker-compose.yml'"
        )
        print(stdout.read().decode().strip())

        print("\n--- FINDING ALL .env ---")
        stdin, stdout, stderr = client.exec_command(
            "find /data/coolify/services -name '.env'"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    global_find_compose("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
