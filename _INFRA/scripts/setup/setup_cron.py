import paramiko
import sys


def setup_cron_tasks(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {ip} to setup cron maintenance and backups...")
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Tarea de Mantenimiento y Reinicio en Diferido (04:00 AM)
        # Usaremos 'at' para programarlo como un One-Shot (lo ejecuta una vez y listo)
        # Instalamos 'at' de forma silenciosa si no estuviera.
        cmd_at = """
        apt-get install -y at >/dev/null 2>&1
        echo 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && reboot' | at 04:00
        """
        stdin, stdout, stderr = client.exec_command(cmd_at)
        time_msg = (
            stderr.read().decode().strip()
        )  # 'at' escupe la confirmación por stderr
        print("--- REINICIO PROGRAMADO ---")
        print(time_msg)

        # 2. Backup de Base de Datos de n8n Postgres (Diario a las 02:00 AM)
        # Esto exportará el PostgreSQL de n8n al volumen compartido /data/agencia/backups_n8n
        # De esta forma el usuario lo puede descargar vía Filebrowser.
        cron_job = "0 2 * * * docker exec $(docker ps -a -q -f name=postgresql-ps48skwo848408oo8gg04k8k) pg_dump -U n8n n8n > /data/agencia/backups_n8n/n8n_db_backup_\$(date +\\%F).sql"

        # Añadir al crontab si no existe
        cmd_cron = f"""
        (crontab -l 2>/dev/null | grep -v 'pg_dump'; echo '{cron_job}') | crontab -
        crontab -l | tail -n 1
        """
        stdin, stdout, stderr = client.exec_command(cmd_cron)
        cron_msg = stdout.read().decode().strip()
        print("\n--- CRON BACKUP N8N CONFIGURADO ---")
        print(f"Tarea insertada: {cron_msg}")

    except Exception as e:
        print(f"Failed: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    setup_cron_tasks(sys.argv[1], sys.argv[2], sys.argv[3])
