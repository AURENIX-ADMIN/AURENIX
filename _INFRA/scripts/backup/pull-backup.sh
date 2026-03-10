#!/bin/bash
# =============================================================================
# AURENIX PULL BACKUP — Sync VPS backups to local PC (Location 2 of 3-2-1)
# Ubicacion: _INFRA/scripts/backup/pull-backup.sh
# Windows Task Scheduler: 05:00 AM diario (via Git Bash)
# Usage: bash pull-backup.sh
# =============================================================================

set -euo pipefail

# --- CONFIG ---
VPS_HOST="vps-aurenix"  # SSH alias from ~/.ssh/config
VPS_BACKUP_DIR="/data/agencia/backups"
LOCAL_BACKUP_DIR="$(dirname "$(cd "$(dirname "$0")" && pwd)")/../../Backups"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$LOCAL_BACKUP_DIR/sync_log.txt"

# Resolve absolute path
LOCAL_BACKUP_DIR=$(cd "$LOCAL_BACKUP_DIR" 2>/dev/null && pwd || mkdir -p "$LOCAL_BACKUP_DIR" && cd "$LOCAL_BACKUP_DIR" && pwd)

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== PULL BACKUP START =========="

# --- Create local dirs ---
mkdir -p "$LOCAL_BACKUP_DIR/db" "$LOCAL_BACKUP_DIR/workflows" "$LOCAL_BACKUP_DIR/docker"

# --- Sync via rsync over SSH ---
log "Syncing DB backups..."
rsync -avz --progress \
  -e "ssh" \
  "$VPS_HOST:$VPS_BACKUP_DIR/db/" \
  "$LOCAL_BACKUP_DIR/db/" 2>&1 | tail -3 | while read line; do log "  $line"; done

log "Syncing workflow backups..."
rsync -avz --progress \
  -e "ssh" \
  "$VPS_HOST:$VPS_BACKUP_DIR/workflows/" \
  "$LOCAL_BACKUP_DIR/workflows/" 2>&1 | tail -3 | while read line; do log "  $line"; done

log "Syncing Docker configs..."
rsync -avz --progress \
  -e "ssh" \
  "$VPS_HOST:$VPS_BACKUP_DIR/docker/" \
  "$LOCAL_BACKUP_DIR/docker/" 2>&1 | tail -3 | while read line; do log "  $line"; done

log "Syncing error logs..."
rsync -avz --progress \
  -e "ssh" \
  "$VPS_HOST:$VPS_BACKUP_DIR/sentinel_errors.jsonl" \
  "$LOCAL_BACKUP_DIR/" 2>/dev/null | tail -1 | while read line; do log "  $line"; done || true

rsync -avz --progress \
  -e "ssh" \
  "$VPS_HOST:$VPS_BACKUP_DIR/oracle_intel.jsonl" \
  "$LOCAL_BACKUP_DIR/" 2>/dev/null | tail -1 | while read line; do log "  $line"; done || true

# --- Verify ---
DB_COUNT=$(ls -1 "$LOCAL_BACKUP_DIR/db/"*.sql.gz 2>/dev/null | wc -l)
WF_COUNT=$(ls -1 "$LOCAL_BACKUP_DIR/workflows/"*.json.gz 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "$LOCAL_BACKUP_DIR" 2>/dev/null | cut -f1)

log "========== PULL BACKUP COMPLETE =========="
log "  DB files synced: $DB_COUNT"
log "  WF files synced: $WF_COUNT"
log "  Local total size: $TOTAL_SIZE"
log "==========================================="
