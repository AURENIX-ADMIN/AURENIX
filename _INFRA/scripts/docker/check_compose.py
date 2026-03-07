import paramiko


def check_compose(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        paths = [
            "/data/coolify/services/ps48skwo848408oo8gg04k8k/docker-compose.yml",
            "/data/coolify/services/qs40wkswkws04wgc04w0sogc/docker-compose.yml",
            "/data/coolify/services/fsokwsssck0c0gw448w0wkcw/docker-compose.yml",
        ]

        for p in paths:
            stdin, stdout, stderr = client.exec_command(f"ls -l {p}")
            print(f"Checking {p}: {stdout.read().decode().strip() or 'Not found'}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    check_compose("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
