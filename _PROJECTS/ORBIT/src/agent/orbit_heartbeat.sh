#!/bin/bash
# orbit_heartbeat.sh — Agente mínimo Orbit (bash + curl + openssl)
# Fallback para VPS sin Python. Cero dependencias adicionales.
#
# Variables de entorno requeridas:
#   ORBIT_URL      URL del dashboard Orbit
#   CLIENT_ID      UUID del cliente
#   SYSTEM_ID      UUID del sistema
#   AGENT_TOKEN    Token de autenticación
#
# Instalar como cron o systemd timer:
#   */5 * * * * /opt/orbit-agent/orbit_heartbeat.sh >> /var/log/orbit-agent.log 2>&1

set -euo pipefail

ORBIT_URL="${ORBIT_URL:-}"
CLIENT_ID="${CLIENT_ID:-}"
SYSTEM_ID="${SYSTEM_ID:-}"
AGENT_TOKEN="${AGENT_TOKEN:-}"
AGENT_VERSION="1.0.0-bash"

if [[ -z "$ORBIT_URL" || -z "$CLIENT_ID" || -z "$SYSTEM_ID" || -z "$AGENT_TOKEN" ]]; then
    echo "[orbit-agent] ERROR: Variables ORBIT_URL, CLIENT_ID, SYSTEM_ID y AGENT_TOKEN son obligatorias."
    exit 1
fi

# ── Checks de servicios ──────────────────────────────────────

check_http() {
    local url="$1"
    if curl -sf --max-time 5 "$url" > /dev/null 2>&1; then
        echo "true"
    else
        echo "false"
    fi
}

check_port() {
    local port="$1"
    if bash -c "echo >/dev/tcp/localhost/$port" 2>/dev/null; then
        echo "true"
    else
        echo "false"
    fi
}

FASTAPI_URL="${FASTAPI_HEALTH_URL:-http://localhost:8001/health}"
N8N_URL="${N8N_HEALTH_URL:-http://localhost:5678/healthz}"

FASTAPI_UP=$(check_http "$FASTAPI_URL")
N8N_UP=$(check_http "$N8N_URL")
PG_UP=$(check_port 5432)

# Overall status
if [[ "$FASTAPI_UP" == "true" && "$PG_UP" == "true" ]]; then
    STATUS="healthy"
elif [[ "$FASTAPI_UP" == "true" || "$PG_UP" == "true" ]]; then
    STATUS="degraded"
else
    STATUS="critical"
fi

# ── Payload ──────────────────────────────────────────────────

TIMESTAMP=$(date +%s)
BODY=$(cat <<EOF
{"status":"$STATUS","services":{"fastapi":{"up":$FASTAPI_UP},"n8n":{"up":$N8N_UP},"postgresql":{"up":$PG_UP}},"system":{"cpu_pct":null,"ram_pct":null,"disk_pct":null},"agent_version":"$AGENT_VERSION"}
EOF
)

# ── HMAC-SHA256 firma ────────────────────────────────────────

MESSAGE="${CLIENT_ID}${TIMESTAMP}${BODY}"
SIGNATURE=$(printf '%s' "$MESSAGE" | openssl dgst -sha256 -hmac "$AGENT_TOKEN" | awk '{print $2}')

# ── Envío ────────────────────────────────────────────────────

RESPONSE=$(curl -sf --max-time 15 \
    -X POST "${ORBIT_URL}/heartbeat" \
    -H "Content-Type: application/json" \
    -H "X-Client-ID: $CLIENT_ID" \
    -H "X-System-ID: $SYSTEM_ID" \
    -H "X-Timestamp: $TIMESTAMP" \
    -H "X-Signature: $SIGNATURE" \
    -H "X-Agent-Token: $AGENT_TOKEN" \
    -d "$BODY" 2>&1) || true

echo "[orbit-agent] $(date '+%Y-%m-%d %H:%M:%S') status=$STATUS response=$RESPONSE"
