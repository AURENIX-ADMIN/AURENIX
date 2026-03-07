import paramiko


def deploy_rsa_key(ip, user, password, pub_key):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        agent_user = "aurenix_it_agent"
        print(f"\n--- DEPLOYING RSA KEY FOR {agent_user} ---")

        # Ensure .ssh exists and has right permissions
        client.exec_command(f"mkdir -p /home/{agent_user}/.ssh")
        client.exec_command(f"chown {agent_user}:{agent_user} /home/{agent_user}/.ssh")
        client.exec_command(f"chmod 700 /home/{agent_user}/.ssh")

        # Overwrite authorized_keys with the new RSA key
        cmd = f"echo '{pub_key}' > /home/{agent_user}/.ssh/authorized_keys"
        client.exec_command(cmd)

        # Correct permissions for authorized_keys
        client.exec_command(
            f"chown {agent_user}:{agent_user} /home/{agent_user}/.ssh/authorized_keys"
        )
        client.exec_command(f"chmod 600 /home/{agent_user}/.ssh/authorized_keys")

        print("RSA Public Key deployed and permissions secured.")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    pub_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCx3mW5uOzZbvM2uOW63dgkYuohzMU7bZms/DQGqOgqDPcVGhcM9dwpgCyvs4bfej+7Sexc9AYtf0/lcQhLN0ECCT7/O3BUHNPP+EC1C6K7QDRQuI2O2YORJ2Xhi00QkzzmXDdrHzdT1t8oJcys7IfEOe9XPXIco5K45ywcrLZa0UPU2npeg2ncUSXq/iBISRNOo96lV8DRMuLXtplgQkuNCVj7OWvEZj4fj6nlDrANerMfVUcXS3N+KQ3FnR0NB2RCqYck3vHvtUqUe1dGywRqtnUBwZzNxApw/m29/ipOSVza90dY609H8s6gmQXGQ42MObviPPmP9Y566877GRkDb9kYSvBGoQ4vGNIXAmXPnhF1xxyTyMgzZu9cx2eY4Ko5+Y8hg15JRjD/mebP+f7w7Y1/6j6/KLh30T6KG3U8TgVt0yoS1MgljmFXNpThqTMAoy7AyGr4l+fs1HpApZ2assLb3W9Bo90cYUKqi/qMpMMkP2k70GZonJGjF8PVA6XW4kzwSoHsuOgrJDn8gEvyW/tiOsWLPM9QXR+aNnBCQW41Q0afmU69upiQCJeKl3ktgWoGBjpUTrgdUahnMPNrcQpZhaMeARaZhj6rHnfC9TJXBmEqyx4c//I6Lf6qZGxnDeSHoE9JxVeVjgkKjv5pdH5qo5U2EwqcgM+pycLjsQ=="
    deploy_rsa_key("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE", pub_key)
