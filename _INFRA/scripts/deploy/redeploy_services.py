import paramiko


def redeploy_services(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        services = [
            "/data/coolify/services/ps48skwo848408oo8gg04k8k",  # n8n
            "/data/coolify/services/qs40wkswkws04wgc04w0sogc",  # Vaultwarden
            "/data/coolify/services/fsokwsssck0c0gw448w0wkcw",  # Filebrowser
        ]

        for path in services:
            print(f"\nRedeploying {path}...")
            # Note: Coolify might use 'docker stack' or 'docker compose'.
            # We'll try 'docker compose up -d' as it's common in recent Coolify.
            stdin, stdout, stderr = client.exec_command(
                f"cd {path} && docker compose up -d"
            )
            print(stdout.read().decode().strip())
            err = stderr.read().decode().strip()
            if err:
                print(f"Info/Error: {err}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    redeploy_services("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
