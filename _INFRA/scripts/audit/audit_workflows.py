import paramiko
import sys
import json


def list_n8n_workflows(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Conectando a {ip} para auditar flujos de n8n...")
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Obtener el usuario y db reales del config de n8n
        cmd_env = "docker inspect $(docker ps -a -q -f name=n8n) --format '{{json .Config.Env}}' 2>/dev/null"
        stdin, stdout, stderr = client.exec_command(cmd_env)
        env_vars_json = stdout.read().decode().strip()

        db_user = "n8n"
        db_name = "n8n"

        if env_vars_json:
            env_vars = json.loads(env_vars_json)
            for var in env_vars:
                if var.startswith("DB_POSTGRESDB_USER="):
                    db_user = var.split("=")[1]
                elif var.startswith("DB_POSTGRESDB_DATABASE="):
                    db_name = var.split("=")[1]

        print(f"Usando DB User: {db_user}, DB Name: {db_name}")

        # 2. Consultar PostgreSQL
        cmd_sql = f"""
        PG_CONTAINER=$(docker ps -a -q -f name=postgresql-)
        docker exec $PG_CONTAINER psql -U {db_user} -d {db_name} -c "SELECT id, name, active FROM workflow_entity;"
        """

        stdin, stdout, stderr = client.exec_command(cmd_sql)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()

        if out:
            print("\n--- FLUJOS DE N8N ENCONTRADOS ---")
            print(out)
        if err:
            print(f"\nErrores/Warnings: {err}")

    except Exception as e:
        print(f"Error de conexión: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    list_n8n_workflows(sys.argv[1], sys.argv[2], sys.argv[3])
