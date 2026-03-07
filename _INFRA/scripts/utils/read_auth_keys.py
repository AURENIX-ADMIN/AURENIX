import paramiko


def read_auth_keys(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        agent_user = "aurenix_it_agent"
        print(f"\n--- AUTHORIZED_KEYS FOR {agent_user} ---")
        stdin, stdout, stderr = client.exec_command(
            f"cat /home/{agent_user}/.ssh/authorized_keys"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    read_auth_keys("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
