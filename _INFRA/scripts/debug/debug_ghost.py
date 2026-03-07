import paramiko


def debug_ghost(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        container = "ghost-to8gos8g8c8gg04k8k8c0osgg"
        print(f"\n--- INSPECTING GHOST: {container} ---")

        # 1. Check status and why it exited
        stdin, stdout, stderr = client.exec_command(
            f"docker inspect {container} --format '{{{{.State.Status}}}} | {{{{.State.ExitCode}}}} | {{{{.State.Error}}}}'"
        )
        print(f"Status/Exit/Error: {stdout.read().decode().strip()}")

        # 2. Check logs
        print("\n--- GHOST LOGS (Last 50 lines) ---")
        stdin, stdout, stderr = client.exec_command(
            f"docker logs --tail 50 {container}"
        )
        print(stdout.read().decode().strip())
        print(stderr.read().decode().strip())

        # 3. Check env vars (redacted)
        print("\n--- GHOST ENV VARS ---")
        stdin, stdout, stderr = client.exec_command(
            f"docker inspect {container} --format '{{{{json .Config.Env}}}}'"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    debug_ghost("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
