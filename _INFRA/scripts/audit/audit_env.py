import re


def parse_env_and_check(filepath):
    required = [
        "VPS_IP",
        "VPS_PASSWORD",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_ID_JOSE",
        "GROQ_API_KEY",
        "SMTP_JOSE_USER",
        "SMTP_JOSE_PASSWORD",
    ]
    present = []
    missing = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            for req in required:
                # Buscar patrón clave=valor donde valor no esté vacío y no sea un comentario puro
                match = re.search(f"^{req}=(.*?)(?:#|$)", content, re.MULTILINE)
                if match and match.group(1).strip():
                    present.append(req)
                else:
                    missing.append(req)

        print(f"--- VERIFICACIÓN .ENV.LOCAL ---")
        print(f"✅ Variables configuradas: {', '.join(present)}")
        if missing:
            print(f"❌ Variables FALTANTES o vacías: {', '.join(missing)}")
        else:
            print("🚀 Todo listo. Entorno OK para empezar.")

    except Exception as e:
        print(f"Error procesando {filepath}: {str(e)}")


if __name__ == "__main__":
    parse_env_and_check(r"c:\Users\Usuario\Desktop\AURENIX\.env.local")
