import paramiko


def run_backup_script(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        print("\n--- RUNNING BACKUP SCRIPT ---")
        stdin, stdout, stderr = client.exec_command("/usr/local/bin/aurenix-backup.sh")
        print(f"Stdout: {stdout.read().decode().strip()}")
        print(f"Stderr: {stderr.read().decode().strip()}")

        print("\n--- CHECKING FILE SIZE ---")
        stdin, stdout, stderr = client.exec_command(
            "du -h /data/agencia/backups_n8n/n8n_db_backup_$(date +%F).sql"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    run_backup_script("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
