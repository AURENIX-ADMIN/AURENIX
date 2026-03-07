import paramiko


def deploy_rsa_classic(ip, user, password, pub_key):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        agent_user = "aurenix_it_agent"
        print(f"\n--- DEPLOYING CLASSIC RSA KEY FOR {agent_user} ---")

        # Overwrite authorized_keys with the new Classic RSA key
        cmd = f"echo '{pub_key}' > /home/{agent_user}/.ssh/authorized_keys"
        client.exec_command(cmd)

        # Ensure permissions
        client.exec_command(
            f"chown {agent_user}:{agent_user} /home/{agent_user}/.ssh/authorized_keys"
        )
        client.exec_command(f"chmod 600 /home/{agent_user}/.ssh/authorized_keys")

        print("Classic RSA Public Key deployed.")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    pub_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCyBnCetoQC/2VgKt5H/SPO1RhgaRm//tvwikreu8zBz24k4AMCfwmEHbDTuZfAEvTn0CQxxclB95MT2mP1Xl2s9Zjhe36ci/P882f9/qXvY/IwqW0QAK1eH+GwuX2LNVPKPK9so740qN6IvIKhO7BWKyj7n39yichsuUEFVzDfBGj/tctTZdfSN7a7NnZ6uv7fZoSkXikuP4XA5rbRp69Dp735H0mBBS4SgORyFDgecriNeYfhcNIQsWz7c35ZQBPIl8hOkwv2Zwb8LyUPWlUR0vAcLsqLseh+7+HXiAxdPEeyijpI45gt9AEl3j7Vnd0NuIClQcejLeT0R3/eoA+e4/BsbM/E+x2ikTMzNqlqwgnIp8H9eUyZNKNKyZrcH/pe5zvHkmzcIoMDxTUQHaP66JnjSC+pHLYm9o8fhZB3J+5gU8LS8TcwAOUW6y+/+qliZwb4h9KuqMCTi3kBSOCCbMZb0fDStfPV1rJZaanbL171Ih39dXwENccwvr20+4diXG2Qn9Gn534tIdLvEbktmc1/vRhIN+UBXHHt5DAmSJkoEYI9jq4tCfbqLAp0hoyJwQN30EMseQpC6bBr6xVrL7Ew3T4GwY6JJDMc09EsCu1eWnhE6FsJMCltji7zW++u7iX3FI4WWfgF0QEXMaMI70IFndZPgIADhjoS94HYdw=="
    deploy_rsa_classic("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE", pub_key)
