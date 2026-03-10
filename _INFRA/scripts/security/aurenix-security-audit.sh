#!/bin/bash
# =============================================================================
# AURENIX SECURITY AUDIT — S13 Tokin Privacy
# Ubicacion VPS: /usr/local/bin/aurenix-security-audit.sh
# Cron: 0 2 * * * /usr/local/bin/aurenix-security-audit.sh
# Output: /data/agencia/security/audit_YYYY-MM-DD.json
# =============================================================================

set -euo pipefail

DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
OUTPUT_DIR="/data/agencia/security"
OUTPUT_FILE="$OUTPUT_DIR/audit_${DATE}.json"
RETENTION_DAYS=90

mkdir -p "$OUTPUT_DIR"

# --- Helper: JSON escape ---
json_escape() {
  echo "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))'
}

# --- 1. Open Ports vs Whitelist ---
WHITELIST_PORTS="22 80 443 8000"
OPEN_PORTS=$(ss -tlnp 2>/dev/null | awk 'NR>1 {print $4}' | grep -oP ':\K\d+$' | sort -un | tr '\n' ' ' || echo "")
UNEXPECTED_PORTS=""
for port in $OPEN_PORTS; do
  if ! echo "$WHITELIST_PORTS" | grep -qw "$port"; then
    UNEXPECTED_PORTS="$UNEXPECTED_PORTS $port"
  fi
done
UNEXPECTED_PORTS=$(echo "$UNEXPECTED_PORTS" | xargs)
PORT_STATUS="OK"
[ -n "$UNEXPECTED_PORTS" ] && PORT_STATUS="WARNING"

# --- 2. SSH Failed Attempts (24h) ---
SSH_FAILED_24H=$(journalctl -u ssh --since "24 hours ago" 2>/dev/null | grep -c "Failed password\|Failed publickey" || echo "0")
SSH_STATUS="OK"
[ "$SSH_FAILED_24H" -gt 100 ] && SSH_STATUS="WARNING"
[ "$SSH_FAILED_24H" -gt 500 ] && SSH_STATUS="CRITICAL"

# --- 3. SSH Config Security ---
PERMIT_ROOT=$(grep -E "^PermitRootLogin" /etc/ssh/sshd_config 2>/dev/null | awk '{print $2}' || echo "unknown")
PASSWORD_AUTH=$(grep -E "^PasswordAuthentication" /etc/ssh/sshd_config 2>/dev/null | awk '{print $2}' || echo "unknown")
SSHD_STATUS="OK"
[ "$PERMIT_ROOT" = "yes" ] && SSHD_STATUS="WARNING"
[ "$PASSWORD_AUTH" = "yes" ] && SSHD_STATUS="WARNING"

# --- 4. Docker Security ---
PRIVILEGED_CONTAINERS=$(docker ps --format '{{.Names}}' 2>/dev/null | while read name; do
  docker inspect "$name" --format '{{.HostConfig.Privileged}}' 2>/dev/null | grep -q "true" && echo "$name"
done || echo "")
EXPOSED_PORTS=$(docker ps --format '{{.Names}}: {{.Ports}}' 2>/dev/null | grep "0.0.0.0:" | grep -vE ":(80|443|8000|6001|6002)->" || echo "")
DOCKER_STATUS="OK"
[ -n "$PRIVILEGED_CONTAINERS" ] && DOCKER_STATUS="CRITICAL"
[ -n "$EXPOSED_PORTS" ] && DOCKER_STATUS="WARNING"

# --- 5. File Permissions ---
PERM_ISSUES=""
# Check SSH keys
for keyfile in /root/.ssh/id_* /root/.ssh/authorized_keys /home/*/.ssh/id_* /home/*/.ssh/authorized_keys; do
  [ -f "$keyfile" ] || continue
  perms=$(stat -c%a "$keyfile" 2>/dev/null || echo "unknown")
  if [ "$perms" != "600" ] && [ "$perms" != "644" ] && [ "$perms" != "unknown" ]; then
    PERM_ISSUES="$PERM_ISSUES $keyfile($perms)"
  fi
done
# Check sensitive dirs
for dir in /etc/aurenix /data/coolify; do
  [ -d "$dir" ] || continue
  perms=$(stat -c%a "$dir" 2>/dev/null || echo "unknown")
  if [ "$perms" != "700" ] && [ "$perms" != "750" ] && [ "$perms" != "755" ] && [ "$perms" != "unknown" ]; then
    PERM_ISSUES="$PERM_ISSUES $dir($perms)"
  fi
done
PERM_ISSUES=$(echo "$PERM_ISSUES" | xargs)
PERM_STATUS="OK"
[ -n "$PERM_ISSUES" ] && PERM_STATUS="WARNING"

# --- 6. UFW/iptables ---
UFW_STATUS_RAW=$(ufw status 2>/dev/null | head -1 || echo "not installed")
UFW_RULES=$(ufw status numbered 2>/dev/null | grep -c "ALLOW\|DENY" || echo "0")
FW_STATUS="OK"
echo "$UFW_STATUS_RAW" | grep -qi "inactive" && FW_STATUS="CRITICAL"
echo "$UFW_STATUS_RAW" | grep -qi "not installed" && FW_STATUS="WARNING"

# --- 7. Unattended Upgrades ---
UNATTENDED=$(dpkg -l 2>/dev/null | grep -c "unattended-upgrades" || echo "0")
UNATTENDED_STATUS="OK"
[ "$UNATTENDED" = "0" ] && UNATTENDED_STATUS="WARNING"

# --- 8. SSL Cert Expiry ---
SSL_CERTS=""
for domain in n8n.aurenix.cloud files.aurenix.cloud qdrant.aurenix.cloud dashboard.aurenix.cloud aurenix.cloud; do
  EXPIRY=$(echo | timeout 5 openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2 || echo "unknown")
  if [ "$EXPIRY" != "unknown" ] && [ -n "$EXPIRY" ]; then
    EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || echo "0")
    NOW_EPOCH=$(date +%s)
    DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
    SSL_CERTS="$SSL_CERTS {\"domain\":\"$domain\",\"expires\":\"$EXPIRY\",\"daysLeft\":$DAYS_LEFT},"
  fi
done
SSL_CERTS="[${SSL_CERTS%,}]"
SSL_STATUS="OK"
echo "$SSL_CERTS" | grep -qP '"daysLeft":\s*[0-9]{1,2}[^0-9]' && SSL_STATUS="WARNING"
echo "$SSL_CERTS" | grep -qP '"daysLeft":\s*-' && SSL_STATUS="CRITICAL"

# --- 9. Fail2ban ---
F2B_STATUS=$(fail2ban-client status 2>/dev/null | grep "Number of jail" | awk '{print $NF}' || echo "0")
F2B_SSH_BANNED=$(fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | awk '{print $NF}' || echo "0")
F2B_SSH_TOTAL=$(fail2ban-client status sshd 2>/dev/null | grep "Total banned" | awk '{print $NF}' || echo "0")
F2B_BAN_STATUS="OK"
[ "$F2B_STATUS" = "0" ] && F2B_BAN_STATUS="CRITICAL"

# --- 10. Disk & Resources ---
DISK_USAGE=$(df -h / 2>/dev/null | awk 'NR==2 {print $5}' | tr -d '%' || echo "0")
RAM_USAGE=$(free 2>/dev/null | awk '/Mem:/ {printf "%.0f", $3/$2*100}' || echo "0")
RESOURCE_STATUS="OK"
[ "$DISK_USAGE" -gt 85 ] && RESOURCE_STATUS="WARNING"
[ "$DISK_USAGE" -gt 95 ] && RESOURCE_STATUS="CRITICAL"

# --- Determine overall severity ---
OVERALL="OK"
for status in "$PORT_STATUS" "$SSH_STATUS" "$SSHD_STATUS" "$DOCKER_STATUS" "$PERM_STATUS" "$FW_STATUS" "$UNATTENDED_STATUS" "$SSL_STATUS" "$F2B_BAN_STATUS" "$RESOURCE_STATUS"; do
  [ "$status" = "CRITICAL" ] && OVERALL="CRITICAL" && break
  [ "$status" = "WARNING" ] && OVERALL="WARNING"
done

# --- Build JSON Output ---
cat > "$OUTPUT_FILE" << JSONEOF
{
  "timestamp": "$TIMESTAMP",
  "date": "$DATE",
  "overall": "$OVERALL",
  "checks": {
    "ports": {
      "status": "$PORT_STATUS",
      "whitelist": "$WHITELIST_PORTS",
      "open": "$OPEN_PORTS",
      "unexpected": "$UNEXPECTED_PORTS"
    },
    "ssh_attacks": {
      "status": "$SSH_STATUS",
      "failed_24h": $SSH_FAILED_24H
    },
    "sshd_config": {
      "status": "$SSHD_STATUS",
      "permit_root_login": "$PERMIT_ROOT",
      "password_auth": "$PASSWORD_AUTH"
    },
    "docker": {
      "status": "$DOCKER_STATUS",
      "privileged_containers": "$PRIVILEGED_CONTAINERS",
      "exposed_ports": "$(echo "$EXPOSED_PORTS" | tr '\n' '; ')"
    },
    "file_permissions": {
      "status": "$PERM_STATUS",
      "issues": "$PERM_ISSUES"
    },
    "firewall": {
      "status": "$FW_STATUS",
      "ufw_status": "$UFW_STATUS_RAW",
      "rules_count": $UFW_RULES
    },
    "unattended_upgrades": {
      "status": "$UNATTENDED_STATUS",
      "installed": $UNATTENDED
    },
    "ssl_certs": {
      "status": "$SSL_STATUS",
      "certs": $SSL_CERTS
    },
    "fail2ban": {
      "status": "$F2B_BAN_STATUS",
      "jails": $F2B_STATUS,
      "ssh_currently_banned": $F2B_SSH_BANNED,
      "ssh_total_banned": $F2B_SSH_TOTAL
    },
    "resources": {
      "status": "$RESOURCE_STATUS",
      "disk_percent": $DISK_USAGE,
      "ram_percent": $RAM_USAGE
    }
  }
}
JSONEOF

echo "[$(date)] Security audit complete: $OVERALL -> $OUTPUT_FILE"

# --- Cleanup old audits ---
find "$OUTPUT_DIR" -name "audit_*.json" -mtime +"$RETENTION_DAYS" -delete 2>/dev/null || true
