import paramiko


def read_envs(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        files = [
            "/data/coolify/services/ps48skwo848408oo8gg04k8k/.env",
            "/data/coolify/services/qs40wkswkws04wgc04w0sogc/.env",
            "/data/coolify/services/fsokwsssck0c0gw448w0wkcw/.env",
        ]

        for f in files:
            print(f"\n--- FILE: {f} ---")
            stdin, stdout, stderr = client.exec_command(f"cat {f}")
            content = stdout.read().decode().strip()
            # Mask passwords for output
            for line in content.split("\n"):
                if "PASS" in line or "SECRET" in line or "KEY" in line:
                    print(line.split("=")[0] + "=********")
                else:
                    print(line)

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    read_envs("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
