#!/bin/bash
# install_agent.sh — Instala el agente Orbit en un VPS cliente.
# Detecta si hay Python 3.8+ disponible e instala el agente adecuado.
# Si no hay Python, instala el agente bash mínimo.
#
# Uso:
#   bash install_agent.sh \
#     --client-id <UUID> \
#     --system-id <UUID> \
#     --agent-token <TOKEN> \
#     --orbit-url https://orbit.aurenix.cloud \
#     [--fastapi-url http://localhost:8001/health]

set -euo pipefail

# ── Defaults ─────────────────────────────────────────────────
CLIENT_ID=""
SYSTEM_ID=""
AGENT_TOKEN=""
ORBIT_URL=""
FASTAPI_URL="http://localhost:8001/health"
INSTALL_DIR="/opt/orbit-agent"
SERVICE_USER="${SUDO_USER:-ubuntu}"

# ── Parse arguments ──────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --client-id) CLIENT_ID="$2"; shift 2 ;;
        --system-id) SYSTEM_ID="$2"; shift 2 ;;
        --agent-token) AGENT_TOKEN="$2"; shift 2 ;;
        --orbit-url) ORBIT_URL="$2"; shift 2 ;;
        --fastapi-url) FASTAPI_URL="$2"; shift 2 ;;
        *) echo "Argumento desconocido: $1"; exit 1 ;;
    esac
done

if [[ -z "$CLIENT_ID" || -z "$SYSTEM_ID" || -z "$AGENT_TOKEN" || -z "$ORBIT_URL" ]]; then
    echo "Uso: bash install_agent.sh --client-id UUID --system-id UUID --agent-token TOKEN --orbit-url URL"
    exit 1
fi

echo "============================================="
echo "Orbit Agent — Instalación"
echo "============================================="

# ── Detect Python ────────────────────────────────────────────
PYTHON_CMD=""
for cmd in python3.11 python3.10 python3.9 python3.8 python3; do
    if command -v "$cmd" &>/dev/null; then
        version=$($cmd -c "import sys; print(sys.version_info.minor + sys.version_info.major * 10)")
        if [[ $version -ge 38 ]]; then
            PYTHON_CMD="$cmd"
            echo "[1/4] Python encontrado: $cmd"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    echo "[1/4] Python 3.8+ no encontrado — usando agente bash mínimo."
    USE_BASH_AGENT=true
else
    USE_BASH_AGENT=false
fi

# ── Create install dir ───────────────────────────────────────
echo "[2/4] Creando directorio $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

# ── Write env file ───────────────────────────────────────────
echo "[3/4] Escribiendo configuración..."
cat > "$INSTALL_DIR/.env" <<EOF
ORBIT_URL=$ORBIT_URL
CLIENT_ID=$CLIENT_ID
SYSTEM_ID=$SYSTEM_ID
AGENT_TOKEN=$AGENT_TOKEN
FASTAPI_HEALTH_URL=$FASTAPI_URL
EOF
chmod 600 "$INSTALL_DIR/.env"

# ── Install agent ────────────────────────────────────────────
if [[ "$USE_BASH_AGENT" == "false" ]]; then
    # Copy Python agent
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cp "$SCRIPT_DIR/../src/agent/orbit_agent.py" "$INSTALL_DIR/orbit_agent.py"

    # Install psutil
    $PYTHON_CMD -m pip install psutil --quiet

    # Create systemd service
    cat > /etc/systemd/system/orbit-agent.service <<EOF
[Unit]
Description=Orbit Agent — AURENIX Monitoring
After=network.target

[Service]
Type=oneshot
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$PYTHON_CMD $INSTALL_DIR/orbit_agent.py
StandardOutput=journal
StandardError=journal
EOF

    # Create systemd timer (every 5 minutes)
    cat > /etc/systemd/system/orbit-agent.timer <<EOF
[Unit]
Description=Orbit Agent Timer — cada 5 minutos
Requires=orbit-agent.service

[Timer]
OnBootSec=30s
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
EOF

    systemctl daemon-reload
    systemctl enable orbit-agent.timer
    systemctl start orbit-agent.timer
    echo "[4/4] Servicio Python instalado y activo (systemd timer)."

else
    # Copy bash agent
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cp "$SCRIPT_DIR/../src/agent/orbit_heartbeat.sh" "$INSTALL_DIR/orbit_heartbeat.sh"
    chmod +x "$INSTALL_DIR/orbit_heartbeat.sh"

    # Install via cron
    CRON_LINE="*/5 * * * * source $INSTALL_DIR/.env && bash $INSTALL_DIR/orbit_heartbeat.sh >> /var/log/orbit-agent.log 2>&1"
    (crontab -l 2>/dev/null | grep -v orbit-agent; echo "$CRON_LINE") | crontab -
    echo "[4/4] Agente bash instalado vía cron (cada 5 minutos)."
fi

echo ""
echo "============================================="
echo "Instalación completada."
echo "Logs: journalctl -u orbit-agent -f"
echo "============================================="

# ── Test first heartbeat ──────────────────────────────────────
echo ""
echo "Enviando primer heartbeat de prueba..."
if [[ "$USE_BASH_AGENT" == "false" ]]; then
    source "$INSTALL_DIR/.env"
    $PYTHON_CMD "$INSTALL_DIR/orbit_agent.py" && echo "Heartbeat enviado con exito." || echo "Error en heartbeat — revisar logs."
else
    source "$INSTALL_DIR/.env"
    bash "$INSTALL_DIR/orbit_heartbeat.sh" && echo "Heartbeat enviado con exito." || echo "Error en heartbeat — revisar logs."
fi
