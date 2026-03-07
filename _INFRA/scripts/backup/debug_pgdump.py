import paramiko


def debug_backup(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        DB_USER = "dVgL7FYPMsvrV5wk"
        DB_NAME = "n8n"
        CONTAINER = "postgresql-ps48skwo848408oo8gg04k8k"

        print("\n--- TESTING PG_DUMP DIRECTLY ---")
        cmd = f"docker exec {CONTAINER} pg_dump -U {DB_USER} {DB_NAME}"
        stdin, stdout, stderr = client.exec_command(cmd)

        out = stdout.read(100).decode()  # Just first 100 bytes
        err = stderr.read().decode()

        print(f"Stdout (first 100b): {out}...")
        print(f"Stderr: {err}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    debug_backup("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
