# Patrones DevOps y SSH (Agencia AURENIX)

Este documento centraliza los patrones estándar de Python y DevOps extraídos durante la auditoría quirúrgica de marzo de 2026. Estos fragmentos son la base para construir herramientas de automatización seguras y escalables para la agencia.

## 1. Patrón Base: Conexión SSH con Paramiko
Todos los scripts de auditoría y despliegue deben seguir este patrón de conexión robusta con `paramiko`, asegurando la política de llaves y el cierre de la conexión en un bloque `finally`.

```python
import paramiko

def execute_remote_action(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)
        
        # Ejecutar comando
        stdin, stdout, stderr = client.exec_command("docker ps -a")
        
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        if error:
            print(f"Error o Advertencia: {error}")
        print(f"Salida: {output}")
        
    except Exception as e:
        print(f"Error crítico en SSH: {str(e)}")
    finally:
        client.close()
```

## 2. Inyección de Configuración (Docker Compose)
Para modificar configuraciones en caliente dentro de servicios manejados por Coolify, el patrón es leer el archivo (`cat`), reemplazar las cadenas usando Python localmente o `sed` remoto, y volver a escribir con cat EOF.

*Rutas de Coolify conocidas:*
- `n8n`: `/data/coolify/services/ps48skwo848408oo8gg04k8k`
- `Filebrowser`: `/data/coolify/services/fsokwsssck0c0gw448w0wkcw`
- `Vaultwarden`: `/data/coolify/services/qs40wkswkws04wgc04w0sogc`

*Mounts Estándar de la Agencia:*
- `n8n`: `/data/agencia:/data/shared`
- `Filebrowser`: `/data/agencia:/srv/agencia`

## 3. Comandos Quirúrgicos de Auditoría
- **Puertos a la Escucha:** `netstat -tuln | grep LISTEN`
- **Contenedores:** `docker ps -a --format '{{.Names}} | {{.Status}} | {{.Image}}'`
- **Protección (Fail2Ban):** `which fail2ban-client && fail2ban-client status`
- **Archivos SSH:** `cat /home/aurenix_it_agent/.ssh/authorized_keys`

> **Nota Arquitectónica:** Nunca almacenar claves directamente en texto plano. En scripts futuros (como los del S5), se deberá usar un gestor de secretos o variables de entorno inyectadas.
