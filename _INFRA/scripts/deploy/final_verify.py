import paramiko


def final_verify(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Trigger Backup
        print("\n--- TRIGGERING MANUAL BACKUP ---")
        client.exec_command("/usr/local/bin/aurenix-backup.sh")

        # 2. Check Backup Size
        print("\n--- CHECKING BACKUP SIZE ---")
        stdin, stdout, stderr = client.exec_command("ls -la /data/agencia/backups_n8n")
        print(stdout.read().decode().strip())

        # 3. Trigger Health Check
        print("\n--- TRIGGERING HEALTH CHECK ---")
        client.exec_command("/usr/local/bin/aurenix-health.sh")

        # 4. Check Health Report
        print("\n--- CHECKING HEALTH REPORT ---")
        stdin, stdout, stderr = client.exec_command(
            "cat /data/agencia/health_status.txt"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    final_verify("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
