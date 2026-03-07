import paramiko


def check_script_content(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        print("\n--- SCRIPT CONTENT ---")
        stdin, stdout, stderr = client.exec_command(
            "cat /usr/local/bin/aurenix-backup.sh"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    check_script_content("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
