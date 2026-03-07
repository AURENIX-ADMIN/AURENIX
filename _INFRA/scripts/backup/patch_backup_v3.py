import paramiko


def patch_backup_v3(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # Patched Backup script without -t
        backup_script = """#!/bin/bash
BACKUP_DIR="/data/agencia/backups_n8n"
DB_USER="dVgL7FYPMsvrV5wk"
DB_NAME="n8n"
DB_PASS="zewHkX8o4l94D6BCK1mFRFWH9aJPlqBk"
PG_CONTAINER=$(docker ps -q -f name=postgresql-ps48skwo848408oo8gg04k8k)

mkdir -p $BACKUP_DIR
# Using -i instead of -t, or no flags. -t messes up redirection.
docker exec -e PGPASSWORD=$DB_PASS $PG_CONTAINER pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/n8n_db_backup_$(date +\%F).sql
# Delete files older than 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
echo "Backup completed for AURENIX DB."
"""

        client.exec_command(
            f"cat << 'EOF' > /usr/local/bin/aurenix-backup.sh\n{backup_script}\nEOF"
        )
        client.exec_command("chmod +x /usr/local/bin/aurenix-backup.sh")
        print("Backup script patched V3.")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    patch_backup_v3("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
