import paramiko
import json


def get_n8n_db_creds(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username=user, password=password, timeout=10)

        container = "n8n-ps48skwo848408oo8gg04k8k"
        cmd = f"docker inspect {container} --format '{{{{json .Config.Env}}}}'"
        stdin, stdout, stderr = client.exec_command(cmd)
        envs = json.loads(stdout.read().decode().strip())

        creds = {}
        for e in envs:
            if "DB_POSTGRESDB_USER" in e:
                creds["user"] = e.split("=")[1]
            if "DB_POSTGRESDB_DATABASE" in e:
                creds["db"] = e.split("=")[1]
            if "DB_POSTGRESDB_PASSWORD" in e:
                creds["pass"] = e.split("=")[1]

        print(json.dumps(creds, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    get_n8n_db_creds("76.13.9.238", "root", r"0Vw&9k'l/yo+OS/IjbPE")
