import paramiko


def read_compose(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        path = "/data/coolify/services/ps48skwo848408oo8gg04k8k/docker-compose.yml"
        stdin, stdout, stderr = client.exec_command(f"cat {path}")
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    read_compose("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
