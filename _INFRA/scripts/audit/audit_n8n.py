import paramiko
import sys
import json


def run_n8n_audit(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # Obtener variables de entorno de n8n para ver conexión a BBDD
        cmd_env = "docker inspect $(docker ps -a -q -f name=n8n) --format '{{json .Config.Env}}' 2>/dev/null"
        stdin, stdout, stderr = client.exec_command(cmd_env)
        env_vars_json = stdout.read().decode().strip()

        print("\n--- Analizando Entorno de n8n ---")
        if env_vars_json:
            try:
                env_vars = json.loads(env_vars_json)
                db_type = "sqlite (default)"
                for var in env_vars:
                    if var.startswith("DB_TYPE="):
                        db_type = var.split("=")[1]
                        break
                print(f"Tipo de Base de Datos n8n: {db_type}")

                # Ocultar secretos, imprimir resto
                for var in env_vars:
                    if "DB_POSTGRESDB_USER" in var or "POSTGRES" in var:
                        print(f"Detectada config Postgres: {var.split('=')[0]}=***")
            except json.JSONDecodeError:
                print("No se pudo parsear el JSON de variables de entorno.")

        # Listar archivos en ~/.n8n
        cmd_files = "docker exec $(docker ps -qf name=n8n) ls -la /home/node/.n8n"
        stdin, stdout, stderr = client.exec_command(cmd_files)
        files = stdout.read().decode().strip()
        print("\n--- Archivos en /home/node/.n8n ---")
        print(files)

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    run_n8n_audit(sys.argv[1], sys.argv[2], sys.argv[3])
