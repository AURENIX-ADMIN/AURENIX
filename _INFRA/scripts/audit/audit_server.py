import paramiko
import sys
import os


def check_and_backup(ip, user, password, local_backup_dir):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"--- CONECTANDO A {ip} ---")
        client.connect(hostname=ip, username=user, password=password, timeout=15)

        # 1. Verificar Uptime (¿Se reinició a las 04:00?)
        stdin, stdout, stderr = client.exec_command("uptime -p")
        print(f"Uptime del Servidor: {stdout.read().decode().strip()}")

        # 2. Verificar si el Cron de las 02:00 AM funcionó
        stdin, stdout, stderr = client.exec_command("ls -la /data/agencia/backups_n8n/")
        print(
            f"\nBackups automáticos n8n encontrados en VPS:\n{stdout.read().decode().strip()}"
        )

        # 3. Verificar si se montaron los volúmenes en Coolify (n8n y Filebrowser)
        cmd_n8n_vols = "docker inspect $(docker ps -q -f name=n8n) --format '{{json .Mounts}}' 2>/dev/null | grep '/data/agencia'"
        stdin, stdout, stderr = client.exec_command(cmd_n8n_vols)
        n8n_mounts = stdout.read().decode().strip()
        print(
            f"\nVolúmenes de n8n montados en /data/agencia: {'SÍ' if n8n_mounts else 'NO (Falta hacerlo en Coolify)'}"
        )

        # 4. CREAR BACKUP MANUAL COMPLETO DE SEGURIDAD
        print("\n--- INICIANDO BACKUP MANUAL COMPLETO EN EL VPS ---")
        cmd_backup = """
        mkdir -p /data/agencia/backups_manual
        # Backup n8n Postgres
        PG_CONTAINER=$(docker ps -a -q -f name=postgresql-)
        if [ ! -z "$PG_CONTAINER" ]; then
            docker exec $PG_CONTAINER pg_dump -U n8n n8n > /data/agencia/backups_manual/n8n_db_manual.sql
            echo "Base de datos n8n exportada."
        fi
        
        # Comprimir todos los backups y configs importantes (ej. Coolify y datos agencia)
        cd /data/agencia
        tar -czf /data/agencia/backups_manual/VPS_Complete_Backup_Now.tar.gz backups_manual/n8n_db_manual.sql backups_n8n/
        echo "Contenedor de backup creado: /data/agencia/backups_manual/VPS_Complete_Backup_Now.tar.gz"
        """
        stdin, stdout, stderr = client.exec_command(cmd_backup)
        print(stdout.read().decode().strip())
        err = stderr.read().decode().strip()
        if err:
            print(f"Errores en backup: {err}")

        # 5. DESCARGAR EL BACKUP AL DISCO LOCAL
        print(f"\n--- DESCARGANDO BACKUP A DISCO LOCAL ({local_backup_dir}) ---")
        os.makedirs(local_backup_dir, exist_ok=True)
        sftp = client.open_sftp()
        remote_path = "/data/agencia/backups_manual/VPS_Complete_Backup_Now.tar.gz"
        local_path = os.path.join(local_backup_dir, "VPS_Complete_Backup_Now.tar.gz")

        sftp.get(remote_path, local_path)
        print(f"¡Backup descargado y asegurado en {local_path}!")
        sftp.close()

    except Exception as e:
        print(f"Error crítico: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    ip = sys.argv[1]
    pwd = sys.argv[2]
    local_dir = r"C:\Users\Usuario\Desktop\AURENIX\Backups"
    check_and_backup(ip, "root", pwd, local_dir)
