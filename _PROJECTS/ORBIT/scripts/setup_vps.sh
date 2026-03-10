#!/bin/bash
# =============================================================================
# Orbit — Setup inicial en VPS Hostinger (Ubuntu 22.04)
# Ejecutar como root: bash setup_vps.sh
# =============================================================================
set -e

APP_DIR="/opt/orbit"
APP_USER="orbit"
PYTHON="python3.11"
DB_NAME="orbit_db"
DB_USER="orbit_user"

echo "=== [1/8] Actualizar sistema ==="
apt-get update -qq && apt-get upgrade -y -qq

echo "=== [2/8] Instalar dependencias del sistema ==="
apt-get install -y -qq \
    python3.11 python3.11-venv python3.11-dev \
    postgresql postgresql-contrib \
    build-essential libpq-dev \
    git curl

echo "=== [3/8] Crear usuario orbit ==="
id -u $APP_USER &>/dev/null || useradd --system --shell /bin/bash --create-home --home-dir $APP_DIR $APP_USER

echo "=== [4/8] Crear base de datos PostgreSQL ==="
DB_PASSWORD=$(openssl rand -hex 16)
sudo -u postgres psql <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
    CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASSWORD';
  END IF;
END
\$\$;
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
SQL
echo "  → DB creada. Contraseña: $DB_PASSWORD"
echo "  → Guarda esto: DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"

echo "=== [5/8] Ajustar permisos de aplicación ==="
# Código ya transferido por rsync; solo ajustar permisos
chown -R $APP_USER:$APP_USER $APP_DIR

echo "=== [6/8] Crear entorno virtual e instalar dependencias ==="
sudo -u $APP_USER $PYTHON -m venv $APP_DIR/.venv
sudo -u $APP_USER $APP_DIR/.venv/bin/pip install --quiet --upgrade pip
sudo -u $APP_USER $APP_DIR/.venv/bin/pip install --quiet -r $APP_DIR/requirements.txt

echo "=== [7/8] Instalar servicio systemd ==="
cp $APP_DIR/orbit.service /etc/systemd/system/orbit.service
systemctl daemon-reload
systemctl enable orbit

echo "=== [8/8] Añadir Orbit al túnel de Cloudflare ==="
TUNNEL_CONFIG="/etc/cloudflared/config.yml"
if [ -f "$TUNNEL_CONFIG" ]; then
    echo ""
    echo "  *** Añade esta entrada al inicio de ingress en $TUNNEL_CONFIG: ***"
    echo ""
    echo "  - hostname: orbit.aurenix.cloud"
    echo "    service: http://localhost:8003"
    echo ""
    echo "  Luego ejecuta: systemctl restart cloudflared"
else
    echo "  (cloudflared no encontrado — configura el túnel manualmente)"
fi

echo ""
echo "============================================================"
echo " NEXT STEPS:"
echo "============================================================"
echo " 1. Crea /opt/orbit/.env (usa .env.example como base)"
echo "    DATABASE_URL=postgresql+asyncpg://$DB_USER:<password>@localhost:5432/$DB_NAME"
echo ""
echo " 2. Inicializa la base de datos:"
echo "    cd /opt/orbit && sudo -u orbit .venv/bin/python scripts/setup_db.py"
echo ""
echo " 3. Arranca el servicio:"
echo "    systemctl start orbit && systemctl status orbit"
echo ""
echo " 4. Configura Cloudflare Tunnel (ver instrucciones arriba)"
echo "============================================================"
