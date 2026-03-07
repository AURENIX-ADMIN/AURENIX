import paramiko
import sys
import time


def setup_m2m_bridge(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {ip}...")
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Crear usuario restringido sin contraseña local (login solo por clave SSH)
        cmd_user = "id -u aurenix_it_agent &>/dev/null || useradd -m -s /bin/bash aurenix_it_agent"
        client.exec_command(cmd_user)
        time.sleep(1)

        # 2. Configurar sudoers para comandos inofensivos de docker sin password
        # Permitiremos: docker ps, docker logs, free, df
        sudoers_rule = "aurenix_it_agent ALL=(ALL) NOPASSWD: /usr/bin/docker ps, /usr/bin/docker logs *, /usr/bin/free, /usr/bin/df"
        cmd_sudoers = f"echo '{sudoers_rule}' > /etc/sudoers.d/aurenix_it_agent && chmod 0440 /etc/sudoers.d/aurenix_it_agent"
        stdin, stdout, stderr = client.exec_command(cmd_sudoers)
        err = stderr.read().decode().strip()
        if err:
            print(f"Error sudoers: {err}")

        # 3. Generar par de claves SSH (ed25519) para 'aurenix_it_agent'
        cmd_ssh = """
        mkdir -p /home/aurenix_it_agent/.ssh
        # Generar clave si no existe
        if [ ! -f /home/aurenix_it_agent/.ssh/id_ed25519 ]; then
            ssh-keygen -t ed25519 -f /home/aurenix_it_agent/.ssh/id_ed25519 -N "" -q
        fi
        # Añadir al authorized_keys para que pueda loguearse consigo mismo (o n8n con esta clave)
        cat /home/aurenix_it_agent/.ssh/id_ed25519.pub > /home/aurenix_it_agent/.ssh/authorized_keys
        chmod 700 /home/aurenix_it_agent/.ssh
        chmod 600 /home/aurenix_it_agent/.ssh/authorized_keys
        chown -R aurenix_it_agent:aurenix_it_agent /home/aurenix_it_agent/.ssh
        
        # Devolver la clave PRIVADA por pantalla para que el agente local la guarde
        cat /home/aurenix_it_agent/.ssh/id_ed25519
        """
        stdin, stdout, stderr = client.exec_command(cmd_ssh)
        private_key = stdout.read().decode().strip()
        err_ssh = stderr.read().decode().strip()

        if err_ssh:
            print(f"Error SSH: {err_ssh}")
        else:
            print("\n--- CLAVE PRIVADA DEL AGENTE IT ---")
            print(private_key)
            print("-----------------------------------")
            print(
                "Usuario 'aurenix_it_agent' configurado correctamente con Zero Trust."
            )

    except Exception as e:
        print(f"Failed: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    setup_m2m_bridge(sys.argv[1], sys.argv[2], sys.argv[3])
