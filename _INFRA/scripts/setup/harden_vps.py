import paramiko
import sys


def harden_vps(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"--- INICIANDO HARDENING EN {ip} ---")
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        commands = [
            # 1. Install Fail2ban
            "apt-get update && apt-get install -y fail2ban",
            "systemctl enable fail2ban",
            "systemctl start fail2ban",
            # 2. Setup UFW (Cautious)
            "ufw allow 22/tcp",
            "ufw allow 80/tcp",
            "ufw allow 443/tcp",
            "ufw allow 8000/tcp",  # Coolify
            "ufw allow 6379/tcp",  # Redis (if needed externally, but usually internal) - we'll keep it for now as per previous audit
            "ufw --force enable",
            # 3. Verify
            "ufw status verbose",
            "fail2ban-client status sshd",
        ]

        for cmd in commands:
            print(f"\nExecuting: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode().strip())
            err = stderr.read().decode().strip()
            if err:
                print(f"Info/Error: {err}")

    except Exception as e:
        print(f"Failed: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    harden_vps("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
