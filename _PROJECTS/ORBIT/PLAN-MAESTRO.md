# PLAN-MAESTRO — Orbit by AURENIX

Panel de control operacional interno para gestionar clientes, sistemas desplegados,
monitorización en tiempo real, costes y onboarding.

---

## Índice

1. [Vision del Producto](#1-vision-del-producto)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Stack Tecnico](#3-stack-tecnico)
4. [Estructura de Carpetas](#4-estructura-de-carpetas)
5. [Variables de Entorno](#5-variables-de-entorno)
6. [Plan de Fases](#6-plan-de-fases)
7. [Checklist Global de Progreso](#7-checklist-global-de-progreso)
8. [Modelo de Datos](#8-modelo-de-datos)
9. [Despliegue en Servidor](#9-despliegue-en-servidor)
10. [Metricas Clave](#10-metricas-clave)

---

## 1. Vision del Producto

### Que es Orbit

Orbit es el centro de control operacional de AURENIX. Un dashboard interno que
proporciona visibilidad total sobre todos los clientes activos, los sistemas de
automatizacion desplegados en sus servidores, el estado de salud en tiempo real,
el consumo de recursos y los costes asociados a cada instalacion.

**Problema que resuelve:** Sin Orbit, un fallo en el servidor de un cliente se
detecta cuando el cliente llama. Con Orbit, AURENIX lo detecta antes que el cliente.

**Flujo end-to-end:**

```
VPS Cliente A                    VPS AURENIX (Orbit)              Equipo AURENIX
─────────────                    ───────────────────              ──────────────
orbit_agent.py                   FastAPI :8003                    Navegador web
    │                                │                                 │
    ├─ heartbeat cada 5min ─────────>│                                 │
    │  (HMAC firmado)                ├─ guarda en PostgreSQL           │
    │                                ├─ detecta anomalia               │
    │                                ├─ crea alerta ─────────────────> Telegram
    │                                │                                 │
    │<─ pull metricas cada 60min ────┤                                 │
    │  (tokens Claude, n8n stats)    ├─ actualiza dashboard ──────────>│ ve dashboard
    │                                │                                 │
    │                                │<─── GET / (admin) ─────────────│
    │                                │──── renderiza HTML ────────────>│
```

### Principios de diseno

- **Seguridad primero**: cada capa tiene su propia autenticacion, nunca se asume
  que la capa anterior es suficiente
- **Silencio inteligente**: no genera ruido — solo alerta cuando hay algo accionable
- **Escalable desde el dia 1**: el modelo de datos soporta 1 o 100 clientes sin
  cambios estructurales
- **Cero dependencia de terceros para el core**: si cae Telegram, Notion o cualquier
  servicio externo, el dashboard sigue funcionando

---

## 2. Arquitectura del Sistema

```
                          INTERNET
                             │
                   ┌─────────▼──────────┐
                   │  Cloudflare Access  │  Zero-trust: bloquea todo excepto
                   │  (Zero Trust)       │  emails/IPs de AURENIX autorizados
                   └─────────┬──────────┘
                             │
                   ┌─────────▼──────────┐
                   │  Cloudflare Tunnel  │  HTTPS terminado aqui
                   │  orbit.aurenix.cloud│  Puerto 8003 nunca expuesto
                   └─────────┬──────────┘
                             │
            ┌────────────────▼────────────────────┐
            │         VPS AURENIX                  │
            │                                      │
            │  ┌──────────────────────────────┐   │
            │  │   FastAPI :8003 (Orbit API)   │   │
            │  │   ├── /auth        JWT auth   │   │
            │  │   ├── /clients     CRUD        │   │
            │  │   ├── /systems     estado      │   │
            │  │   ├── /heartbeat   receptor    │   │
            │  │   ├── /metrics     consultas   │   │
            │  │   └── /alerts      incidentes  │   │
            │  │   Rate limiting + HMAC verify  │   │
            │  └──────────────┬───────────────┘   │
            │                 │                    │
            │  ┌──────────────▼───────────────┐   │
            │  │   PostgreSQL (local)          │   │
            │  │   Solo accesible desde        │   │
            │  │   localhost:5432              │   │
            │  └───────────────────────────────┘   │
            │                                      │
            │  ┌───────────────────────────────┐   │
            │  │   n8n (scheduler)             │   │
            │  │   Workflows de monitorizacion │   │
            │  │   y alertas automaticas       │   │
            │  └───────────────────────────────┘   │
            └──────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼──┐  ┌────────▼───┐  ┌──────▼──────┐
    │ VPS Cliente│  │ VPS Cliente│  │ VPS Cliente │
    │     A      │  │     B      │  │     C       │
    │            │  │            │  │             │
    │ orbit_agent│  │ orbit_agent│  │ orbit_agent │
    │ (Python)   │  │ (Python)   │  │ (bash)      │
    │            │  │            │  │             │
    │ Resona     │  │ Resona     │  │ Asistente   │
    │ NEXO       │  │            │  │ Personal    │
    └────────────┘  └────────────┘  └─────────────┘
```

### Seguridad en capas

```
Capa 1 — Cloudflare Access
  Regla: solo correos @aurenix.es pueden autenticarse via OTP
  Resultado: ninguna peticion no autorizada llega al servidor

Capa 2 — Cloudflare Tunnel
  Puerto 8003 vinculado al tunnel, no expuesto en firewall
  Resultado: la IP del servidor es invisible para atacantes

Capa 3 — FastAPI + JWT
  Login con bcrypt (cost factor 12) + JWT firmado (RS256, expira en 8h)
  Rate limiting: max 10 intentos de login por IP en 5 minutos -> bloqueo 15min
  Resultado: fuerza bruta imposible en la practica

Capa 4 — HMAC en heartbeats de agente
  Cada cliente tiene un AGENT_TOKEN unico (32 bytes aleatorios)
  Cada payload lleva timestamp + HMAC-SHA256 con ese token
  Rechazamos mensajes con timestamp > 5 minutos de antiguedad (anti-replay)
  Resultado: un agente comprometido no puede suplantar a otro cliente

Capa 5 — PostgreSQL local
  Usuario orbit_user con permisos minimos (solo sobre schema orbit)
  Solo accesible desde localhost
  Sin superuser, sin acceso remoto
```

### Protocolo de heartbeat (agente -> Orbit)

```
POST https://orbit.aurenix.cloud/heartbeat
Headers:
  X-Client-ID: <client_id>          # UUID del cliente
  X-Timestamp: 1741234567           # Unix timestamp
  X-Signature: <hmac-sha256>        # HMAC(client_id + timestamp + body, AGENT_TOKEN)
Body (JSON):
{
  "status": "healthy",              # healthy | degraded | critical
  "services": {                     # estado de cada servicio en ese VPS
    "fastapi": {"up": true, "response_ms": 45},
    "n8n": {"up": true, "active_workflows": 3},
    "postgresql": {"up": true},
    "telegram_bot": {"up": true, "last_message_ago_s": 120}
  },
  "system": {                       # metricas del OS
    "cpu_pct": 12.4,
    "ram_pct": 67.2,
    "disk_pct": 34.1
  },
  "agent_version": "1.0.0"
}
```

### Protocolo de pull de metricas (Orbit -> agente)

```
GET https://<client-domain>/orbit/metrics
Headers:
  X-Orbit-Key: <client_pull_key>    # API key separada para pull, solo lectura
Response (JSON):
{
  "period": "last_hour",
  "claude_usage": {
    "haiku_tokens": 45230,
    "sonnet_tokens": 8100,
    "estimated_cost_eur": 0.087
  },
  "n8n_executions": {
    "total": 48,
    "failed": 1,
    "workflows": [
      {"name": "Resona hourly poll", "last_run": "2026-03-07T14:00:00", "status": "success"}
    ]
  },
  "system_metrics": {              # metricas especificas del/los sistemas instalados
    "resona": {
      "reviews_processed_today": 12,
      "responses_published": 10,
      "pending_approval": 2,
      "avg_response_time_ms": 2340
    }
  }
}
```

---

## 3. Stack Tecnico

| Herramienta | Componente | Razon |
|-------------|-----------|-------|
| Python 3.11 | Runtime backend | Consistente con todo el stack AURENIX |
| FastAPI | API y servidor de templates | Async, rapido, tipado, mismo patron que otros proyectos |
| SQLAlchemy 2.0 | ORM | Previene SQL injection, migraciones limpias |
| Alembic | Migraciones de BD | Control de versiones del schema |
| PostgreSQL 15 | Base de datos | Ya en el servidor, robusto, transaccional |
| Jinja2 | Templates HTML | Sin build pipeline, SSR limpio |
| HTMX | Interactividad frontend | Actualizaciones parciales sin SPA compleja |
| Alpine.js | Microinteractividad | Dropdowns, modals, toggles sin framework pesado |
| Tailwind CSS (CDN) | Estilos | Utility-first, estética premium alcanzable |
| Chart.js | Graficas | Ligero, suficiente para uptime y costes |
| python-jose | JWT | Tokens de sesion seguros |
| passlib + bcrypt | Hash de passwords | Estandar de la industria |
| slowapi | Rate limiting | Limitar intentos de login y endpoints criticos |
| httpx | Cliente HTTP async | Pull de metricas desde VPS cliente |
| python-telegram-bot | Notificaciones | Ya integrado en el stack AURENIX |
| Pydantic v2 | Validacion | Validacion estricta en todos los endpoints |
| systemd | Process management | Mismo patron que Resona y otros servicios |
| Cloudflare Tunnel | HTTPS | Ya configurado, mismo patron |
| Cloudflare Access | Zero-trust auth | Capa extra de seguridad antes de llegar a FastAPI |

---

## 4. Estructura de Carpetas

```
dashboard/
├── PLAN-MAESTRO.md              # Este documento
├── README.md                    # Setup rapido
├── main.py                      # CLI: python main.py serve | setup | add-client
├── requirements.txt
├── .env.example
│
├── config/
│   └── settings.py              # Pydantic BaseSettings con todas las vars de entorno
│
├── src/
│   ├── api/
│   │   ├── server.py            # FastAPI app factory, middleware, routers
│   │   ├── middleware/
│   │   │   ├── auth.py          # JWT validation middleware
│   │   │   └── rate_limiter.py  # slowapi rate limiting config
│   │   └── routes/
│   │       ├── auth.py          # POST /auth/login, POST /auth/logout, GET /auth/me
│   │       ├── clients.py       # CRUD de clientes + vista detalle
│   │       ├── systems.py       # CRUD de sistemas + estado + metricas
│   │       ├── heartbeat.py     # POST /heartbeat (receptor publico, solo HMAC auth)
│   │       ├── metrics.py       # GET metricas historicas, costes
│   │       ├── alerts.py        # GET/PATCH alertas (ack, resolve, silence)
│   │       └── onboarding.py    # CRUD checklist de onboarding por cliente
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── base.py              # DeclarativeBase compartida
│   │   ├── user.py              # Tabla users (equipo AURENIX)
│   │   ├── client.py            # Tabla clients
│   │   ├── system.py            # Tabla systems
│   │   ├── agent_token.py       # Tabla agent_tokens
│   │   ├── heartbeat.py         # Tabla heartbeats (time series)
│   │   ├── metric.py            # Tabla system_metrics (time series)
│   │   ├── alert.py             # Tabla alerts
│   │   ├── cost_record.py       # Tabla cost_records
│   │   └── onboarding.py        # Tablas onboarding_checklists + checklist_items
│   │
│   ├── schemas/                 # Pydantic schemas (request/response validation)
│   │   ├── auth.py
│   │   ├── client.py
│   │   ├── system.py
│   │   ├── heartbeat.py
│   │   ├── metric.py
│   │   └── alert.py
│   │
│   ├── services/
│   │   ├── auth_service.py      # Login, JWT issue/verify, password hash
│   │   ├── hmac_service.py      # Verificacion de firmas HMAC de agentes
│   │   ├── health_puller.py     # Pull async de metricas a VPS cliente cada 60min
│   │   ├── alert_service.py     # Logica de creacion y escalado de alertas
│   │   ├── cost_tracker.py      # Agregacion de costes Claude + VPS por cliente/mes
│   │   └── n8n_client.py        # Cliente para API de n8n (leer estado de workflows)
│   │
│   ├── agent/
│   │   ├── orbit_agent.py       # Agente completo Python 3.8+ para VPS cliente
│   │   └── orbit_heartbeat.sh   # Agente minimo bash+curl para VPS sin Python
│   │
│   └── notifications/
│       └── telegram_notifier.py # Alertas a Telegram (bot existente de AURENIX)
│
├── templates/                   # Jinja2 HTML
│   ├── base.html                # Layout base: nav, sidebar, scripts
│   ├── home.html                # Command center: grid de clientes + feed alertas
│   ├── client_detail.html       # Vista detalle de un cliente
│   ├── system_detail.html       # Vista detalle de un sistema: uptime, metricas, logs
│   ├── alerts.html              # Centro de alertas con filtros
│   ├── costs.html               # Vista de costes y margenes
│   └── onboarding.html          # Pipeline de onboarding de nuevos clientes
│
├── static/
│   ├── css/
│   │   └── orbit.css            # Variables de color, fuentes, estilos custom
│   └── js/
│       └── orbit.js             # Chart.js configs, helpers Alpine
│
├── n8n/
│   └── workflows/
│       ├── health_monitor.json  # Comprueba heartbeats perdidos cada 10min
│       └── cost_alert.json      # Alerta si consumo Claude supera umbral mensual
│
└── scripts/
    ├── setup_db.py              # Inicializa BD, crea tablas, crea usuario admin
    └── install_agent.sh         # Script de instalacion del agente en VPS cliente
```

---

## 5. Variables de Entorno

```env
# ─── SERVIDOR ────────────────────────────────────────────────
PORT=8003
ENVIRONMENT=production           # development | production
SECRET_KEY=                      # 64 bytes hex aleatorios (openssl rand -hex 64)
ALLOWED_HOSTS=orbit.aurenix.cloud

# ─── BASE DE DATOS ───────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://orbit_user:CHANGE_ME@localhost:5432/orbit_db

# ─── AUTENTICACION JWT ───────────────────────────────────────
JWT_SECRET_KEY=                  # 64 bytes hex aleatorios (diferente de SECRET_KEY)
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=8

# ─── RATE LIMITING ───────────────────────────────────────────
RATE_LIMIT_LOGIN=10/5minutes     # max 10 intentos de login por IP en 5 minutos
RATE_LIMIT_API=200/minute        # max 200 req/min en endpoints generales

# ─── TELEGRAM (alertas internas AURENIX) ─────────────────────
TELEGRAM_BOT_TOKEN=              # Bot existente de AURENIX para alertas internas
TELEGRAM_ADMIN_CHAT_ID=          # Chat ID del equipo AURENIX

# ─── PULL DE METRICAS ────────────────────────────────────────
METRICS_PULL_INTERVAL_MINUTES=60 # Frecuencia de pull a VPS cliente
METRICS_PULL_TIMEOUT_SECONDS=10  # Timeout por peticion
HEARTBEAT_ALERT_AFTER_MINUTES=10 # Alerta si no llega heartbeat en X minutos

# ─── ALERTAS ─────────────────────────────────────────────────
ALERT_CPU_THRESHOLD_PCT=85       # Alerta si CPU supera este %
ALERT_RAM_THRESHOLD_PCT=90       # Alerta si RAM supera este %
ALERT_DISK_THRESHOLD_PCT=80      # Alerta si disco supera este %
ALERT_CLAUDE_COST_MONTHLY_EUR=   # Alerta si coste Claude/cliente supera X euros/mes

# ─── N8N (instancia AURENIX) ─────────────────────────────────
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=                     # API key de la instancia n8n de AURENIX

# ─── ADMIN ───────────────────────────────────────────────────
ADMIN_EMAIL=                     # Email del primer usuario admin
ADMIN_PASSWORD=                  # Password inicial (cambiar tras primer login)
```

---

## 6. Plan de Fases

---

### Fase 1 — Nucleo funcional
**Objetivo:** Dashboard operativo con auth, gestion de clientes/sistemas,
heartbeat receiver y alertas basicas. Al terminar esta fase, AURENIX puede
registrarse como su propio primer "cliente" y monitorizar sus sistemas actuales.
**Duracion estimada:** 2 semanas

**Tareas:**

1. Inicializacion del proyecto
   - Crear estructura de carpetas completa
   - `requirements.txt` con todas las dependencias
   - `config/settings.py` con Pydantic BaseSettings
   - `.env.example` completo

2. Base de datos
   - `scripts/setup_db.py`: crear usuario PostgreSQL `orbit_user`, base de datos
     `orbit_db`, schema inicial
   - SQLAlchemy models: users, clients, systems, agent_tokens, heartbeats, alerts
   - Alembic configurado para migraciones futuras

3. Autenticacion y seguridad
   - `src/services/auth_service.py`: login con bcrypt, JWT issue/verify
   - `src/api/middleware/auth.py`: validacion de JWT en cada request protegida
   - `src/api/middleware/rate_limiter.py`: slowapi configurado
   - `src/api/routes/auth.py`: POST /auth/login, POST /auth/logout
   - Primer usuario admin creado via `scripts/setup_db.py`

4. CRUD de clientes y sistemas
   - `src/api/routes/clients.py`: listar, crear, editar, desactivar clientes
   - `src/api/routes/systems.py`: listar por cliente, crear, cambiar estado manual,
     desactivar
   - Enums: SystemStatus (operativo/degradado/caido/en_construccion/mantenimiento),
     SystemType (resona/nexo/asistente_personal/ocr_facturas/custom)

5. Receptor de heartbeats
   - `src/services/hmac_service.py`: verificacion HMAC-SHA256 + validacion timestamp
   - `src/api/routes/heartbeat.py`: POST /heartbeat (sin JWT, solo HMAC)
   - Guardar en tabla heartbeats, actualizar last_seen en systems
   - Deteccion de heartbeat perdido: job async cada 5 minutos que revisa
     sistemas con last_seen > HEARTBEAT_ALERT_AFTER_MINUTES

6. Sistema de alertas basico
   - `src/models/alert.py`: tabla alerts con severity, status (open/acked/resolved)
   - `src/services/alert_service.py`: crear alerta, deduplicar (no crear la misma
     alerta dos veces si sigue abierta), escalar a Telegram
   - `src/api/routes/alerts.py`: listar, acknowledge, resolver, silenciar X horas
   - `src/notifications/telegram_notifier.py`: envio de alertas criticas a Telegram

7. Agente para VPS cliente
   - `src/agent/orbit_agent.py`: script Python 3.8+ standalone
     - Comprueba estado de FastAPI local (GET /health), n8n API, PostgreSQL,
       Telegram bot (heartbeat fresco < 3 min)
     - Comprueba CPU, RAM, disco con psutil
     - Firma el payload con HMAC-SHA256
     - POST al endpoint /heartbeat de Orbit
     - Corre como servicio systemd cada 5 minutos
   - `src/agent/orbit_heartbeat.sh`: script bash+curl minimo
     - Solo openssl + curl (cero dependencias Python)
     - Envia heartbeat basico firmado
     - Fallback para VPS sin Python
   - `scripts/install_agent.sh`: detecta Python disponible, instala el agente
     adecuado, crea servicio systemd

8. Frontend — Home y vistas basicas
   - `templates/base.html`: layout con sidebar (clientes, alertas, costes),
     topbar con estado global, tema oscuro elegante
   - `templates/home.html`: grid de tarjetas de clientes con semaforo de salud,
     MRR total, contador sistemas operativos/total, feed de alertas recientes
   - `templates/client_detail.html`: sistemas del cliente, estado de cada uno,
     ultimo heartbeat, acciones rapidas
   - `templates/alerts.html`: feed cronologico con filtros, botones ack/resolve
   - HTMX polling cada 30 segundos en home para refrescar estados sin reload

---

### Fase 2 — Metricas, costes y n8n
**Objetivo:** Incorporar datos ricos de metricas de negocio, tracking de costes
reales de Claude por cliente y estado de workflows de n8n.
**Duracion estimada:** 2 semanas

**Tareas:**

1. Endpoint de metricas en sistemas cliente
   - Definir contrato de API `/orbit/metrics` que cada sistema AURENIX expone
   - Implementar en Resona: reviews procesadas, tasa respuesta, pendientes
   - Implementar en Investment Copilot: edicion generada, drips enviados, tokens
   - Wrapper de logging de Claude tokens: decorador async que registra en
     `/data/orbit_metrics.jsonl` sin bloquear la llamada principal

2. Pull de metricas
   - `src/services/health_puller.py`: job async que corre cada 60 minutos,
     itera todos los sistemas activos, hace GET a su endpoint de metricas,
     guarda en tabla system_metrics
   - Manejo de timeouts: si el VPS no responde en 10s, registrar como error
     sin bloquear el ciclo

3. Tracking de costes
   - `src/models/cost_record.py`: registro mensual de costes por sistema
     (claude_haiku_eur, claude_sonnet_eur, vps_eur, total_eur)
   - `src/services/cost_tracker.py`: agrega registros de system_metrics para
     calcular coste mensual acumulado; calcula margen (MRR - COGS)
   - `src/api/routes/metrics.py`: endpoints para consultar costes por cliente,
     por sistema, por mes
   - Alerta automatica si coste Claude supera umbral configurado

4. Integracion n8n
   - `src/services/n8n_client.py`: cliente para API REST de n8n
     - GET workflows activos
     - GET ultimas ejecuciones (estado, duracion, errores)
   - Mostrar workflows de n8n en vista detalle de sistema

5. Frontend — Vistas de metricas y costes
   - `templates/system_detail.html`: grafica de uptime estilo contribution graph
     (30 dias, celda por dia coloreada por disponibilidad), metricas de negocio
     del sistema, workflows n8n, log de alertas del sistema
   - `templates/costs.html`: tabla por cliente con MRR / COGS / margen,
     grafica de evolucion mensual con Chart.js, desglose por modelo Claude

6. Workflows n8n para monitorizacion automatica
   - `n8n/workflows/health_monitor.json`: se ejecuta cada 10 minutos, llama
     a GET /orbit/systems/unhealthy, si hay sistemas caidos envia resumen a Telegram
   - `n8n/workflows/cost_alert.json`: se ejecuta diariamente, comprueba costes
     acumulados del mes, alerta si algun cliente supera el 70% del margen

---

### Fase 3 — Onboarding y UX premium
**Objetivo:** Pipeline de onboarding para nuevos clientes y refinamiento visual
completo del dashboard.
**Duracion estimada:** 1 semana

**Tareas:**

1. Sistema de onboarding
   - `src/models/onboarding.py`: tablas onboarding_checklists y checklist_items
   - Checklist generado automaticamente al crear un nuevo cliente con los pasos
     estandar de la Fase 0 al 3
   - Al anadir un sistema al cliente, se anade automaticamente su fila en Fase 2
   - `src/api/routes/onboarding.py`: CRUD de items, marcar completado, anadir notas
   - `templates/onboarding.html`: vista kanban por fases, progreso visual por cliente

2. Refinamiento visual
   - Paleta de colores definida: fondo muy oscuro (#0d1117), acentos en azul electrico
     (#2563eb) y verde operativo (#10b981), rojo critico (#ef4444), amarillo degradado
     (#f59e0b)
   - Fuentes: Inter para UI, JetBrains Mono para datos tecnicos
   - Tarjetas de cliente con gradiente sutil, bordes con glow de color segun estado
   - Graficas de uptime con Chart.js: barras de disponibilidad diaria 30d
   - Favicon y meta tags

3. Funcionalidades UX
   - Filtros en home: por estado, por sistema tipo, por cliente
   - Busqueda global de clientes y sistemas
   - Vista compacta / vista expandida toggle
   - Indicador de tiempo desde ultimo heartbeat en tiempo real (contador regresivo)
   - Toast notifications para acciones (ack, resolve) via Alpine.js

---

### Fase 4 — Automatizacion avanzada y robustez
**Objetivo:** Reportes automaticos, gestion de tokens de agente, escalabilidad.
**Duracion estimada:** 1 semana

**Tareas:**

1. Gestion de tokens de agente
   - Endpoint admin para rotar AGENT_TOKEN de un cliente sin downtime
   - Log de cuando fue usado por ultima vez cada token
   - Alerta si un token no es usado en >15 minutos (posible caida del agente)

2. Reporte semanal automatico
   - Workflow n8n: cada lunes a las 9:00 genera resumen de la semana
   - Contenido: clientes con incidentes, tiempo medio de resolucion, consumo
     Claude top 3 clientes, MRR total AURENIX
   - Enviado a Telegram del equipo

3. API para sistemas AURENIX
   - Endpoint GET /orbit/my-status que los propios sistemas de AURENIX pueden
     consultar para saber si Orbit los considera saludables
   - Util para que un sistema se autodiagnostique antes de ejecutar tareas criticas

4. Backup y recuperacion
   - Script de backup diario de PostgreSQL orbit_db a fichero comprimido
   - Rotacion de backups (mantener ultimos 30 dias)
   - Documentacion de procedimiento de restauracion

---

## 7. Checklist Global de Progreso

### Fase 1 — Nucleo funcional
- [ ] Estructura de carpetas creada
- [ ] requirements.txt completado
- [ ] config/settings.py con todas las vars
- [ ] setup_db.py funcional (crea BD y usuario)
- [ ] SQLAlchemy models: users, clients, systems, agent_tokens, heartbeats, alerts
- [ ] Alembic configurado
- [ ] auth_service.py: login + JWT
- [ ] middleware/auth.py: validacion JWT
- [ ] middleware/rate_limiter.py: slowapi
- [ ] routes/auth.py: login/logout
- [ ] routes/clients.py: CRUD completo
- [ ] routes/systems.py: CRUD + cambio de estado
- [ ] hmac_service.py: verificacion HMAC + timestamp
- [ ] routes/heartbeat.py: receptor con HMAC auth
- [ ] Job de deteccion de heartbeat perdido
- [ ] alert_service.py: crear + deduplicar + escalar
- [ ] routes/alerts.py: listar + ack + resolve + silence
- [ ] telegram_notifier.py: alertas a Telegram
- [ ] orbit_agent.py: agente Python completo
- [ ] orbit_heartbeat.sh: agente bash minimal
- [ ] install_agent.sh: detector + instalador
- [ ] templates/base.html: layout con sidebar
- [ ] templates/home.html: grid clientes + feed alertas
- [ ] templates/client_detail.html: sistemas + estados
- [ ] templates/alerts.html: feed con filtros
- [ ] HTMX polling 30s en home
- [ ] Primer cliente "AURENIX" registrado
- [ ] Primer heartbeat recibido desde investment-copilot

### Fase 2 — Metricas, costes y n8n
- [ ] Contrato API /orbit/metrics definido
- [ ] Endpoint /orbit/metrics implementado en Resona
- [ ] Endpoint /orbit/metrics implementado en Investment Copilot
- [ ] Wrapper de logging de tokens Claude (no bloqueante)
- [ ] health_puller.py: pull async cada 60 min
- [ ] Modelos system_metrics y cost_records
- [ ] cost_tracker.py: calculo de costes y margen
- [ ] routes/metrics.py: endpoints de consulta
- [ ] Alerta por coste Claude superado
- [ ] n8n_client.py: workflows + ejecuciones
- [ ] templates/system_detail.html: uptime graph + metricas + n8n
- [ ] templates/costs.html: tabla margenes + grafica
- [ ] n8n workflow health_monitor.json
- [ ] n8n workflow cost_alert.json

### Fase 3 — Onboarding y UX premium
- [ ] Modelo onboarding_checklists + checklist_items
- [ ] Generacion automatica de checklist al crear cliente
- [ ] routes/onboarding.py
- [ ] templates/onboarding.html: kanban por fases
- [ ] Paleta de colores y variables CSS aplicadas
- [ ] Fuentes Inter + JetBrains Mono integradas
- [ ] Tarjetas con glow segun estado de salud
- [ ] Graficas Chart.js de uptime 30 dias
- [ ] Filtros y busqueda global en home
- [ ] Toast notifications con Alpine.js

### Fase 4 — Automatizacion avanzada
- [ ] Rotacion de AGENT_TOKEN desde admin
- [ ] Log de ultimo uso por token
- [ ] Alerta por token inactivo > 15 min
- [ ] Workflow n8n reporte semanal lunes 9:00
- [ ] Endpoint GET /orbit/my-status
- [ ] Script de backup diario PostgreSQL
- [ ] Rotacion de backups (30 dias)

---

## 8. Modelo de Datos

### PostgreSQL — Schema orbit

```sql
-- Usuarios del dashboard (equipo AURENIX)
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,       -- bcrypt hash
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Clientes de AURENIX
CREATE TABLE clients (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,          -- nombre de la empresa cliente
    slug        VARCHAR(100) UNIQUE NOT NULL,   -- identificador URL-safe
    plan        VARCHAR(50) NOT NULL,           -- basic | pro | enterprise
    mrr_eur     NUMERIC(10,2) DEFAULT 0,        -- ingreso mensual recurrente
    vps_cost_eur NUMERIC(10,2) DEFAULT 0,       -- coste del VPS mensual
    contact_email VARCHAR(255),
    contact_name VARCHAR(255),
    notes       TEXT,
    is_active   BOOLEAN DEFAULT true,
    started_at  DATE,                           -- fecha inicio del servicio
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

-- Sistemas de automatizacion por cliente
CREATE TABLE systems (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id   UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name        VARCHAR(255) NOT NULL,          -- nombre descriptivo
    system_type VARCHAR(50) NOT NULL,           -- resona | nexo | asistente_personal |
                                               -- ocr_facturas | custom
    status      VARCHAR(30) NOT NULL DEFAULT 'en_construccion',
                                               -- operativo | degradado | caido |
                                               -- en_construccion | mantenimiento
    base_url    VARCHAR(500),                  -- URL del sistema en el VPS cliente
    pull_key    VARCHAR(255),                  -- API key para pull de metricas (solo lectura)
    last_heartbeat_at TIMESTAMPTZ,
    last_metrics_at   TIMESTAMPTZ,
    uptime_30d  NUMERIC(5,2),                  -- % uptime ultimos 30 dias (cache)
    notes       TEXT,
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

-- Tokens de autenticacion para agentes en VPS cliente
CREATE TABLE agent_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id   UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL,         -- SHA-256 del token (no guardamos el token en claro)
    label       VARCHAR(100),                  -- ej: "VPS principal", "VPS backup"
    last_used_at TIMESTAMPTZ,
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Heartbeats recibidos de agentes (time series)
CREATE TABLE heartbeats (
    id          BIGSERIAL PRIMARY KEY,
    system_id   UUID NOT NULL REFERENCES systems(id) ON DELETE CASCADE,
    received_at TIMESTAMPTZ DEFAULT now(),
    agent_status VARCHAR(20),                  -- healthy | degraded | critical
    fastapi_up  BOOLEAN,
    n8n_up      BOOLEAN,
    postgresql_up BOOLEAN,
    telegram_bot_up BOOLEAN,
    cpu_pct     NUMERIC(5,2),
    ram_pct     NUMERIC(5,2),
    disk_pct    NUMERIC(5,2),
    agent_version VARCHAR(20),
    raw_payload JSONB                          -- payload completo para auditoria
);
CREATE INDEX idx_heartbeats_system_time ON heartbeats(system_id, received_at DESC);

-- Metricas de negocio por sistema (time series)
CREATE TABLE system_metrics (
    id          BIGSERIAL PRIMARY KEY,
    system_id   UUID NOT NULL REFERENCES systems(id) ON DELETE CASCADE,
    collected_at TIMESTAMPTZ DEFAULT now(),
    -- Costes Claude (periodo = ultima hora)
    claude_haiku_tokens  BIGINT DEFAULT 0,
    claude_sonnet_tokens BIGINT DEFAULT 0,
    claude_cost_eur      NUMERIC(8,4) DEFAULT 0,
    -- n8n
    n8n_executions_total INTEGER DEFAULT 0,
    n8n_executions_failed INTEGER DEFAULT 0,
    -- Metricas especificas del sistema (flexible)
    custom_metrics JSONB DEFAULT '{}'          -- metricas propias de cada tipo
);
CREATE INDEX idx_metrics_system_time ON system_metrics(system_id, collected_at DESC);

-- Alertas e incidentes
CREATE TABLE alerts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_id   UUID REFERENCES systems(id) ON DELETE CASCADE,
    client_id   UUID REFERENCES clients(id) ON DELETE CASCADE,
    severity    VARCHAR(20) NOT NULL,          -- critica | alta | media | baja | info
    alert_type  VARCHAR(50) NOT NULL,          -- heartbeat_lost | service_down | high_cpu |
                                               -- high_cost | n8n_failures | disk_warning
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    status      VARCHAR(20) DEFAULT 'open',    -- open | acknowledged | resolved | silenced
    silenced_until TIMESTAMPTZ,
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES users(id),
    telegram_sent BOOLEAN DEFAULT false,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_alerts_status ON alerts(status, created_at DESC);

-- Registros de costes mensuales por sistema (agregados)
CREATE TABLE cost_records (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_id   UUID NOT NULL REFERENCES systems(id) ON DELETE CASCADE,
    client_id   UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    month       DATE NOT NULL,                 -- primer dia del mes: 2026-03-01
    claude_haiku_eur NUMERIC(8,4) DEFAULT 0,
    claude_sonnet_eur NUMERIC(8,4) DEFAULT 0,
    vps_share_eur NUMERIC(8,4) DEFAULT 0,      -- fraccion del VPS asignada a este sistema
    total_cost_eur NUMERIC(8,4) DEFAULT 0,
    mrr_eur     NUMERIC(10,2) DEFAULT 0,       -- snapshot del MRR ese mes
    margin_eur  NUMERIC(10,2) DEFAULT 0,       -- mrr - total_cost
    margin_pct  NUMERIC(5,2) DEFAULT 0,        -- (margin / mrr) * 100
    UNIQUE(system_id, month)
);

-- Checklists de onboarding por cliente
CREATE TABLE onboarding_checklists (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id   UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    phase       VARCHAR(50) NOT NULL,          -- pre_deployment | infra | systems | handoff
    phase_order INTEGER NOT NULL,
    title       VARCHAR(255) NOT NULL,
    is_completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMPTZ,
    completed_by UUID REFERENCES users(id),
    notes       TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);
```

### Datos de referencia — Tipos de sistema y sus metricas custom

```json
{
  "resona": {
    "reviews_processed_today": 0,
    "responses_published": 0,
    "pending_approval": 0,
    "avg_response_ms": 0
  },
  "nexo": {
    "edition_generated_today": false,
    "drips_sent_today": 0,
    "free_subscribers": 0,
    "premium_subscribers": 0
  },
  "asistente_personal": {
    "emails_processed_today": 0,
    "tasks_automated_today": 0,
    "avg_response_ms": 0
  },
  "ocr_facturas": {
    "invoices_processed_today": 0,
    "invoices_failed": 0,
    "avg_processing_ms": 0
  }
}
```

---

## 9. Despliegue en Servidor

### Prerequisitos

El VPS de AURENIX ya tiene: Python 3.11, PostgreSQL 15, n8n, cloudflared activo.

### Paso 1 — Clonar e instalar dependencias

```bash
cd /opt
git clone https://github.com/aurenix/orbit.git
cd orbit
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Paso 2 — Variables de entorno

```bash
cp .env.example .env
# Editar .env con valores reales
nano .env

# Generar claves seguras:
openssl rand -hex 64   # para SECRET_KEY
openssl rand -hex 64   # para JWT_SECRET_KEY
```

### Paso 3 — Base de datos

```bash
# Crear usuario y BD en PostgreSQL
sudo -u postgres psql <<EOF
CREATE USER orbit_user WITH PASSWORD 'CAMBIAR_POR_PASSWORD_SEGURO';
CREATE DATABASE orbit_db OWNER orbit_user;
GRANT ALL PRIVILEGES ON DATABASE orbit_db TO orbit_user;
\c orbit_db
CREATE SCHEMA orbit AUTHORIZATION orbit_user;
EOF

# Inicializar tablas y crear usuario admin
source venv/bin/activate
python scripts/setup_db.py
```

### Paso 4 — Servicio systemd

```bash
sudo nano /etc/systemd/system/orbit.service
```

```ini
[Unit]
Description=Orbit - AURENIX Control Dashboard
After=network.target postgresql.service

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/opt/orbit
EnvironmentFile=/opt/orbit/.env
ExecStart=/opt/orbit/venv/bin/python main.py serve
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable orbit
sudo systemctl start orbit
sudo systemctl status orbit
```

### Paso 5 — Cloudflare Tunnel

Anadir ruta en el tunnel existente de AURENIX:

```bash
# En el config del tunnel (~/.cloudflared/config.yml), anadir:
ingress:
  - hostname: orbit.aurenix.cloud
    service: http://localhost:8003
  # ... otras reglas existentes

# Recargar el tunnel
sudo systemctl restart cloudflared
```

### Paso 6 — Cloudflare Access (Zero Trust)

En el panel de Cloudflare > Zero Trust > Access > Applications:

1. Crear nueva aplicacion: Self-hosted
2. Application domain: `orbit.aurenix.cloud`
3. Crear politica: Allow — Email ends in `@aurenix.es` (o listar emails autorizados)
4. Authentication method: One-time PIN al email
5. Session duration: 8 horas

Con esto, ningun acceso llega a FastAPI sin pasar primero por Cloudflare Access.

### Paso 7 — Verificacion

```bash
# Health check
curl https://orbit.aurenix.cloud/health

# Ver logs
sudo journalctl -u orbit -f
```

### Paso 8 — Instalar agente en VPS AURENIX (primer cliente)

```bash
# Desde el VPS de AURENIX, instalamos el agente apuntando a si mismo
# para monitorizar los propios sistemas de AURENIX (investment-copilot, etc.)

bash scripts/install_agent.sh \
  --client-id <UUID_AURENIX_CLIENT> \
  --agent-token <TOKEN_GENERADO_EN_ORBIT> \
  --orbit-url https://orbit.aurenix.cloud
```

### Instalacion del agente en VPS de un cliente nuevo

```bash
# Ejecutar desde el VPS del cliente tras configurar el cliente en Orbit
scp scripts/install_agent.sh ubuntu@<IP_CLIENTE>:/tmp/
ssh ubuntu@<IP_CLIENTE>
bash /tmp/install_agent.sh \
  --client-id <UUID_CLIENTE> \
  --agent-token <TOKEN_CLIENTE> \
  --orbit-url https://orbit.aurenix.cloud
```

El script detecta automaticamente si hay Python 3.8+ disponible e instala el
agente completo, o cae al agente bash minimo si no lo hay.

### Puertos en uso (referencia)

| Puerto | Servicio |
|--------|---------|
| 8001 | Resona |
| 8002 | Overture |
| 8003 | Orbit (este proyecto) |
| 5678 | n8n |
| 5432 | PostgreSQL (solo localhost) |

---

## 10. Metricas Clave

| Metrica | Formula | Objetivo Inicial |
|---------|---------|-----------------|
| Disponibilidad global | sistemas operativos / total sistemas × 100 | > 99% |
| MTTR (tiempo medio resolucion) | suma(resolved_at - created_at) / alertas_resueltas | < 30 min |
| Cobertura de monitorizado | sistemas con heartbeat activo / total sistemas | 100% |
| Margen medio por cliente | media(margin_pct) de todos los clientes activos | > 65% |
| Alertas criticas sin resolver > 1h | COUNT WHERE severity=critica AND status=open AND age > 1h | 0 |
| Tasa de falsos positivos | alertas_silenciadas / alertas_totales × 100 | < 10% |
| Carga media del agente | media(cpu_pct) en heartbeats de las 24h | < 20% |
| Coste Claude por cliente / MRR | claude_cost_eur / mrr_eur × 100 | < 15% |
