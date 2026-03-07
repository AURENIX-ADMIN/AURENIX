import paramiko


def audit_agent_ssh(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        agent_user = "aurenix_it_agent"
        print(f"\n--- AUDITING USER: {agent_user} ---")

        # 1. Check if user exists
        stdin, stdout, stderr = client.exec_command(f"id {agent_user}")
        print(f"User ID: {stdout.read().decode().strip() or 'User not found'}")

        # 2. Check .ssh directory and authorized_keys
        print("\n--- SHH DIRECTORY PERMISSIONS ---")
        stdin, stdout, stderr = client.exec_command(f"ls -la /home/{agent_user}/.ssh/")
        print(stdout.read().decode().strip())

        # 3. Check authorized_keys content (redacted)
        print("\n--- AUTHORIZED_KEYS CONTENT ---")
        stdin, stdout, stderr = client.exec_command(
            f"cat /home/{agent_user}/.ssh/authorized_keys"
        )
        print(f"Key count: {len(stdout.readlines())}")

        # 4. Check sshd config for PubkeyAuthentication
        print("\n--- SSHD CONFIG SNIPPET ---")
        stdin, stdout, stderr = client.exec_command(
            "grep -E 'PubkeyAuthentication|AuthorizedKeysFile' /etc/ssh/sshd_config"
        )
        print(stdout.read().decode().strip())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    audit_agent_ssh("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
