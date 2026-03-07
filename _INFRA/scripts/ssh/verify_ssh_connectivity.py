import paramiko
import os
import sys


def test_connection():
    vps_ip = "76.13.9.238"
    vps_user_agent = "aurenix_it_agent"
    key_path = (
        r"C:\Users\Usuario\Desktop\AURENIX\Claves_contraseñas\aurenix_it_agent_key.pem"
    )

    print("--- Verificando conexion SSH ---")
    print(f"Agent Target: {vps_user_agent}@{vps_ip}")
    print(f"Key: {key_path}")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        pkey = paramiko.RSAKey.from_private_key_file(key_path)
        print("[OK] Llave RSA parseada correctamente.")

        print(f"Intentando conexion como {vps_user_agent}...")
        client.connect(hostname=vps_ip, username=vps_user_agent, pkey=pkey, timeout=10)
        print(f"[OK] Conexion SSH EXITOSA como {vps_user_agent}.")

        stdin, stdout, stderr = client.exec_command("whoami && groups")
        info = stdout.read().decode().strip()
        print(f"[OK] User info: {info}")

    except Exception as e:
        print(f"[ERROR] de conexion: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    test_connection()
