# ORBIT — Arquitectura y Estado (Importado 2026-03-10)

> Fuente: `_PROJECTS/ORBIT/PLAN-MAESTRO.md` (38KB)
> Autor: Sebas. Repo origen: github.com/AURENIX-ADMIN/SIACompleto (carpeta `business-ideas/orbit/`)

---

## ¿Qué es Orbit?

**Orbit = Centro de Control Operacional de AURENIX.** Dashboard interno FastAPI (Python) que:

- Monitoriza todos los sistemas de clientes via **protocolo de heartbeat HMAC-SHA256** (agentes en VPS cliente)
- Trackea MRR, costos (Claude tokens por cliente, VPS) y márgenes en tiempo real
- Dashboard web: Jinja2 + HTMX + Alpine.js + Tailwind CSS
- Gestiona alertas con escalado automático (crítica/alta/media/baja)
- Pipeline de onboarding de nuevos clientes con checklists por fases
- Integra con n8n API para ver workflows por cliente
- **5 capas de seguridad**: Cloudflare Access + Tunnel + JWT + HMAC + PostgreSQL local

---

## Stack Técnico

| Componente | Tecnología |
|---|---|
| Runtime | Python 3.11 |
| API Framework | FastAPI |
| ORM | SQLAlchemy 2.0 + Alembic (migraciones) |
| Base de Datos | PostgreSQL (schema `orbit`, usuario `orbit_user`) |
| Templates | Jinja2 (SSR, sin SPA) |
| Interactividad | HTMX (partial updates) + Alpine.js (microinteracciones) |
| Estilos | Tailwind CSS (CDN) + Chart.js |
| Auth | bcrypt (cost 12) + JWT RS256 (expira 8h) + rate limit (slowapi) |
| HTTP client | httpx (pull async de métricas) |
| Notificaciones | Telegram (bot existente AURENIX) |
| Deploy | systemd service + Cloudflare Tunnel (puerto 8003) |

---

## Arquitectura de Seguridad (5 capas)

```
Capa 1 — Cloudflare Access (Zero Trust)
  Solo correos @aurenix.es + OTP. Bloquea antes de llegar al servidor.

Capa 2 — Cloudflare Tunnel
  Puerto 8003 no expuesto en firewall. IP del servidor invisible.

Capa 3 — FastAPI + JWT
  bcrypt (factor 12) + JWT firmado RS256. Rate limit: 10 logins/IP/5min.

Capa 4 — HMAC en heartbeats de agente
  Cada cliente = AGENT_TOKEN único (32 bytes). Anti-replay: timestamp ±5min.

Capa 5 — PostgreSQL local
  orbit_user con permisos mínimos. Solo accesible desde localhost.
```

---

## Protocolo de Heartbeat (Agente → Orbit)

```
POST https://orbit.aurenix.cloud/heartbeat
Headers: X-Client-ID, X-Timestamp, X-Signature (HMAC-SHA256)
Body: { status, services: {fastapi, n8n, postgresql, telegram_bot}, system: {cpu, ram, disk} }
Frecuencia: cada 5 minutos
```

---

## Modelo de Datos (9 tablas PostgreSQL)

| Tabla | Descripción |
|---|---|
| `users` | Equipo AURENIX (UUID, email, bcrypt hash) |
| `clients` | Clientes con MRR, VPS cost, margen |
| `systems` | Sistemas por cliente (tipo: resona, nexo, ocr_facturas, custom) |
| `agent_tokens` | SHA-256 de tokens por cliente (nunca en claro) |
| `heartbeats` | Time series: CPU/RAM/disk/servicios por sistema |
| `system_metrics` | Time series: tokens Claude, n8n executions, métricas custom |
| `alerts` | Incidentes con severity/status/deduplicación |
| `cost_records` | Costes mensuales por sistema (claude + vps) + margen |
| `onboarding_checklists` | Pipeline por fases por cliente |

---

## Estructura del Código (`_PROJECTS/ORBIT/`)

```
main.py                   # CLI: serve | setup | add-token
requirements.txt
config/settings.py        # Pydantic BaseSettings
src/
  api/routes/             # auth, clients, systems, heartbeat, metrics, alerts, onboarding
  models/                 # 9 tablas SQLAlchemy
  schemas/                # Pydantic validators
  services/               # auth, hmac, health_puller, alert, cost_tracker, n8n_client
  agent/                  # orbit_agent.py (Python) + orbit_heartbeat.sh (bash fallback)
  notifications/          # telegram_notifier.py
templates/                # Jinja2: home, client_detail, system_detail, alerts, costs, onboarding
static/                   # orbit.css, orbit.js (Chart.js)
n8n/workflows/            # health_monitor.json, cost_alert.json
scripts/                  # setup_vps.sh, setup_db.py, deploy.sh, install_agent.sh
```

---

## Plan de Fases (Estado del Código)

| Fase | Objetivo | Estado |
|---|---|---|
| **Fase 1** | Core: Auth + CRUD clientes/sistemas + heartbeat + alertas | **Código presente** |
| **Fase 2** | Métricas + costes + n8n integration | Checklist pendiente |
| **Fase 3** | Onboarding + UX premium | Checklist pendiente |
| **Fase 4** | Automatización avanzada + backup | Checklist pendiente |

---

## Puerto de Despliegue

- Orbit: `:8003` (via Cloudflare Tunnel → `orbit.aurenix.cloud`)
- Puertos ocupados en VPS: 8001 (Resona), 8002 (Overture), 5678 (n8n), 5432 (PostgreSQL)

---

## Debate de Integración Orbit vs FENIX Dashboard

### La tensión real

| Sistema | Stack | Orientación |
|---|---|---|
| **Orbit** (Sebas) | FastAPI + Python, SSR Jinja2/HTMX | Operaciones internas, monitoreo clientes |
| **FENIX Dashboard** (Jose) | Next.js 15 + TypeScript + React | Control plane agencia, APIs REST |

Ambos son el "control panel" de la agencia. **Solapamiento real.**

### Opciones

**Opción A — Orbit = Backend + FENIX = Frontend** *(Recomendada corto plazo)*
- Orbit gestiona lógica: heartbeats, costos, alertas. FENIX consume via BFF.
- Pros: No reescribir lógica sólida. Separación clara.
- Contras: Dos stacks, dos deploys. Coordinación técnica entre socios.

**Opción B — FENIX absorbe Orbit** *(Evaluar en 2-3 meses)*
- Reescribir core de Orbit en TypeScript dentro del monorepo FENIX.
- Pros: Un stack, un deploy, coherencia.
- Contras: Trabajo de reescritura. Sebas pierde "su" proyecto.

**Opción C — Coexistencia con integración puntual** *(No recomendada)*
- FENIX solo consume `/api/costs/summary` de Orbit para KPIs.
- Pros: Mínimo esfuerzo.
- Contras: Dos dashboards, experiencia fragmentada.

**Decisión pendiente:** Debatir con ambos socios con código en mano.

---

## Métricas Clave de Orbit

| Métrica | Objetivo |
|---|---|
| Disponibilidad global | > 99% |
| MTTR (tiempo medio resolución) | < 30 min |
| Margen medio por cliente | > 65% |
| Alertas críticas sin resolver >1h | 0 |
| Coste Claude / MRR por cliente | < 15% |

---

*Importado: 2026-03-10 | Leer PLAN-MAESTRO.md completo para setup de deploy.*
