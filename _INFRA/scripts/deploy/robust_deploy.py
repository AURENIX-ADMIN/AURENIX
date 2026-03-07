import paramiko
import os


def robust_deploy(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)
        sftp = client.open_sftp()

        # 1. Backup script
        backup_content = """#!/bin/bash
BACKUP_DIR="/data/agencia/backups_n8n"
DB_USER="dVgL7FYPMsvrV5wk"
DB_NAME="n8n"
DB_PASS="zewHkX8o4l94D6BCK1mFRFWH9aJPlqBk"
PG_CONTAINER=$(docker ps -q -f name=postgresql-ps48skwo848408oo8gg04k8k)

mkdir -p $BACKUP_DIR
# Remove -t, use -i or no flags for redirection.
docker exec -e PGPASSWORD=$DB_PASS $PG_CONTAINER pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/n8n_db_backup_$(date +%F).sql
# Delete files older than 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
echo "Backup completed for AURENIX DB."
"""
        with sftp.open("/usr/local/bin/aurenix-backup.sh", "w") as f:
            f.write(backup_content)

        # 2. Health script
        health_content = """#!/bin/bash
REPORT="/data/agencia/health_status.txt"
echo "--- AURENIX HEALTH STATUS ($(date)) ---" > $REPORT
echo "Uptime: $(uptime -p)" >> $REPORT
echo "Memory: $(free -m | grep Mem | awk '{print $3"MB / "$2"MB"}')" >> $REPORT
echo "Disk: $(df -h / | tail -1 | awk '{print $5}')" >> $REPORT
echo "Containers:" >> $REPORT
docker ps --format '{{.Names}} | {{.Status}}' >> $REPORT
echo "UFW: $(ufw status | head -1)" >> $REPORT
"""
        with sftp.open("/usr/local/bin/aurenix-health.sh", "w") as f:
            f.write(health_content)

        sftp.close()

        # Set permissions
        client.exec_command(
            "chmod +x /usr/local/bin/aurenix-backup.sh /usr/local/bin/aurenix-health.sh"
        )
        print("Scripts deployed robustly via SFTP.")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    robust_deploy("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
