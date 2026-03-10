# Orbit — Guía de Deploy en VPS

**URL producción**: `https://orbit.aurenix.cloud`
**VPS**: 76.13.9.238 | Ubuntu 24.04 | ID 1285851
**Puerto**: 8003

---

## Cómo acceder al VPS

Abre **Hostinger → VPS → Consola** (web terminal en el panel).
O si tienes SSH configurado: `ssh root@76.13.9.238`

Si usas SSH desde otro equipo, añadir la deploy key:
```bash
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJhYByLG++hpwCbkSJbia+kpTzIkBhZaBsCsc9K3pbuF orbit-deploy" >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
# Abrir puerto SSH si UFW está activo:
ufw allow 22/tcp
```

Luego desde PC: `ssh -i ~/.ssh/orbit_deploy root@76.13.9.238`

---

## Paso 1 — Clonar código en el VPS

```bash
# Instalar git si no está
apt-get install -y git

# Clonar el repo (sustituir TOKEN por tu GitHub PAT)
git clone https://TOKEN@github.com/AURENIX-ADMIN/SIACompleto.git /tmp/siacompleto

# Copiar solo orbit/ a /opt/orbit
mkdir -p /opt/orbit
cp -r /tmp/siacompleto/business-ideas/orbit/. /opt/orbit/
rm -rf /tmp/siacompleto
```

---

## Paso 2 — Ejecutar setup automatizado

```bash
cd /opt/orbit
bash scripts/setup_vps.sh
```

El script:
- Instala Python 3.11, PostgreSQL, build tools
- Crea usuario sistema `orbit`
- Crea DB `orbit_db` + usuario `orbit_user` con password aleatorio (**ANOTA EL PASSWORD**)
- Instala venv + dependencias
- Registra `orbit.service` en systemd

---

## Paso 3 — Crear .env de producción

```bash
nano /opt/orbit/.env
```

Contenido completo:
```
PORT=8003
ENVIRONMENT=production
ALLOWED_HOSTS=orbit.aurenix.cloud

SECRET_KEY=fa7139c16e27f7c780d81889d90660e692f3faeb2a617e1648008f22d1ae1c610b71054564a388787bc692e1de92b0476022255cd4ffb4b8fe403d17d24b3fcf
JWT_SECRET_KEY=840cbe2229a994acce5f42da5aedf52d18cf2606da4f32a0c4173a7dd11b47d92cf91ea07af7c64dab4499bef03e8271f44c81637c2478aaf394b2930b3d639b
INTERNAL_API_KEY=0a901127657b16b169668b13925ca4019b814b092e8a51f9cedf67f4ecc78fb8

# Sustituir <DB_PASSWORD> con el password generado en el paso 2
DATABASE_URL=postgresql+asyncpg://orbit_user:<DB_PASSWORD>@localhost:5432/orbit_db

ADMIN_EMAIL=admin@aurenix.es
ADMIN_PASSWORD=<password seguro para el admin>

TELEGRAM_BOT_TOKEN=<token del bot Orbit — dejar vacío si no hay>
TELEGRAM_ADMIN_CHAT_ID=5529992654

HOSTINGER_API_TOKEN=<tu token API de Hostinger>
HOSTINGER_VPS_ID=1285851

N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=<obtener de n8n UI → Settings → API Keys>
```

---

## Paso 4 — Inicializar base de datos

```bash
cd /opt/orbit
sudo -u orbit .venv/bin/python scripts/setup_db.py
```

Salida esperada: crea tablas, usuario admin, cliente AURENIX-Internal.
**Guarda el CLIENT_ID** que imprime (lo necesitas para el agente).

---

## Paso 5 — Arrancar servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable orbit
sudo systemctl start orbit
sudo systemctl status orbit
# Debe mostrar "Active: active (running)"
journalctl -u orbit -f   # logs en vivo (Ctrl+C para salir)
```

---

## Paso 6 — Cloudflare Tunnel

```bash
nano /etc/cloudflared/config.yml
```

Añadir al inicio de la sección `ingress:`:
```yaml
  - hostname: orbit.aurenix.cloud
    service: http://localhost:8003
```

Guardar y reiniciar:
```bash
sudo systemctl restart cloudflared
```

Verificar en el navegador: `https://orbit.aurenix.cloud`

---

## Paso 7 — Verificación funcional

1. Abrir `https://orbit.aurenix.cloud` → debe cargar el login
2. Login con `admin@aurenix.es` + tu ADMIN_PASSWORD
3. Crear cliente AURENIX desde la UI (o ya está creado por setup_db.py)
4. Generar token agente: `cd /opt/orbit && sudo -u orbit .venv/bin/python main.py add-token <CLIENT_ID>`
5. Anotar el token

---

## Paso 8 — Importar workflows n8n

En `https://n8n.aurenix.cloud`:

1. Crear credencial Telegram: Settings → Credentials → New → Telegram API
   - Name: `Orbit Telegram`
   - Bot token: el de tu bot Orbit

2. Importar `orbit/n8n/workflows/health_monitor.json`
3. Importar `orbit/n8n/workflows/cost_alert.json`
4. Activar ambos workflows

> Los JSONs ya tienen las URLs y claves hardcoded (no necesitan env vars de n8n).

---

## Paso 9 — Instalar agente en VPS (AURENIX interno)

```bash
# En VPS, como root:
ORBIT_URL=https://orbit.aurenix.cloud
AGENT_TOKEN=<token del paso 7>
CLIENT_ID=<CLIENT_ID del paso 4>

# Descargar e instalar agente
cp /opt/orbit/scripts/install_agent.sh /tmp/
chmod +x /tmp/install_agent.sh
/tmp/install_agent.sh "$ORBIT_URL" "$AGENT_TOKEN" "$CLIENT_ID"
```

Dentro de 5 minutos debería aparecer un heartbeat verde en el dashboard.

---

## Notas de producción

- Logs del servicio: `journalctl -u orbit -f`
- Restart: `systemctl restart orbit`
- DB: `sudo -u postgres psql orbit_db`
- Config actual: `/opt/orbit/.env`
- Si UFW está activo: asegúrate de que puerto 8003 NO esté abierto al exterior (solo Cloudflare/localhost)
