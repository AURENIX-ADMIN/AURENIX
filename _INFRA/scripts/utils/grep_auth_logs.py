import paramiko


def grep_auth_logs(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        agent_user = "aurenix_it_agent"
        print(f"\n--- LOGS FOR {agent_user} ---")
        cmd = f"grep '{agent_user}' /var/log/auth.log || journalctl -u ssh | grep '{agent_user}'"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    grep_auth_logs("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
