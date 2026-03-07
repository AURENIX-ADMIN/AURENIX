import paramiko
import time


def run_update_and_reboot(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {ip} to apply kernel patches and reboot...")
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        # Ejecutamos update, upgrade y reboot en una sola transacción nohup/background
        cmd = "nohup sh -c 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && reboot' > /var/log/system_update.log 2>&1 &"
        stdin, stdout, stderr = client.exec_command(cmd)

        print(
            "Update & Reboot command issued successfully. The server will go down shortly."
        )

    except Exception as e:
        print(f"Connection/Execution failed: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    import sys

    run_update_and_reboot(sys.argv[1], sys.argv[2], sys.argv[3])
