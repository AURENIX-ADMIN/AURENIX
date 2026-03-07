import paramiko


def deep_db_audit(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        CONTAINER = "postgresql-ps48skwo848408oo8gg04k8k"
        USER = "dVgL7FYPMsvrV5wk"
        PASS = "zewHkX8o4l94D6BCK1mFRFWH9aJPlqBk"

        print("\n--- CHECKING DATABASES ---")
        cmd_list = f"docker exec -e PGPASSWORD={PASS} {CONTAINER} psql -U {USER} -lqt"
        stdin, stdout, stderr = client.exec_command(cmd_list)
        print(stdout.read().decode().strip())

        print("\n--- TESTING PG_DUMP SAMPLE ---")
        cmd_dump = f"docker exec -e PGPASSWORD={PASS} {CONTAINER} pg_dump -U {USER} n8n | head -n 20"
        stdin, stdout, stderr = client.exec_command(cmd_dump)
        print(stdout.read().decode().strip())
        print(stderr.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    deep_db_audit("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
