import paramiko


def read_auth_logs(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        print("\n--- RECENT AUTH LOGS ---")
        # Check /var/log/auth.log (standard on Ubuntu/Debian) or journalctl
        stdin, stdout, stderr = client.exec_command("tail -n 50 /var/log/auth.log")
        logs = stdout.read().decode().strip()
        if not logs:
            stdin, stdout, stderr = client.exec_command(
                "journalctl -u ssh --no-pager -n 50"
            )
            logs = stdout.read().decode().strip()
        print(logs)

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    read_auth_logs("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
