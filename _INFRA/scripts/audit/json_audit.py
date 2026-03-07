import paramiko
import json


def get_clean_audit(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    results = {}
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # Helper to run and get output
        def run(cmd):
            stdin, stdout, stderr = client.exec_command(cmd)
            return stdout.read().decode().strip()

        results["ufw"] = run("ufw status")
        results["docker"] = run("docker ps --format '{{.Names}}'").split("\n")
        results["cron"] = run("crontab -l")
        results["fail2ban"] = run("fail2ban-client status || echo 'Not installed'")
        results["storage"] = run("ls -R /data/agencia")

        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    get_clean_audit("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
