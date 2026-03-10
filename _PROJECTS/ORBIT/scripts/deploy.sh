#!/bin/bash
# =============================================================================
# Orbit — Deploy rápido (actualizar código en VPS ya configurado)
# Uso: bash scripts/deploy.sh [VPS_IP] [VPS_USER]
# Ejemplo: bash scripts/deploy.sh 123.45.67.89 root
# =============================================================================
set -e

VPS_IP="${1:?Uso: deploy.sh <VPS_IP> [VPS_USER]}"
VPS_USER="${2:-root}"
APP_DIR="/opt/orbit"
APP_USER="orbit"

echo "=== Desplegando Orbit en $VPS_USER@$VPS_IP ==="

echo "[1/4] Sincronizando archivos..."
rsync -az --progress \
    --exclude='.env' \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.git/' \
    --exclude='data/cache/' \
    . "$VPS_USER@$VPS_IP:$APP_DIR/"

echo "[2/4] Actualizando dependencias..."
ssh "$VPS_USER@$VPS_IP" "
    chown -R $APP_USER:$APP_USER $APP_DIR
    sudo -u $APP_USER $APP_DIR/.venv/bin/pip install --quiet -r $APP_DIR/requirements.txt
"

echo "[3/4] Reiniciando servicio..."
ssh "$VPS_USER@$VPS_IP" "systemctl restart orbit && sleep 2 && systemctl status orbit --no-pager"

echo "[4/4] Health check..."
sleep 3
if ssh "$VPS_USER@$VPS_IP" "curl -sf http://localhost:8003/health" | grep -q '"status":"ok"'; then
    echo "✓ Orbit operativo en https://orbit.aurenix.cloud"
else
    echo "✗ Health check fallido — revisa: journalctl -u orbit -n 50"
    exit 1
fi
