import paramiko


def update_compose(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Update n8n docker-compose.yml
        n8n_path = "/data/coolify/services/ps48skwo848408oo8gg04k8k/docker-compose.yml"
        # Since I can't easily parse YAML, I'll use sed/awk or just read and replace
        stdin, stdout, stderr = client.exec_command(f"cat {n8n_path}")
        content = stdout.read().decode()

        if "/data/agencia:/data/shared" not in content:
            # Simple injection before the last volumes: section or under n8n service
            # We look for 'volumes:' under the n8n service.
            new_content = content.replace(
                "- ps48skwo848408oo8gg04k8k_n8n-data:/home/node/.n8n",
                "- ps48skwo848408oo8gg04k8k_n8n-data:/home/node/.n8n\n      - /data/agencia:/data/shared",
            )
            # Write back
            stdin, stdout, stderr = client.exec_command(
                f"cat << 'EOF' > {n8n_path}\n{new_content}\nEOF"
            )
            print("n8n docker-compose.yml updated.")
        else:
            print("n8n docker-compose.yml already updated.")

        # 2. Update FileBrowser docker-compose.yml
        fb_path = "/data/coolify/services/fsokwsssck0c0gw448w0wkcw/docker-compose.yml"
        stdin, stdout, stderr = client.exec_command(f"cat {fb_path}")
        content_fb = stdout.read().decode()

        if "/data/agencia:/srv/agencia" not in content_fb:
            # Inject volume for filebrowser
            # Usually filebrowser has a volume for data. We'll add our shared folder.
            # I'll look for a common volume line to anchor.
            new_content_fb = content_fb.replace(
                "volumes:", "volumes:\n      - /data/agencia:/srv/agencia"
            )
            stdin, stdout, stderr = client.exec_command(
                f"cat << 'EOF' > {fb_path}\n{new_content_fb}\nEOF"
            )
            print("FileBrowser docker-compose.yml updated.")
        else:
            print("FileBrowser docker-compose.yml already updated.")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    update_compose("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
