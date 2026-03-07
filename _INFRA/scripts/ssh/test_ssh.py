import paramiko
import sys


def test_conn(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Testing connection to {ip}...")
        client.connect(hostname=ip, username=user, password=password, timeout=10)
        print("Success!")
        stdin, stdout, stderr = client.exec_command("uptime")
        print(f"Uptime: {stdout.read().decode().strip()}")
    except Exception as e:
        print(f"Failed: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    # Hardcoded or passed carefully
    test_conn("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
