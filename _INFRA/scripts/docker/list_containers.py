import paramiko


def list_all_containers(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)
        stdin, stdout, stderr = client.exec_command(
            "docker ps -a --format '{{.Names}} | {{.Status}}'"
        )
        print(stdout.read().decode().strip())
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    list_all_containers("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
