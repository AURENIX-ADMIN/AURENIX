import paramiko
import sys


def surgical_audit(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # 1. Docker
        print("\n--- DOCKER CONTAINERS ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps -a --format '{{.Names}} | {{.Status}} | {{.Image}}'"
        )
        print(stdout.read().decode().strip())

        # 2. Crontab
        print("\n--- CRONTAB ROOT ---")
        stdin, stdout, stderr = client.exec_command("crontab -l")
        print(stdout.read().decode().strip())

        # 3. Network Ports
        print("\n--- LISTENING PORTS ---")
        stdin, stdout, stderr = client.exec_command("netstat -tuln | grep LISTEN")
        print(stdout.read().decode().strip())

        # 4. Fail2ban
        print("\n--- FAIL2BAN CHECK ---")
        stdin, stdout, stderr = client.exec_command(
            "which fail2ban-client && fail2ban-client status"
        )
        print(stdout.read().decode().strip())
        err = stderr.read().decode().strip()
        if err:
            print(f"Info: {err}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    surgical_audit("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
