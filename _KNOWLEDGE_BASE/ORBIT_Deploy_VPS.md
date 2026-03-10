# Orbit — Guía de Deploy en VPS AURENIX

> VPS: 76.13.9.238 | Ubuntu 24.04 | Docker + Coolify + Traefik
> Puerto Orbit: 8003 | Subdomain: orbit.aurenix.cloud

---

## 1. Prerequisitos

- SSH acceso root: `ssh vps-aurenix` (alias configurado en ~/.ssh/config)
- Traefik ya activo como proxy (usado por n8n, dashboard, web)
- PostgreSQL corriendo en container Docker (accesible en red Docker interna)
- Python 3.11 disponible en el VPS

Verificar prerequisitos:
```bash
ssh vps-aurenix "python3.11 --version && docker ps --format '{{.Names}}' | grep -E 'postgres|traefik'"
```

---

## 2. Base de Datos PostgreSQL

Orbit usa la instancia PostgreSQL existente del VPS. Crear una DB separada para aislamiento:

```bash
ssh vps-aurenix

# Entrar al container PostgreSQL de n8n (ajustar nombre si cambia)
POSTGRES_CONTAINER=$(docker ps --format '{{.Names}}' | grep postgres | head -1)
echo "Container: $POSTGRES_CONTAINER"

# Crear DB y usuario para Orbit
docker exec -it "$POSTGRES_CONTAINER" psql -U dVgL7FYPMsvrV5wk -c "
  CREATE DATABASE orbit_db;
  CREATE USER orbit_user WITH ENCRYPTED PASSWORD 'OrbitDB2026!';
  GRANT ALL PRIVILEGES ON DATABASE orbit_db TO orbit_user;
"
```

La DATABASE_URL para Orbit:
```
postgresql://orbit_user:OrbitDB2026!@localhost:5432/orbit_db
```

Nota: Si Orbit corre como container Docker en la misma red, usar el nombre del container PostgreSQL en lugar de `localhost`.

---

## 3. Estructura de Directorios en VPS

```
/opt/orbit/                 <- Código de la aplicación
/opt/orbit/venv/            <- Virtualenv Python
/opt/orbit/logs/            <- Logs de la aplicación
/data/agencia/orbit/        <- Datos persistentes (uploads, exports)
/etc/systemd/system/orbit.service  <- Service file
```

Crear estructura:
```bash
ssh vps-aurenix "mkdir -p /opt/orbit /data/agencia/orbit/uploads /data/agencia/orbit/exports"
```

---

## 4. Deploy Inicial (Primera vez)

### 4.1 Clonar el código
```bash
ssh vps-aurenix

cd /opt
git clone /data/git-repos/aurenix.git orbit-repo
# Si el código de Orbit está en un subdirectorio:
ln -s /opt/orbit-repo/_PROJECTS/ORBIT /opt/orbit
```

O clonar directamente desde GitHub (una vez que el PAT esté configurado):
```bash
git clone https://github.com/AURENIX-ADMIN/AURENIX.git /opt/orbit-repo
```

### 4.2 Instalar dependencias Python
```bash
ssh vps-aurenix

cd /opt/orbit
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 Archivo .env de Orbit
Crear `/opt/orbit/.env`:
```bash
ssh vps-aurenix "cat > /opt/orbit/.env" << 'EOF'
DATABASE_URL=postgresql://orbit_user:OrbitDB2026!@localhost:5432/orbit_db
SECRET_KEY=CAMBIAR_POR_SECRET_ALEATORIO_64_CHARS
ENVIRONMENT=production
PORT=8003
LOG_LEVEL=info
DATA_DIR=/data/agencia/orbit
EOF
```

Generar un SECRET_KEY seguro:
```bash
ssh vps-aurenix "python3 -c 'import secrets; print(secrets.token_hex(32))'"
```

### 4.4 Health check en main.py
Orbit DEBE exponer un endpoint `/health` para el CI/CD. Si no existe, añadir a `main.py` o `app.py`:

```python
# Para FastAPI:
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "orbit", "version": "1.0.0"}

# Para Flask:
@app.route("/health")
def health_check():
    return {"status": "ok", "service": "orbit", "version": "1.0.0"}, 200
```

Verificar que responde antes de configurar Traefik:
```bash
ssh vps-aurenix "curl -s http://localhost:8003/health"
```

### 4.5 Migraciones de BD (si usa Alembic)
```bash
ssh vps-aurenix "cd /opt/orbit && source venv/bin/activate && alembic upgrade head"
```

---

## 5. Systemd Service

### 5.1 Crear orbit.service
```bash
ssh vps-aurenix "cat > /etc/systemd/system/orbit.service" << 'EOF'
[Unit]
Description=Orbit — AURENIX Internal Tool
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/orbit
EnvironmentFile=/opt/orbit/.env
ExecStart=/opt/orbit/venv/bin/python main.py
# Si usa uvicorn (FastAPI):
# ExecStart=/opt/orbit/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8003 --workers 2
Restart=always
RestartSec=5
StandardOutput=append:/opt/orbit/logs/orbit.log
StandardError=append:/opt/orbit/logs/orbit_error.log

[Install]
WantedBy=multi-user.target
EOF
```

Nota: Si Orbit usa FastAPI + uvicorn, descomentar la línea ExecStart de uvicorn y comentar la de python.

### 5.2 Activar e iniciar
```bash
ssh vps-aurenix "
  mkdir -p /opt/orbit/logs
  systemctl daemon-reload
  systemctl enable orbit
  systemctl start orbit
  sleep 2
  systemctl status orbit
"
```

### 5.3 Comandos de gestión
```bash
# Ver estado
ssh vps-aurenix "systemctl status orbit"

# Ver logs en tiempo real
ssh vps-aurenix "journalctl -u orbit -f"

# Ver últimas 50 líneas de log
ssh vps-aurenix "tail -50 /opt/orbit/logs/orbit.log"

# Reiniciar
ssh vps-aurenix "systemctl restart orbit"

# Parar
ssh vps-aurenix "systemctl stop orbit"
```

---

## 6. Traefik — Exponer orbit.aurenix.cloud

Orbit no corre en Docker, corre como servicio systemd. Necesitamos un container Docker mínimo que haga proxy, O configurar Traefik directamente para apuntar a localhost:8003.

### Opción A: Docker container proxy (recomendada — consistente con el resto del stack)

Crear un container Nginx que haga proxy a host:8003:

```bash
ssh vps-aurenix

# Crear configuración nginx
mkdir -p /data/orbit-proxy
cat > /data/orbit-proxy/nginx.conf << 'EOF'
server {
    listen 80;
    location / {
        proxy_pass http://172.17.0.1:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Levantar container proxy con labels Traefik
BT=$(printf "\x60")
docker run -d \
  --name orbit-proxy \
  --restart unless-stopped \
  -v /data/orbit-proxy/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  -l "traefik.enable=true" \
  -l "traefik.http.routers.orbit.rule=Host(${BT}orbit.aurenix.cloud${BT})" \
  -l "traefik.http.routers.orbit.tls=true" \
  -l "traefik.http.routers.orbit.tls.certresolver=letsencrypt" \
  -l "traefik.http.services.orbit.loadbalancer.server.port=80" \
  nginx:alpine
```

### Opción B: Traefik file provider (si prefieres sin Docker proxy)

Crear `/data/traefik/dynamic/orbit.yml`:
```yaml
http:
  routers:
    orbit:
      rule: "Host(`orbit.aurenix.cloud`)"
      service: orbit
      tls:
        certResolver: letsencrypt
  services:
    orbit:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:8003"
```

Requiere que Traefik tenga file provider configurado apuntando a ese directorio.

### Verificar que funciona
```bash
# Desde VPS
ssh vps-aurenix "curl -s http://localhost:8003/health"

# Desde local (después de DNS propagado)
curl https://orbit.aurenix.cloud/health
```

---

## 7. DNS

Añadir registro A en el panel DNS de aurenix.cloud (Cloudflare o el registrador):
```
orbit.aurenix.cloud  A  76.13.9.238  TTL: 300
```

---

## 8. Deploy de Actualizaciones (Después del primer deploy)

El GitHub Action `deploy-orbit.yml` automatiza esto. Para deploy manual:

```bash
ssh vps-aurenix "
  cd /opt/orbit-repo
  git pull origin main
  cd /opt/orbit
  source venv/bin/activate
  pip install -r requirements.txt --quiet
  # alembic upgrade head  # Si hay migraciones
  systemctl restart orbit
  sleep 3
  systemctl is-active orbit && echo 'OK' || echo 'FAILED'
  curl -sf http://localhost:8003/health && echo 'Health check OK' || echo 'Health check FAILED'
"
```

---

## 9. Monitoring

### Integración con S1 VPS Guard
S1 ya monitorea el servidor. Para añadir Orbit al health check, editar el comando SSH mega en `Flujo_S1_Health_Collector.json` y añadir:
```bash
systemctl is-active orbit 2>/dev/null && echo "orbit:active" || echo "orbit:inactive"
```

### Logs centralizados
Los logs de Orbit se escriben en `/opt/orbit/logs/`. Para incluirlos en el backup de Filebrowser o en rotación de logs:
```bash
# Añadir logrotate para Orbit
cat > /etc/logrotate.d/orbit << 'EOF'
/opt/orbit/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    postrotate
        systemctl kill -s HUP orbit 2>/dev/null || true
    endscript
}
EOF
```

---

## 10. Checklist de Deploy

- [ ] PostgreSQL: DB `orbit_db` creada y usuario `orbit_user` con permisos
- [ ] Código clonado en `/opt/orbit`
- [ ] Virtualenv creado y dependencias instaladas
- [ ] `/opt/orbit/.env` creado con SECRET_KEY aleatorio
- [ ] Endpoint `/health` existe en main.py
- [ ] `orbit.service` creado y activo (`systemctl status orbit` = active)
- [ ] `curl localhost:8003/health` responde `{"status": "ok"}`
- [ ] Container Docker proxy levantado con labels Traefik (Opción A)
- [ ] Registro DNS A creado para `orbit.aurenix.cloud`
- [ ] `curl https://orbit.aurenix.cloud/health` responde OK
- [ ] GitHub Secrets configurados: VPS_IP, VPS_SSH_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_ID_JOSE
- [ ] GitHub Action `deploy-orbit.yml` verificado en Actions tab

---

*Última actualización: Marzo 2026 — AURENIX IT Agent Senior*
