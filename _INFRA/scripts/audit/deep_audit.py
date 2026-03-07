import paramiko
import sys


def audit_server(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"--- INICIANDO AUDITORÍA EN {ip} ---")
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        commands = {
            "Uptime": "uptime -p",
            "UFW Status": "ufw status verbose",
            "Fail2ban Status": "fail2ban-client status",
            "Docker Containers": "docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'",
            "Cron Jobs (root)": "crontab -l",
            "Shared Folders": "ls -la /data/agencia",
            "Disk Space": "df -h /",
            "Memory Usage": "free -m",
        }

        for name, cmd in commands.items():
            print(f"\n>>> {name} ({cmd})")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            if out:
                print(out)
            if err:
                print(f"Error/Info: {err}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    audit_server("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
