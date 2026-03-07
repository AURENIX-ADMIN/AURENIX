import paramiko


def surgical_dump_debug(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        DB_USER = "dVgL7FYPMsvrV5wk"
        DB_NAME = "n8n"
        DB_PASS = "zewHkX8o4l94D6BCK1mFRFWH9aJPlqBk"
        CONTAINER = "postgresql-ps48skwo848408oo8gg04k8k"

        # Try to dump and see if it even produces a single line
        print("\n--- TEST: pg_dump | head ---")
        cmd = f"docker exec -e PGPASSWORD={DB_PASS} {CONTAINER} pg_dump -U {DB_USER} {DB_NAME} | head -n 5"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"Stdout: {stdout.read().decode().strip()}")
        print(f"Stderr: {stderr.read().decode().strip()}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    surgical_dump_debug("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
