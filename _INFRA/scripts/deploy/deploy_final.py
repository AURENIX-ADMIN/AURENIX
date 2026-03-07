import paramiko


def deploy_final_scripts(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Backup script (Rotate 30 days)
        # Using real n8n DB credentials
        backup_script = """#!/bin/bash
BACKUP_DIR="/data/agencia/backups_n8n"
DB_USER="dVgL7FYPMsvrV5wk"
DB_NAME="n8n"
PG_CONTAINER=$(docker ps -q -f name=postgresql-ps48skwo848408oo8gg04k8k)

mkdir -p $BACKUP_DIR
docker exec -t $PG_CONTAINER pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/n8n_db_backup_$(date +\%F).sql
# Delete files older than 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
echo "Backup completed for AURENIX DB."
"""

        # 2. Health check script
        health_script = """#!/bin/bash
REPORT="/data/agencia/health_status.txt"
echo "--- AURENIX HEALTH STATUS ($(date)) ---" > $REPORT
echo "Uptime: $(uptime -p)" >> $REPORT
echo "Memory: $(free -m | grep Mem | awk '{print $3\"MB / \"$2\"MB\"}')" >> $REPORT
echo "Disk: $(df -h / | tail -1 | awk '{print $5}')" >> $REPORT
echo "Containers:" >> $REPORT
docker ps --format '{{.Names}} | {{.Status}}' >> $REPORT
echo "UFW: $(ufw status | head -1)" >> $REPORT
"""

        # Upload scripts
        client.exec_command(
            f"cat << 'EOF' > /usr/local/bin/aurenix-backup.sh\n{backup_script}\nEOF"
        )
        client.exec_command(
            f"cat << 'EOF' > /usr/local/bin/aurenix-health.sh\n{health_script}\nEOF"
        )
        client.exec_command(
            "chmod +x /usr/local/bin/aurenix-backup.sh /usr/local/bin/aurenix-health.sh"
        )

        # 3. Setup Crontab
        # 02:00 AM Backup
        # Every 5 min Health Check
        cron_tasks = """
0 2 * * * /usr/local/bin/aurenix-backup.sh
*/5 * * * * /usr/local/bin/aurenix-health.sh
"""
        client.exec_command(
            f"(crontab -l 2>/dev/null | grep -v 'aurenix'; echo '{cron_tasks}') | crontab -"
        )

        print("Final scripts and crons deployed.")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    deploy_final_scripts("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
