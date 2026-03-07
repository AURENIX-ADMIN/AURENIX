import paramiko
import sys


def setup_volumes(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {ip} to setup shared volumes...")
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Crear directorios base en el Host
        cmd_dirs = """
        mkdir -p /data/agencia/backups_n8n
        mkdir -p /data/agencia/documentos
        # Dar permisos totales 777 a la carpeta entera de forma recursiva (para evitar clashing de usuarios docker n8n=1000/node)
        chmod -R 777 /data/agencia
        chown -R root:root /data/agencia
        echo 'Directorios creados en /data/agencia con r/w recursivo.'
        """
        stdin, stdout, stderr = client.exec_command(cmd_dirs)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if out:
            print(out)
        if err:
            print(f"Warning/Error: {err}")

        # Nota sobre Coolify: Inyectar volumens directamente por `docker run` o `sqlite` en Coolify es riesgoso sin hacerlo
        # por la API interna o el Panel. Por tanto, preparamos la carpeta a nivel Host,
        # y le dejamos un script que el usuario (o yo mediante la API) pueda aplicar luego en la configuración.

        print("\n--- PASOS SIGUIENTES (COOLIFY UI) ---")
        print(
            "El sistema operativo está listo. Cuando el socio termine a la madrugada:"
        )
        print("1. Ve a Coolify -> Project -> n8n -> Storages.")
        print("   Añade: Host Path: /data/agencia | Container Path: /data/shared")
        print("2. Ve a Coolify -> Project -> FileBrowser -> Storages.")
        print("   Añade: Host Path: /data/agencia | Container Path: /srv/agencia")
        print("3. Reinicia ambos contenedores.")

    except Exception as e:
        print(f"Failed: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    setup_volumes(sys.argv[1], sys.argv[2], sys.argv[3])
