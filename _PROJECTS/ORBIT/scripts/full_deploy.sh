#!/bin/bash
# =============================================================================
# Orbit — Deploy completo en VPS Hostinger (Ubuntu 24.04)
# Ejecutar como root. Hace TODO en un solo script.
# =============================================================================
set -e
export DEBIAN_FRONTEND=noninteractive

APP_DIR="/opt/orbit"
APP_USER="orbit"
DB_NAME="orbit_db"
DB_USER="orbit_user"
GITHUB_REPO="AURENIX-ADMIN/SIACompleto"
GITHUB_BRANCH="main"
ORBIT_SUBPATH="business-ideas/orbit"

echo ""
echo "============================================================"
echo "  ORBIT — Deploy automatico en VPS"
echo "============================================================"

# ── 1. Actualizar sistema ─────────────────────────────────────
echo ""
echo "[1/10] Actualizando sistema..."
apt-get update -qq
apt-get install -y -qq git curl openssl build-essential libpq-dev

# ── 2. Instalar Python 3.11 ───────────────────────────────────
echo "[2/10] Verificando Python 3.11..."
if ! command -v python3.11 &>/dev/null; then
    apt-get install -y -qq software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update -qq
    apt-get install -y -qq python3.11 python3.11-venv python3.11-dev
fi
python3.11 --version

# ── 3. Instalar PostgreSQL ────────────────────────────────────
echo "[3/10] Verificando PostgreSQL..."
if ! command -v psql &>/dev/null; then
    apt-get install -y -qq postgresql postgresql-contrib
fi
systemctl enable postgresql
systemctl start postgresql

# ── 4. Clonar código desde GitHub ────────────────────────────
echo "[4/10] Clonando codigo desde GitHub..."
mkdir -p /tmp/orbit_clone
# El token se pasa como argumento o está hardcoded temporalmente
GITHUB_TOKEN="${GITHUB_TOKEN:-__GITHUB_TOKEN__}"
git clone -q --depth 1 \
    "https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git" \
    /tmp/orbit_clone/repo 2>/dev/null

mkdir -p "$APP_DIR"
cp -r /tmp/orbit_clone/repo/${ORBIT_SUBPATH}/. "$APP_DIR/"
rm -rf /tmp/orbit_clone
echo "   -> Codigo copiado a $APP_DIR"

# ── 5. Crear usuario sistema ──────────────────────────────────
echo "[5/10] Creando usuario '$APP_USER'..."
id -u $APP_USER &>/dev/null || \
    useradd --system --shell /bin/bash --create-home --home-dir $APP_DIR $APP_USER

# ── 6. Crear base de datos PostgreSQL ────────────────────────
echo "[6/10] Creando base de datos PostgreSQL..."
DB_PASSWORD=$(openssl rand -hex 16)

sudo -u postgres psql <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
    CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASSWORD';
  END IF;
END
\$\$;
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
  WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
SQL

echo "   -> DB: $DB_NAME | User: $DB_USER | Pass: $DB_PASSWORD"

# ── 7. Crear .env de produccion ───────────────────────────────
echo "[7/10] Creando /opt/orbit/.env..."
cat > "$APP_DIR/.env" <<ENV
PORT=8003
ENVIRONMENT=production
ALLOWED_HOSTS=orbit.aurenix.cloud

SECRET_KEY=fa7139c16e27f7c780d81889d90660e692f3faeb2a617e1648008f22d1ae1c610b71054564a388787bc692e1de92b0476022255cd4ffb4b8fe403d17d24b3fcf
JWT_SECRET_KEY=840cbe2229a994acce5f42da5aedf52d18cf2606da4f32a0c4173a7dd11b47d92cf91ea07af7c64dab4499bef03e8271f44c81637c2478aaf394b2930b3d639b
INTERNAL_API_KEY=0a901127657b16b169668b13925ca4019b814b092e8a51f9cedf67f4ecc78fb8

DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}

ADMIN_EMAIL=admin@aurenix.es
ADMIN_PASSWORD=Orbit2026Admin

TELEGRAM_BOT_TOKEN=
TELEGRAM_ADMIN_CHAT_ID=5529992654

HOSTINGER_VPS_ID=1285851
HOSTINGER_API_TOKEN=

N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=PLACEHOLDER_OBTENER_DE_N8N_UI
ENV
chown $APP_USER:$APP_USER "$APP_DIR/.env"
chmod 600 "$APP_DIR/.env"

# ── 8. Crear venv e instalar dependencias ─────────────────────
echo "[8/10] Instalando dependencias Python..."
chown -R $APP_USER:$APP_USER "$APP_DIR"
sudo -u $APP_USER python3.11 -m venv "$APP_DIR/.venv"
sudo -u $APP_USER "$APP_DIR/.venv/bin/pip" install --quiet --upgrade pip
sudo -u $APP_USER "$APP_DIR/.venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"
echo "   -> Dependencias instaladas"

# ── 9. Inicializar base de datos ──────────────────────────────
echo "[9/10] Inicializando base de datos..."
cd "$APP_DIR"
sudo -u $APP_USER .venv/bin/python scripts/setup_db.py

# ── 10. Instalar y arrancar servicio systemd ──────────────────
echo "[10/10] Instalando servicio systemd..."
cp "$APP_DIR/orbit.service" /etc/systemd/system/orbit.service
systemctl daemon-reload
systemctl enable orbit
systemctl start orbit
sleep 3

# ── Cloudflare Tunnel ─────────────────────────────────────────
TUNNEL_CONFIG="/etc/cloudflared/config.yml"
if [ -f "$TUNNEL_CONFIG" ]; then
    if ! grep -q "orbit.aurenix.cloud" "$TUNNEL_CONFIG"; then
        # Insertar ANTES de la línea "  - service:" final (catch-all)
        sed -i '/^ingress:/a\  - hostname: orbit.aurenix.cloud\n    service: http://localhost:8003' \
            "$TUNNEL_CONFIG"
        echo "   -> Cloudflare tunnel configurado"
    else
        echo "   -> Cloudflare tunnel ya tenia entrada para orbit"
    fi
    systemctl restart cloudflared
    sleep 2
else
    echo "   -> AVISO: cloudflared no encontrado - configura el tunnel manualmente"
fi

# ── Resumen ───────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  DEPLOY COMPLETADO"
echo "============================================================"
echo ""
echo "  Status del servicio:"
systemctl status orbit --no-pager -l | head -8
echo ""
echo "  Test local:"
sleep 2
curl -s http://localhost:8003/health 2>/dev/null || echo "  (servicio arrancando...)"
echo ""
echo "  URL produccion: https://orbit.aurenix.cloud"
echo "  Admin: admin@aurenix.es / Orbit2026Admin"
echo ""
echo "  GUARDA ESTOS DATOS:"
echo "  DB_PASSWORD=$DB_PASSWORD"
echo "  DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo "============================================================"
