import paramiko


def system_wide_ghost(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Search for ghost in all filenames
        print("\n--- FINDING ALL FILES WITH 'ghost' IN NAME ---")
        stdin, stdout, stderr = client.exec_command(
            "find /data -name '*ghost*' 2>/dev/null | head -n 20"
        )
        print(stdout.read().decode().strip())

        # 2. Search for any docker volume with ghost
        print("\n--- DOCKER VOLUMES WITH 'ghost' ---")
        stdin, stdout, stderr = client.exec_command("docker volume ls | grep ghost")
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    system_wide_ghost("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
