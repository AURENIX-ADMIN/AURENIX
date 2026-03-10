#!/bin/bash
# =============================================================================
# AURENIX BACKUP PRO — Script de backup profesional 3-2-1
# Ubicacion VPS: /usr/local/bin/aurenix-backup-pro.sh
# Cron: 0 3 * * * /usr/local/bin/aurenix-backup-pro.sh >> /var/log/aurenix-backup.log 2>&1
# =============================================================================

set -euo pipefail

# --- CONFIG ---
BACKUP_BASE="/data/agencia/backups"
DB_DIR="$BACKUP_BASE/db"
WF_DIR="$BACKUP_BASE/workflows"
DOCKER_DIR="$BACKUP_BASE/docker"
DLQ_DIR="$BACKUP_BASE/dlq"
DATE=$(date +%Y-%m-%d_%H%M)
RETENTION_DB=30      # dias
RETENTION_WF=90      # dias
# Discover n8n container IP (Docker network, not exposed on host)
N8N_CONTAINER_IP=$(docker inspect $(docker ps -qf "name=n8n" | head -1) --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null || echo "")
N8N_API_URL="http://${N8N_CONTAINER_IP:-localhost}:5678"
LOG_FILE="/var/log/aurenix-backup.log"

# --- INIT DIRS ---
mkdir -p "$DB_DIR" "$WF_DIR" "$DOCKER_DIR" "$DLQ_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "========== AURENIX BACKUP PRO START =========="

# --- 1. PostgreSQL Backup ---
log "1/5 PostgreSQL backup..."
PG_CONTAINER=$(docker ps -qf "name=postgresql" 2>/dev/null | head -1)
if [ -n "$PG_CONTAINER" ]; then
  docker exec "$PG_CONTAINER" pg_dumpall -U dVgL7FYPMsvrV5wk 2>/dev/null | gzip > "$DB_DIR/pg_full_${DATE}.sql.gz"
  DB_SIZE=$(stat -f%z "$DB_DIR/pg_full_${DATE}.sql.gz" 2>/dev/null || stat -c%s "$DB_DIR/pg_full_${DATE}.sql.gz" 2>/dev/null || echo "0")
  if [ "$DB_SIZE" -gt 1024 ]; then
    log "  OK: pg_full_${DATE}.sql.gz (${DB_SIZE} bytes)"
  else
    log "  WARNING: Backup DB muy pequeno (${DB_SIZE} bytes)"
  fi
else
  log "  ERROR: Container PostgreSQL no encontrado"
fi

# --- 2. n8n Workflows Export via API ---
log "2/5 n8n workflows export..."
# Try to discover API key from container env, fallback to config file
N8N_API_KEY=$(docker exec $(docker ps -qf "name=n8n" | head -1) printenv N8N_ENCRYPTION_KEY 2>/dev/null || echo "")
if [ -z "$N8N_API_KEY" ]; then
  N8N_API_KEY=$(grep -oP 'N8N_API_KEY=\K.*' /data/coolify/services/*/.env 2>/dev/null | head -1 || echo "")
fi
# Fallback: read from dedicated config file (created during setup)
if [ -z "$N8N_API_KEY" ]; then
  N8N_API_KEY=$(cat /etc/aurenix/n8n-api-key 2>/dev/null || echo "")
fi

if [ -n "$N8N_API_KEY" ]; then
  WF_FILE="$WF_DIR/workflows_${DATE}.json"
  HTTP_CODE=$(curl -s -o "$WF_FILE" -w "%{http_code}" \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    "${N8N_API_URL}/api/v1/workflows?limit=250" 2>/dev/null || echo "000")

  if [ "$HTTP_CODE" = "200" ]; then
    gzip "$WF_FILE"
    log "  OK: workflows_${DATE}.json.gz"
  else
    log "  ERROR: n8n API retorno HTTP $HTTP_CODE"
    rm -f "$WF_FILE"
  fi

  # Export credentials metadata (sin secrets)
  CREDS_FILE="$WF_DIR/credentials_meta_${DATE}.json"
  curl -s -o "$CREDS_FILE" \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    "${N8N_API_URL}/api/v1/credentials" 2>/dev/null || true
  if [ -f "$CREDS_FILE" ] && [ -s "$CREDS_FILE" ]; then
    gzip "$CREDS_FILE"
    log "  OK: credentials_meta_${DATE}.json.gz"
  else
    rm -f "$CREDS_FILE"
  fi
else
  log "  WARNING: N8N_API_KEY no encontrada, skip workflow export"
fi

# --- 3. Docker Configs ---
log "3/5 Docker configs backup..."
DOCKER_FILE="$DOCKER_DIR/docker_state_${DATE}.txt"
{
  echo "=== DOCKER PS ==="
  docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null
  echo ""
  echo "=== DOCKER IMAGES ==="
  docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" 2>/dev/null
  echo ""
  echo "=== DOCKER VOLUMES ==="
  docker volume ls 2>/dev/null
  echo ""
  echo "=== DOCKER NETWORKS ==="
  docker network ls 2>/dev/null
} > "$DOCKER_FILE"
gzip "$DOCKER_FILE"
log "  OK: docker_state_${DATE}.txt.gz"

# Backup compose files
find /data/coolify -name "docker-compose.yml" -o -name ".env" 2>/dev/null | while read f; do
  SAFE_NAME=$(echo "$f" | sed 's/\//_/g')
  cp "$f" "$DOCKER_DIR/compose_${SAFE_NAME}_${DATE}" 2>/dev/null || true
done
log "  OK: Compose files copied"

# --- 4. Traefik Config ---
log "4/5 Traefik config backup..."
# Coolify v4 stores proxy config in /data/coolify/proxy
TRAEFIK_DIR=$(find /data/coolify/proxy /data/coolify -maxdepth 3 -name "traefik*" -type d 2>/dev/null | head -1)
[ -z "$TRAEFIK_DIR" ] && TRAEFIK_DIR="/data/coolify/proxy"
if [ -n "$TRAEFIK_DIR" ] && [ -d "$TRAEFIK_DIR" ]; then
  tar czf "$DOCKER_DIR/traefik_config_${DATE}.tar.gz" -C "$TRAEFIK_DIR" . 2>/dev/null
  log "  OK: traefik_config_${DATE}.tar.gz"
else
  log "  WARNING: Traefik config dir not found"
fi

# --- 5. Cleanup old backups ---
log "5/5 Cleanup old backups..."
find "$DB_DIR" -name "pg_full_*.sql.gz" -mtime +"$RETENTION_DB" -delete 2>/dev/null
DB_DELETED=$?
find "$WF_DIR" -name "workflows_*.json.gz" -mtime +"$RETENTION_WF" -delete 2>/dev/null
find "$WF_DIR" -name "credentials_meta_*.json.gz" -mtime +"$RETENTION_WF" -delete 2>/dev/null
find "$DOCKER_DIR" -name "docker_state_*.txt.gz" -mtime +"$RETENTION_DB" -delete 2>/dev/null
find "$DOCKER_DIR" -name "compose_*" -mtime +"$RETENTION_DB" -delete 2>/dev/null
find "$DOCKER_DIR" -name "traefik_config_*" -mtime +"$RETENTION_DB" -delete 2>/dev/null
log "  OK: Old backups cleaned (DB>${RETENTION_DB}d, WF>${RETENTION_WF}d)"

# --- Summary ---
DB_COUNT=$(ls -1 "$DB_DIR"/pg_full_*.sql.gz 2>/dev/null | wc -l)
WF_COUNT=$(ls -1 "$WF_DIR"/workflows_*.json.gz 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_BASE" 2>/dev/null | cut -f1)

log "========== BACKUP COMPLETE =========="
log "  DB backups: $DB_COUNT files"
log "  WF backups: $WF_COUNT files"
log "  Total size: $TOTAL_SIZE"
log "======================================"
