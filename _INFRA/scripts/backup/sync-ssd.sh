#!/bin/bash
# =============================================================================
# AURENIX SSD SYNC — Sync local backups to external SSD (Location 3 of 3-2-1)
# Ubicacion: _INFRA/scripts/backup/sync-ssd.sh
# Usage: bash sync-ssd.sh [SSD_PATH]
# Default SSD path: /d/AURENIX_BACKUPS (D: drive on Windows via Git Bash)
# =============================================================================

set -euo pipefail

# --- CONFIG ---
LOCAL_BACKUP_DIR="$(dirname "$(cd "$(dirname "$0")" && pwd)")/../../Backups"
LOCAL_BACKUP_DIR=$(cd "$LOCAL_BACKUP_DIR" 2>/dev/null && pwd || echo "$LOCAL_BACKUP_DIR")
SSD_PATH="${1:-/d/AURENIX_BACKUPS}"
DATE=$(date +%Y-%m-%d)

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# --- Check SSD ---
if [ ! -d "$(dirname "$SSD_PATH")" ]; then
  log "ERROR: SSD not detected at $(dirname "$SSD_PATH")"
  log "Connect the external drive and try again."
  log "Usage: bash sync-ssd.sh /path/to/ssd/AURENIX_BACKUPS"
  exit 1
fi

mkdir -p "$SSD_PATH"

log "========== SSD SYNC START =========="
log "Source: $LOCAL_BACKUP_DIR"
log "Destination: $SSD_PATH"

# --- Sync ---
rsync -avz --progress \
  "$LOCAL_BACKUP_DIR/" \
  "$SSD_PATH/" 2>&1 | tail -5

# --- Verify ---
SSD_SIZE=$(du -sh "$SSD_PATH" 2>/dev/null | cut -f1)
SSD_FILES=$(find "$SSD_PATH" -type f | wc -l)

log "========== SSD SYNC COMPLETE =========="
log "  Files on SSD: $SSD_FILES"
log "  SSD backup size: $SSD_SIZE"
log "  Last sync: $DATE"
log "========================================"

# Write sync marker
echo "$DATE" > "$SSD_PATH/.last_sync"
