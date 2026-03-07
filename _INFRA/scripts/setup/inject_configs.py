import paramiko


def inject_configs(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Update n8n .env
        n8n_env_path = "/data/coolify/services/ps48skwo848408oo8gg04k8k/.env"
        n8n_smtp = """
# AURENIX SMTP Config (Jose)
N8N_EMAIL_MODE=smtp
N8N_SMTP_HOST=smtp.hostinger.com
N8N_SMTP_PORT=465
N8N_SMTP_USER=jose@aurenix.cloud
N8N_SMTP_PASS=sebas_JOSE_2026_
N8N_SMTP_SENDER=jose@aurenix.cloud
N8N_SMTP_SSL=true
"""
        client.exec_command(f"echo '{n8n_smtp}' >> {n8n_env_path}")
        print("n8n .env updated.")

        # 2. Update Vaultwarden .env
        vw_env_path = "/data/coolify/services/qs40wkswkws04wgc04w0sogc/.env"
        vw_smtp = """
# AURENIX SMTP Config (Sebas)
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_SECURITY=force_tls
SMTP_USERNAME=sebas@aurenix.cloud
SMTP_PASSWORD=s#V2Y@LjJAr
SMTP_FROM=sebas@aurenix.cloud
"""
        client.exec_command(f"echo '{vw_smtp}' >> {vw_env_path}")
        print("Vaultwarden .env updated.")

        # 3. Create shared directories (Safety check)
        client.exec_command(
            "mkdir -p /data/agencia/backups_n8n /data/agencia/documentos && chmod -R 777 /data/agencia"
        )
        print("Directories created/verified.")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    inject_configs("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
