#!/usr/bin/env python3
"""
Orbit Agent — Agente de monitorización para VPS cliente.
Compatible con Python 3.8+. Sin dependencias externas excepto psutil.

Variables de entorno requeridas:
  ORBIT_URL        URL del dashboard Orbit (ej: https://orbit.aurenix.cloud)
  CLIENT_ID        UUID del cliente en Orbit
  SYSTEM_ID        UUID del sistema en Orbit
  AGENT_TOKEN      Token de autenticación (generado con: python main.py add-token)

Uso:
  python orbit_agent.py          Run once (called by systemd timer)
  python orbit_agent.py --loop   Loop every 5 minutes (alternative to systemd)
"""
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

AGENT_VERSION = "1.0.0"
INTERVAL_SECONDS = 300  # 5 minutes


def _env(key: str, required: bool = True) -> str:
    val = os.environ.get(key, "")
    if required and not val:
        print(f"[orbit-agent] ERROR: Variable de entorno '{key}' no configurada.")
        sys.exit(1)
    return val


def _compute_hmac(client_id: str, timestamp: str, body: bytes, token: str) -> str:
    message = f"{client_id}{timestamp}".encode() + body
    return hmac.new(token.encode(), message, hashlib.sha256).hexdigest()


def _check_http(url: str, timeout: int = 5) -> tuple[bool, float]:
    """Returns (is_up, response_ms)."""
    start = time.time()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
        elapsed = (time.time() - start) * 1000
        return True, round(elapsed, 1)
    except Exception:
        return False, 0.0


def _check_postgres() -> bool:
    """Check if PostgreSQL is listening on localhost:5432."""
    import socket
    try:
        with socket.create_connection(("localhost", 5432), timeout=3):
            return True
    except OSError:
        return False


def _check_n8n(n8n_url: str = "http://localhost:5678/healthz") -> bool:
    up, _ = _check_http(n8n_url)
    return up


def _check_fastapi(fastapi_url: str = "http://localhost:8001/health") -> tuple[bool, float]:
    return _check_http(fastapi_url)


def _check_telegram_bot(heartbeat_file: str = "/tmp/telegram_bot_heartbeat") -> bool:
    """
    The Telegram bot should write its PID or timestamp to a file periodically.
    We consider it up if the file was modified in the last 3 minutes.
    Fallback: check if python process with 'bot' in cmdline is running.
    """
    try:
        mtime = os.path.getmtime(heartbeat_file)
        age = time.time() - mtime
        return age < 180
    except FileNotFoundError:
        pass

    # Fallback: check process list
    try:
        import subprocess
        result = subprocess.run(
            ["pgrep", "-f", "telegram"],
            capture_output=True, text=True, timeout=3
        )
        return result.returncode == 0
    except Exception:
        return False


def _get_system_metrics() -> dict:
    try:
        import psutil
        return {
            "cpu_pct": round(psutil.cpu_percent(interval=1), 1),
            "ram_pct": round(psutil.virtual_memory().percent, 1),
            "disk_pct": round(psutil.disk_usage("/").percent, 1),
        }
    except ImportError:
        # psutil not available — return None values
        return {"cpu_pct": None, "ram_pct": None, "disk_pct": None}


def _determine_status(services: dict) -> str:
    """Determine overall health status from individual service checks."""
    critical_services = ["fastapi", "postgresql"]
    all_up = all(
        services.get(s, {}).get("up", True) for s in critical_services
    )
    any_up = any(
        services.get(s, {}).get("up", False) for s in services
    )
    if all_up:
        return "healthy"
    if any_up:
        return "degraded"
    return "critical"


def collect_and_send():
    orbit_url = _env("ORBIT_URL").rstrip("/")
    client_id = _env("CLIENT_ID")
    system_id = _env("SYSTEM_ID")
    agent_token = _env("AGENT_TOKEN")

    # Configurable service URLs (with defaults)
    fastapi_url = os.environ.get("FASTAPI_HEALTH_URL", "http://localhost:8001/health")
    n8n_url = os.environ.get("N8N_HEALTH_URL", "http://localhost:5678/healthz")

    # Collect metrics
    fastapi_up, fastapi_ms = _check_fastapi(fastapi_url)
    n8n_up = _check_n8n(n8n_url)
    pg_up = _check_postgres()
    tg_up = _check_telegram_bot()
    sys_metrics = _get_system_metrics()

    services = {
        "fastapi": {"up": fastapi_up, "response_ms": fastapi_ms},
        "n8n": {"up": n8n_up},
        "postgresql": {"up": pg_up},
        "telegram_bot": {"up": tg_up},
    }

    payload = {
        "status": _determine_status(services),
        "services": services,
        "system": sys_metrics,
        "agent_version": AGENT_VERSION,
    }

    body = json.dumps(payload).encode()
    timestamp = str(int(time.time()))
    signature = _compute_hmac(client_id, timestamp, body, agent_token)

    headers = {
        "Content-Type": "application/json",
        "X-Client-ID": client_id,
        "X-System-ID": system_id,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "X-Agent-Token": agent_token,
    }

    endpoint = f"{orbit_url}/heartbeat"
    req = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_data = json.loads(resp.read())
            print(f"[orbit-agent] OK — {resp_data.get('received_at', 'sent')}")
    except urllib.error.HTTPError as e:
        print(f"[orbit-agent] HTTP {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"[orbit-agent] ERROR: {e}")


def main():
    if "--loop" in sys.argv:
        print(f"[orbit-agent] Modo loop — enviando heartbeat cada {INTERVAL_SECONDS}s")
        while True:
            collect_and_send()
            time.sleep(INTERVAL_SECONDS)
    else:
        collect_and_send()


if __name__ == "__main__":
    main()
