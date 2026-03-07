# AURENIX — Memoria Permanente del IT Agent Senior

> Este archivo es la fuente de verdad operativa para cualquier sesión de trabajo en este directorio.
> Leerlo completo antes de ejecutar cualquier acción. No hacer suposiciones que contradigan este documento.

---

## 1. ¿Qué es AURENIX?

**AURENIX** es una agencia de Inteligencia Artificial B2B en fase de crecimiento activo. No es una consultora tradicional: es una **plataforma de orquestación de agentes autónomos**. Vendemos sistemas, no horas.

- **Dominio:** aurenix.cloud
- **Equipo:** José (jose@aurenix.cloud) + Sebas (sebas@aurenix.cloud)
- **Filosofía central:** *"Primero interno, luego externo."* Dominamos nuestra propia infraestructura antes de venderla. Somos el primer cliente de cada sistema que construimos.

### Modelo de Negocio
- **Setup Fee** alto por implementación (proyecto llave en mano)
- **Retainer mensual** (MRR) por hosting gestionado, monitoreo y mejora continua
- El cliente nunca gestiona su propia infraestructura. La gestiona AURENIX.
- Target: PYMEs y empresas (agnóstico de sector)

### Mentalidad de Trabajo
- Hablar de tú a tú. Pensar siempre en ROI y escalabilidad.
- Código de nivel producción en cada entregable: error handling, seguridad, logging.
- Ser extremadamente crítico con la deuda técnica. Si algo es basura, decirlo y archivarlo.
- No pedir permiso para explorar archivos o analizar el entorno. Ejecutar primero, informar después.

---

## 2. Infraestructura VPS (Confirmada Marzo 2026)

| Parámetro | Valor |
|---|---|
| **Proveedor** | Hostinger |
| **IP** | `76.13.9.238` |
| **Hostname** | `srv1285851` |
| **OS** | Ubuntu 24.04 LTS, kernel 6.8.0 |
| **Uptime** | Estable, último reinicio Feb 26 2026 |
| **Gestor de apps** | Coolify v4 (Docker-based) en `:8000` |
| **SSH root** | Clave `jose_root_ed25519` en `_INFRA/Claves_contraseñas/` |
| **SSH alias** | `ssh vps-aurenix` (configurado en `~/.ssh/config`) |
| **SSH agente** | `ssh vps-agent` (usuario `aurenix_it_agent`, sin acceso Docker) |

### URLs de Servicios en Producción
| Servicio | URL | Credenciales |
|---|---|---|
| **n8n** | `https://n8n.aurenix.cloud` | UI + API Key en `.env.local` |
| **Filebrowser** | `https://files.aurenix.cloud` | `admin / Aurenix2026!` |
| **Qdrant** | `https://qdrant.aurenix.cloud` | API Key en `.env.local` |
| **Vaultwarden** | `https://pass.aurenix.cloud` | Pendiente configurar |
| **Coolify** | `http://76.13.9.238:8000` | Panel de gestión de contenedores |

### Stack Docker Activo (todos healthy)
| Contenedor | Servicio | Estado |
|---|---|---|
| `n8n-*` | n8n v2.1.5 | Up 7 días |
| `postgresql-*` | PostgreSQL (DB de n8n) | Up 7 días |
| `qdrant-*` | Qdrant (Vector Store) | Up 7 días — **YA DESPLEGADO** |
| `filebrowser-*` | Filebrowser (Drive) | Up 7 días |
| `vaultwarden-*` | Vaultwarden (Password Manager) | Up 7 días |
| `task-runners-*` | n8n Task Runners | Up 7 días |
| `coolify` + `coolify-proxy` | Coolify + Traefik | Up 7 días |
| `coolify-redis` | Redis (interno Coolify) | Up 7 días |
| `coolify-db` | PostgreSQL (interno Coolify) | Up 7 días |
| `coolify-realtime` | WebSockets `:6001-6002` | Up 7 días |

### Recursos del Servidor
- **RAM:** 1.9G / 7.8G usada (24%) — Excelente
- **Disco:** 18G / 96G usados (19%) — Excelente
- **Swap:** 8GB configurado, 0 usado
- **Fail2ban:** Activo en SSH (785 IPs baneadas históricamente)

### Git Repos en VPS (backup)
Repos bare en `/data/git-repos/`: `aurenix.git`, `aurenix-infra.git`, `aurenix-monorepo.git`, `aurenix-knowledge.git`

### Credenciales
Todas en `.env.local` (raíz). **Nunca commitear.**
SSH config en `~/.ssh/config` — aliases `vps-aurenix` y `vps-agent` operativos.

### Canales de Comunicación Operativa
- **Telegram:** Alertas, HITL. ID José: `501092522`. Bot Token en `.env.local`.
- **SMTP:** `smtp.hostinger.com:465 SSL` | IMAP: `imap.hostinger.com:993 SSL`

---

## 3. Stack Tecnológico

### Core Actual (Producción — Confirmado Marzo 2026)
| Capa | Tecnología | Rol |
|---|---|---|
| **Orquestación** | n8n v2.1.5 self-hosted | Motor de automatización — 42 workflows |
| **Base de Datos** | PostgreSQL (en VPS via Coolify) | DB principal de n8n |
| **Vector Store** | Qdrant (en VPS, `qdrant.aurenix.cloud`) | RAG corporativo — **ACTIVO** |
| **Frontend** | Next.js 15 (App Router) | Dashboard FENIX (en desarrollo) |
| **Monorepo** | pnpm + Turbo | Gestión de paquetes y builds |
| **LLM (velocidad)** | Groq / Llama-3-70b | Agentes, filtrado, clasificación (bajo coste) |
| **LLM (calidad)** | Claude Sonnet 4.5 | Agentes complejos, redacción, análisis |
| **LLM (backup)** | GPT-4o-mini | Tareas complementarias |
| **Contenedores** | Docker + Coolify v4 | Despliegue y gestión en VPS |
| **Git** | GitHub (`AURENIX-ADMIN`) + VPS bare repos | Control de versiones |
| **Drive** | Filebrowser (`files.aurenix.cloud`) | Archivos corporativos |
| **Secretos** | Vaultwarden (`pass.aurenix.cloud`) | Password manager agencia |
| **MCP** | `.mcp.json` en raíz | n8n, Postgres, Filesystem, Fetch, GitHub |
| **Alertas/HITL** | Telegram Bot | Canal operativo principal |

### MCPs Configurados (`.mcp.json`)
| MCP | Estado | Para qué |
|---|---|---|
| `aurenix-n8n` | Configurado | Crear/editar/ejecutar workflows |
| `aurenix-postgres` | Configurado | Consultar DB de n8n en producción |
| `aurenix-filesystem` | Configurado | Leer/escribir archivos locales AURENIX |
| `aurenix-fetch` | Configurado | Peticiones HTTP a cualquier API |
| `aurenix-github` | Pendiente PAT | Repos, PRs, issues, commits |

### GitHub (AURENIX-ADMIN)
- **Cuenta:** `AURENIX-ADMIN` en github.com
- **Repos existentes:** `AURENIX` (web/landing), `Nexo-periodico-financiero`, `WEB-APP`
- **SSH Key para GitHub:** `_INFRA/Claves_contraseñas/github_aurenix_ed25519` — **PENDIENTE añadir en github.com/settings/keys**
- **PAT:** Pendiente generar en `github.com/settings/tokens` (scopes: `repo`, `workflow`, `read:org`)

### Stack de Visión (Roadmap)
- **Temporal.io** — Orquestación duradera de agentes de larga ejecución (Plan FENIX)
- **LangGraph** — Grafos de razonamiento para agentes complejos (Plan FENIX)
- **Recall.ai** — Captura de reuniones multi-plataforma (Plan NEXUS)
- **Google ADK / Vertex AI** — Despliegue Enterprise de agentes (Plan 2026)

---

## 4. Estructura del Proyecto

```
C:\Users\Usuario\Desktop\AURENIX\
│
├── CLAUDE.md                          <- Este archivo (memoria permanente)
├── handover_sesion_marzo.md           <- Estado de sesión anterior + pendientes
├── prompt_experto_agencia.md          <- System prompt de arranque rápido
├── .env.local                         <- Credenciales (NO commitear)
│
├── _KNOWLEDGE_BASE/                   <- GROUND TRUTH — Leer antes de actuar
│   ├── AURENIX_Master_Architecture_Report.md   <- Biblia operativa (Core 12, patrones)
│   ├── AURENIX_MANIFIESTO.md                   <- Constitución estratégica
│   ├── AURENIX_REFERENCE_ARCHITECTURE.md       <- Arquitectura FENIX/NEXUS/VANTAGE
│   ├── plan_maestro_2026.md                    <- Plan y benchmarking 2026
│   ├── S5_Oracle_Architecture.md               <- Diseño detallado de S5
│   ├── Guia_Claude_Code_MCP_Colaborativo.md
│   ├── Guia_Sync_Filebrowser.md
│   ├── N8N-Cursor-Pro/                <- MCP tools, n8n-skills, AURENIX_CONTEXT.md
│   └── code_snippets/                 <- Estándares de seguridad y patrones SSH
│
├── _INFRA/                            <- Infraestructura operacional
│   ├── Flujo_Agente_IT_n8n_v4.json   <- Agente IT (versión activa)
│   ├── Flujo_S1_VPS_Guard.json        <- S1: Monitor VPS
│   ├── Flujo_S2_Workflow_Sentinel.json <- S2: QA errores n8n
│   ├── Flujo_S3_System_Factory.json   <- S3: Auto-builder
│   ├── Flujo_S5_The_Oracle.json       <- S5: Intel diaria IA
│   ├── Flujo_S6_Onboarding_Autonomo.json
│   ├── Flujo_S7_Intelligent_Billing.json
│   ├── Flujo_S8_Lead_Scoring.json
│   ├── Flujo_S9_Retention_Oracle.json
│   ├── Flujo_S10_Autonomous_DevOps.json
│   ├── Flujo_S11_Inbox_Zero_Triage.json
│   ├── Flujo_S12_Master_CRM_Sync.json
│   ├── INFRAESTRUCTURA/n8n/
│   ├── scripts/                       <- audit, backup, debug, deploy, docker, ssh, utils
│   └── Backups/
│
├── _PROJECTS/                         <- Proyectos internos activos
│   ├── AURENIX AGENCY/                <- Monorepo de la agencia (_PROJECTS version)
│   ├── LIBERTAD FINANCIERA/           <- App finanzas (Python/FastAPI + Tauri + Rust)
│   └── WEB/                           <- Web pública de la agencia
│
├── _CLIENTS/                          <- Proyectos de clientes
│   └── PLANTASUR B2C/                 <- Cliente activo (ver sección 6)
│
├── _ARCHIVE/                          <- Histórico (ZIPs, PDFs, videos)
│
├── AURENIX AGENCY/                    <- Monorepo Next.js (versión más reciente)
│   └── aurenix-monorepo/
│       ├── apps/: api-gateway, dashboard, temporal-worker, web-portal
│       └── packages/: billing, core-engine, data-layer, integrations, security
│
├── PLANTASUR B2C/                     <- Stack cliente (WordPress + Flowise + pg_data)
└── N8N-Cursor-Pro/                    <- MCP activo (n8n-mcp + n8n-skills)
```

---

## 5. Sistemas Core (Core 12)

| Sistema | JSON | Descripción | Estado |
|---|---|---|---|
| **S1: VPS Guard** | `Flujo_S1_VPS_Guard.json` | Monitor RAM/Disco/Docker cada 30min. HITL: requiere `/approve <cmd>` en Telegram para ejecutar. | Implementado |
| **S2: Workflow Sentinel** | `Flujo_S2_Workflow_Sentinel.json` | Recolector global de errores n8n. IA traduce el error a lenguaje humano + alerta Telegram. | Implementado |
| **S3: System Factory** | `Flujo_S3_System_Factory.json` | Recibe `/create <descripcion>` en Telegram, IA diseña el workflow JSON y lo crea via API n8n. | Implementado |
| **S4: Fenix Dashboard** | Monorepo Next.js | Control Plane web: semáforos de S1/S2, `/api/health`. Email Triage y Calendar pendientes. | Parcial |
| **S5: The Oracle** | `Flujo_S5_The_Oracle.json` | Intel diaria: RSS → Groq (filtro) → Jina Reader → LLM (análisis) → Telegram + Qdrant. | JSON pendiente |
| **S6: Onboarding Autónomo** | `Flujo_S6_Onboarding_Autonomo.json` | Creación Drive, briefing LLM, config CRM. Ciclo días→15min. | JSON generado |
| **S7: Intelligent Billing** | `Flujo_S7_Intelligent_Billing.json` | Stripe ↔ QuickBooks/Xero. Facturas PDF, conciliación contable. | JSON generado |
| **S8: Lead Scoring** | `Flujo_S8_Lead_Scoring.json` | Apollo.io + LinkedIn → LLM scoring 50 variables → cold emails personalizados. | JSON generado |
| **S9: Retention Oracle** | `Flujo_S9_Retention_Oracle.json` | Telemetría + sentimiento Zendesk → detección churn → descuentos Stripe autónomos. | JSON generado |
| **S10: Autonomous DevOps** | `Flujo_S10_Autonomous_DevOps.json` | PR en GitHub → LLM analiza diff → comenta vulnerabilidades inline. | JSON generado |
| **S11: Inbox Zero Triage** | `Flujo_S11_Inbox_Zero_Triage.json` | Triage semántico email → Markdown → Vision para pantallazos → RAG → borradores. | JSON generado |
| **S12: Master CRM Sync** | `Flujo_S12_Master_CRM_Sync.json` | Bus asíncrono: HubSpot + Salesforce + DBs propias. Upsert + deduplicación semántica. | JSON generado |

> **S6-S12**: Los JSONs están en `_INFRA/`. Pendiente de importar en el panel n8n, asignar credenciales y probar.

---

## 6. Arquitectura Técnica (Patrones Mandatorios)

### 6.1 Patrón de 4 Capas en n8n (NO negociable)
Todo microservicio debe respetar estas 4 capas aisladas:

1. **Capa de Ingesta (Asíncrona):** El webhook NUNCA procesa. Solo recibe el payload, hace `LPUSH` a Redis y devuelve `200 OK` en < 50ms. Sin excepciones.
2. **Capa Lógica/Cognitiva (Agentic):** Un Cron/Worker hace `RPOP` de Redis. Aquí operan los LLMs (Chained Requests, Stateful Agents). Sub-procesos genéricos van en sub-workflows (`Execute Workflow`).
3. **Capa de Acción (Batching):** Llamadas a APIs externas (CRM, Stripe) en lotes de 50-150 registros. NUNCA inserción 1 a 1 síncrona.
4. **Capa de Fallback (Global Error):** Todo nodo crítico (HTTP, Switch) tiene error routing activado. Si falla → subflujo global → log en Sentinel → Dead Letter Queue → alerta Telegram/Slack.

### 6.2 Patrón BFF (Next.js ↔ n8n)
- El cliente React NUNCA llama directamente a webhooks de n8n.
- Flujo: `Cliente React → Route Handler Next.js (/api/server/...) → proxy autenticado a n8n`
- El BFF inyecta secrets (Bearer Tokens), aplica Rate Limiting y valida con Zod. Elimina CORS y claves expuestas.
- **Respuestas largas de IA:** Server-Sent Events (SSE) / `ReadableStream` — nunca long-polling.
- **Estado async:** `Cliente → BFF → n8n encola → n8n actualiza Supabase → Supabase Realtime → Next.js WebSocket`

### 6.3 Multi-Tenancy y Seguridad de Datos
- **Row Level Security (RLS)** en todas las tablas de Supabase. Política: `tenant_id = auth.uid()`.
- Nunca compartir esquemas entre clientes. El aislamiento es matemático, a nivel de BD.
- PII (datos personales) debe redactarse antes de enviar a LLMs públicos.

### 6.4 Arquitectura FENIX (Visión Técnica)
- **"Cerebro":** LangGraph — grafos de razonamiento, sub-agentes especializados, HITL breakpoints.
- **"Cuerpo":** Temporal.io — ejecución duradera, reintentos con backoff, señales para eventos externos.
- **Integración:** El grafo LangGraph se ejecuta dentro de actividades de Temporal. Estado del grafo persistido en Postgres.
- **Kill Switch:** API `client.terminate_workflow` de Temporal. Budget Guard: límite duro por tarea ($5 o 50 pasos).

---

## 7. Estándares de Seguridad (Mandatory en Todo Agente con Ejecución)

### Zero Trust Filter
El primer nodo tras cualquier Trigger valida el ID numérico del remitente. NUNCA validar por nombre de usuario.
```javascript
// Telegram: verificar ID numérico, no username
{{ $json.message.from.id }} === 501092522  // ID de José
```

### JS Validator (Escudo antes de cualquier ejecución SSH/Bash)
El output del LLM NUNCA va directo al ejecutor. Siempre pasa por un nodo `Code` con lista blanca/negra:
```javascript
const allowedPrefixes = ['docker ps', 'free', 'uptime', 'ls', 'df', 'python scripts/'];
const blockedKeywords = ['rm ', 'dd ', 'mkfs', '> ', 'shutdown', 'chmod 777', 'DROP ', 'DELETE '];
// Si blocked o no en allowedPrefixes: retornar { safe: false } y alertar por separado.
```

### Guardrails del LLM
System prompt siempre con: rol explícito, restricciones de comandos, formato de salida JSON obligatorio.

### HITL (Human-in-the-Loop)
Ninguna acción destructiva o de escritura se ejecuta sin señal explícita (`/approve <cmd>`).
El workflow entra en estado suspendido esperando la señal. No consume CPU mientras espera.

---

## 8. Reglas de Desarrollo

### n8n
- Minimizar nodos de IA. Usar solo cuando la lógica no sea determinista.
- JavaScript/Python para lógica determinista. No usar IA donde basta con código.
- Retry logic en todas las operaciones críticas (HTTP, SSH, DB writes).
- Nunca hardcodear credenciales en nodos. Usar las Credentials de n8n o variables de entorno.
- Todo flujo nuevo debe pasar por el patrón de 4 capas antes de ir a producción.
- Activar error routing en TODOS los nodos críticos.

### Código General
- Nivel producción siempre: manejo de errores, logging, seguridad.
- Validar inputs en los límites del sistema (webhooks, inputs de usuario). Confiar en el código interno.
- No over-engineer. La solución mínima que funcione en producción es la correcta.
- No añadir comentarios obvios. Solo comentar lógica no evidente.
- No añadir features no solicitadas.

### Seguridad
- `.env.local` nunca se commitea. Nunca.
- Credenciales en Coolify Env Vars para el VPS, en `.env.local` para local.
- PII se redacta antes de enviar a APIs de terceros.
- RLS activado en todas las tablas de Supabase desde el inicio.

---

## 9. Clientes Activos

### PLANTASUR B2C
- **Sector:** Comercio B2C (plantas/jardín)
- **Stack:** WordPress + WooCommerce + Flowise (agente IA)
- **Ubicación local:** `PLANTASUR B2C/` (raíz) y `_CLIENTS/PLANTASUR B2C/`
- **Datos:** `pg_data/` (PostgreSQL local para desarrollo), `Uploads/`, `wordpress_data/`
- **Estado:** Activo. Tiene presentación de cliente en `presentacion_cliente_plantasur/`.

---

## 10. Proyectos Internos Activos

### FENIX Dashboard (S4) — Monorepo Next.js
- **Ruta:** `AURENIX AGENCY/aurenix-monorepo/`
- **Stack:** Next.js 15, pnpm, Turbo
- **Apps:** `api-gateway`, `dashboard`, `temporal-worker`, `web-portal`
- **Packages:** `billing`, `core-engine`, `data-layer`, `integrations`, `security`
- **Estado:** Build con errores previos (`build_error.txt`). Control Plane básico implementado.
- **AVISO:** Existe un segundo monorepo en `_PROJECTS/AURENIX AGENCY/`. Consolidar antes de desarrollar.

### LIBERTAD FINANCIERA
- **Ruta:** `_CLIENTS/LIBERTAD FINANCIERA/`
- **Stack:** Python/FastAPI + Tauri (Rust) + DuckDB + Flowise + Prometheus
- **Descripción:** App de finanzas personales/estrategia. Proyecto grande e independiente.
- **Estado:** Tiene scripts de verificación y tests. Tratar como proyecto separado.

---

## 11. Pendientes Críticos

> Ordenados por prioridad según `handover_sesion_marzo.md`

- [ ] **Auditoría quirúrgica del directorio:** Separar proyectos, archivar basura digital, consolidar los dos monorepos.
- [ ] **S5 The Oracle:** Construir el JSON del flujo n8n completo (RSS→Groq→Jina→Qdrant/Telegram).
- [ ] **S6-S12:** Importar JSONs en n8n, asignar credenciales, probar en staging.
- [ ] **S4 Fenix:** Resolver errores de build del monorepo. Implementar Email Triage y Calendar Sync.
- [ ] **Qdrant:** Configurar vía Docker Compose en Coolify (o confirmar uso de Supabase pgvector).
- [ ] **Jina Reader API Key:** Obtener para el pipeline de S5.

---

## 12. Contexto Rápido para Arranque de Sesión

1. Leer `handover_sesion_marzo.md` — estado de la última sesión y pendientes inmediatos.
2. Este archivo — arquitectura, reglas y contexto completo.
3. `_KNOWLEDGE_BASE/AURENIX_Master_Architecture_Report.md` — si la tarea es sobre patrones n8n o Core 12.
4. `_KNOWLEDGE_BASE/AURENIX_REFERENCE_ARCHITECTURE.md` — si la tarea es sobre FENIX/NEXUS/VANTAGE.

---

*Última actualización: Marzo 2026 — Generado por IT Agent Senior tras auditoría completa del directorio.*
