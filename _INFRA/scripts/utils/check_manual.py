import paramiko


def check_manual_backups(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        print("\n--- HOST LISTING /data/agencia/backups_manual ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /data/agencia/backups_manual"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    check_manual_backups("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
