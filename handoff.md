# AURENIX — Handoff de Sesión
**Fecha:** 6 de Marzo 2026
**Duración:** Sesión de fundación del stack completo
**Autor:** IT Agent Senior (Claude Sonnet 4.6)
**Próximo agente:** Lee este documento completo antes de ejecutar cualquier acción.

---

## 1. ESTADO ACTUAL — Qué hay hecho y operativo

### Infraestructura VPS
- **VPS en producción:** `76.13.9.238` (Hostinger, Ubuntu 24.04, 7.8GB RAM, 96GB disco)
- **Coolify v4** gestionando todos los contenedores Docker
- **SSH resuelto definitivamente:**
  - Clave `jose_root_ed25519` (Ed25519) añadida a `authorized_keys` de root
  - Alias `ssh vps-aurenix` → root@76.13.9.238 operativo
  - Alias `ssh vps-agent` → aurenix_it_agent@76.13.9.238 operativo
  - Configuración en `~/.ssh/config`
  - **CRÍTICO:** Las claves físicas están en `_INFRA/Claves_contraseñas/` (ruta con ñ). Para usarlas desde Python, usar `paramiko.Ed25519Key.from_private_key(io.StringIO(key_content))` pasando el contenido como string, no la ruta.

### Stack Docker (todos healthy, up 7+ días)
| Servicio | URL | Credenciales |
|---|---|---|
| n8n v2.1.5 | https://n8n.aurenix.cloud | API Key en `.env.local` |
| Filebrowser | https://files.aurenix.cloud | admin / Aurenix2026! |
| Qdrant | https://qdrant.aurenix.cloud | API Key en `.env.local` |
| Vaultwarden | https://pass.aurenix.cloud | Sin configurar |
| Coolify | http://76.13.9.238:8000 | Acceder vía web |
| PostgreSQL | 76.13.9.238:5432 | Credenciales en `.env.local` |

### n8n — Estado de Workflows
- **42 workflows totales** en la instancia
- **S1, S2, S3 ACTIVADOS** con credenciales enlazadas:
  - S1: VPS Guard — cron cada 30 min, SSH + Groq + Telegram IT_Ops
  - S2: Workflow Sentinel — error trigger, Groq + Telegram IT_Ops
  - S3: System Factory — Telegram trigger, Groq + n8n API
- **S5-S12 INACTIVOS** — credenciales básicas enlazadas en S5, resto pendiente
- **Credenciales creadas en n8n:**
  - `3xX3Du0zMIty4shQ` — Groq account (existía)
  - `8Rr85DDzQK1f3223` — SSH Password account (existía)
  - `j286Y4Q9S28CG36j` — IT_Ops Telegram (existía — ESTE es el bot de sistemas internos)
  - `vsYNaJiibv4SCx1E` — Qdrant AURENIX (creada hoy, enlazada a S5)
  - `QvOqobsyEgZ25FT3` — n8n API AURENIX (creada hoy, enlazada a S3)

### GitHub — Configurado
- **Cuenta:** `AURENIX-ADMIN` (github.com/AURENIX-ADMIN)
- **Token PAT:** en `.env.local` y `.mcp.json` — verificado, accede a 8 repos
- **SSH Key:** `github_aurenix_ed25519` añadida a GitHub (hecho por el usuario)
- **Repos privados descubiertos:** `aurenix-platform` (vacío), `DESARROLLO-AURENIX`, `MIGRACION-COMPLETA`, `SIACompleto`, `Workspaces`
- **Repo relevante para el trabajo actual:** `DESARROLLO-AURENIX` (tiene Newsletter Bot, último commit Oct 2025)

### Archivos creados/actualizados hoy
| Archivo | Descripción |
|---|---|
| `CLAUDE.md` | Memoria permanente — arquitectura completa del stack real |
| `.mcp.json` | 5 MCPs configurados: n8n, postgres, filesystem, fetch, github |
| `.env.local` | Todas las credenciales consolidadas y actualizadas |
| `.gitignore` | Protección completa — secretos, node_modules, datos Docker |
| `~/.ssh/config` | Aliases vps-aurenix y vps-agent operativos |
| `.git/hooks/pre-commit` | Hook de seguridad — bloquea commits con credenciales |
| `handover_sesion_marzo.md` | Estado previo (de sesiones anteriores) |
| `_INFRA/Claves_contraseñas/jose_root_ed25519` | Nueva clave SSH root de José |
| `_INFRA/Claves_contraseñas/github_aurenix_ed25519` | Clave SSH para GitHub |

---

## 2. EN PROGRESO — Estado actual y lo que falta

### BUG CRÍTICO RESUELTO (6 Marzo 2026 — Sesión 2)
**Root cause encontrado y corregido:** n8n v2.1.5 tiene un bug donde el nodo `if v1.1` con la sintaxis antigua de conditions (`{string: [...], number: [...]}`) causa `Cannot read properties of undefined (reading 'execute')` durante la activación de cualquier workflow que lo contenga. El fix fue:
1. Actualizar todos los nodos `if v1.1` a `if v2` con la nueva sintaxis de conditions
2. Actualizar `telegramTrigger v1.1` → `v1.2` en S1 y S3
3. Insertar entradas en `workflow_publish_history` con `activeVersionId` correcto en `workflow_entity`
4. S1/S2/S3 ahora se activan correctamente en cada restart de n8n

**Estado post-fix:**
- S1: ACTIVO | triggers=[Schedule 30min v1.2, TelegramTrigger HITL v1.2] | 10 conn-sources
- S2: ACTIVO | triggers=[ErrorTrigger v1] | 5 conn-sources
- S3: ACTIVO | triggers=[TelegramTrigger v1.2] | 7 conn-sources

### S1 VPS Guard — ACTIVO, SSH fix aplicado (sesión 3)
- **Primer cron disparó a las 16:00:51 UTC (6/3/2026) — status: ERROR**
  - Error: "All configured authentication methods failed" en nodo SSH (Get Health)
  - Root cause: Credencial `8Rr85DDzQK1f3223 SSH Password account` usaba user=`aurenix_it_agent` + password auth → ese user no tiene contraseña. Root no acepta SSH password (solo key).
  - **Fix aplicado sesión 3:** Nueva credencial `zwKkkBrd5NcbMFZ3` tipo `sshPrivateKey` con key Ed25519 (jose_root_ed25519) conectando como `root`. SSH nodes actualizados con nuevo credential ID y cwd `/root`.
- **Pendiente:** Confirmar que el cron de 16:30 UTC ejecuta exitosamente con la nueva credencial
- **S2 capturó el error de S1 a las 16:00:51** → S2 funcionó correctamente

### S2 Workflow Sentinel — ACTIVO y FUNCIONANDO
- **Estado:** Capturó el error de S1 a las 16:00:51 (execution 2495, status=success)
- **Configurado:** S1 y S3 tienen `settings.errorWorkflow = "piwQBZARypgDZxcz"` activo

### S3 System Factory — ACTIVO, pendiente test real
- **Estado:** TelegramTrigger activo. Escucha mensajes con `/create` del bot IT_Ops
- **Fix aplicado sesión 3:** URL corregida `http://localhost:5678` → `https://n8n.aurenix.cloud/api/v1/workflows`
- **Pendiente:** Enviar `/create <descripción>` al bot IT_Ops para verificar que crea workflows

### S5-S12 — En espera deliberada (decisión del usuario)
- Usuario ha indicado explícitamente que NO activar ningún sistema más por ahora
- S5 tiene todas las credenciales enlazadas — listo para activar cuando se decida
- S6-S12 necesitan credenciales de servicios externos que no están configurados todavía

### Dashboard Web (FENIX) — BUILD EXITOSO (sesión 3)
- **Monorepo activo:** `_PROJECTS/AURENIX AGENCY/aurenix-monorepo/apps/dashboard/`
  - El otro en `AURENIX AGENCY/aurenix-monorepo/` es un Python workspace más nuevo, sin frontend
- **Build:** Errores corregidos (4 rutas importaban `@aurenix/data-layer` y `date-fns` inexistentes)
  - Rutas stubadas con 501: `lead-hunter/trigger`, `metrics`, `vantage`, `vantage/process`
  - `@aurenix/billing` y `@aurenix/data-layer` eliminados del `package.json` (workspace:* no existían)
  - `pnpm install` y `next build` completados sin errores
- **`/api/health` ya existe** y acepta POST desde n8n para actualizar el estado de S1/S2
  - GET: devuelve `{s1_vps_guard: {status, lastCheck, message}, s2_workflow_sentinel: {...}}`
  - POST: acepta `{system: 's1'|'s2', status: 'operational'|'degraded'|'down', message}`
- **Stack del dashboard:** Next.js 14.1.0, Clerk auth (placeholder keys), Tailwind, Radix UI
- **Pendiente:** Desplegar dashboard en VPS (Coolify) o localhost, conectar S1 para POSTear a `/api/health` tras cada ejecución
- **Clerk:** Usa keys placeholder (`pk_test_placeholder`) — o quitar Clerk para uso interno o crear cuenta real

---

## 3. PRÓXIMO PROMPT PARA RETOMAR EL TRABAJO

Copia este prompt exactamente al inicio de la próxima sesión:

```
Actúa como IT Agent Senior de AURENIX. Lee primero CLAUDE.md (raíz del proyecto) y handoff.md completos — son tu memoria de lo hecho. No hagas suposiciones.

CONTEXTO RÁPIDO: Somos una agencia de IA B2B. Stack en VPS 76.13.9.238 con Coolify/Docker. n8n con 42 workflows. S1, S2, S3 activados hoy con credenciales enlazadas pero sin test de primera ejecución confirmada. GitHub conectado (AURENIX-ADMIN). MCPs configurados en .mcp.json.

TRABAJO DE HOY:
1. Verificar que S1 ejecutó correctamente su primer cron (30 min). Si hay error, diagnosticar la credencial SSH en n8n UI (Settings > Credentials > SSH Password account).
2. Test de S3: Enviar /create al bot Telegram IT_Ops y verificar que responde.
3. Revisar si S2 Sentinel ha spameado por el NEXO Manager de Sebas. Si es así, decidir cómo filtrar.
4. Una vez S1-S3 verificados, empezar el dashboard FENIX: revisar el monorepo Next.js en "AURENIX AGENCY/aurenix-monorepo/", corregir errores de build y conectar /api/health con los estados de S1/S2.

Antes de empezar, ejecuta: ssh vps-aurenix 'docker ps --format "{{.Names}}: {{.Status}}"' para verificar estado del servidor.
```

---

## 4. DECISIONES TOMADAS HOY — No recogidas aún en CLAUDE.md

Las siguientes decisiones estratégicas se tomaron en esta sesión y deben incorporarse al CLAUDE.md en la próxima sesión:

1. **GitHub como fuente de verdad del código** — No los repos bare del VPS. Los repos bare en `/data/git-repos/` son backup secundario. GitHub es la fuente primaria.

2. **Repos privados de AURENIX-ADMIN que existen y no se sabían:**
   - `aurenix-platform` — Vacío, es el candidato para el monorepo principal
   - `DESARROLLO-AURENIX` — Newsletter Bot, Oct 2025
   - `MIGRACION-COMPLETA` — Contenido desconocido, revisar
   - `SIACompleto` — Contenido desconocido, revisar (podría ser el SIA/FENIX dashboard)
   - `Workspaces` — Contenido desconocido, revisar

3. **Telegram: el bot IT_Ops (j286Y4Q9S28CG36j) es el bot de sistemas internos** — El token es `8708909377:AAEWNlThfUc3HM6M0jkJ5xZ_PF6yHM-0QIc`. Las alertas de S1/S2/S3 irán al ID de José `501092522`. PENDIENTE añadir ID de Sebas cuando lo proporcione.

4. **Servicios externos (S6-S12) — Política decidida:** Se registrarán en todos los servicios necesarios (Stripe, Apollo.io, HubSpot, Zendesk, etc.) según se vayan necesitando. No hay cuentas activas actualmente excepto Google (tiene Google Sheets OAuth2 configurada en n8n).

5. **S5 Oracle — NO activar todavía.** El usuario quiere verificar los sistemas base (S1-S3) antes de activar el de inteligencia continua.

6. **NEXO Manager (Sebas) — No tocar.** Está fallando cada 5 min, es responsabilidad de Sebas arreglarlo. Afecta a S2 (Sentinel) que lo capturará como error masivo.

7. **Activación de workflows via DB + reinicio** — La API pública de n8n v2.1.5 no soporta PATCH para activar workflows. El método es: `UPDATE workflow_entity SET active=true WHERE id='...'` en PostgreSQL + `docker restart n8n-*`. Documentar este patrón.

8. **aurenix_it_agent NO tiene acceso a Docker** — Solo root puede gestionar contenedores. Para operaciones Docker siempre usar `ssh vps-aurenix` (root).

9. **El rol de José en la empresa:** Responsable de todas las automatizaciones, sistemas internos, herramientas de gestión empresarial, y las dos webs (cliente e interna). Los socios también trabajan en el stack pero en sus propias ramas/repos.

---

## 5. PROBLEMAS CONOCIDOS Y RIESGOS

### Críticos (bloquean trabajo)
| Problema | Descripción | Solución |
|---|---|---|
| **SSH credential S1** | No se sabe si la credencial `SSH Password account` en n8n tiene el host/user/pass correcto para el VPS | Ir a n8n UI → Settings → Credentials → SSH Password account → verificar que host=`76.13.9.238`, user=`root`, pass=`0Vw&9k'l/yo+OS/IjbPE` |
| **n8n API Key expira** | El JWT token actual expira el **2026-04-01** | Antes de esa fecha, ir a n8n UI → Settings → n8n API → generar nueva key y actualizar `.env.local` y `.mcp.json` |
| **NEXO Manager spam** | Falla cada 5 min → S2 Sentinel spameará cuando se active correctamente | Sebas debe arreglar su workflow. Mientras tanto, S2 puede ignorar este flujo específico con un filtro por workflow name |

### Altos (degradan funcionalidad)
| Problema | Descripción | Solución |
|---|---|---|
| **S3 credencial HTTP** | El nodo `n8n API Create Flow` en S3 usa `httpHeaderAuth` pero puede que el workflow espere formato diferente | Testear enviando `/create test` al bot y ver logs |
| **Monorepo con build errors** | El Next.js dashboard tiene errores previos en `build_error.txt` | Revisar y corregir antes de desarrollar encima |
| **Dos monorepos duplicados** | `AURENIX AGENCY/aurenix-monorepo/` y `_PROJECTS/AURENIX AGENCY/aurenix-monorepo/` — cual es el actual? | Determinar cuál es la versión más reciente y eliminar el duplicado |
| **githubReleaseTrigger no instalado** | S10 usa un nodo de comunidad no instalado en n8n | Instalar en n8n UI → Settings → Community nodes → `n8n-nodes-github-release-trigger` o rediseñar S10 |

### Medios (a tener en cuenta)
| Problema | Descripción |
|---|---|
| **Repos privados sin revisar** | `MIGRACION-COMPLETA`, `SIACompleto`, `Workspaces` en GitHub — contenido desconocido. Pueden tener trabajo relevante que no conocemos |
| **LIBERTAD FINANCIERA** | El proyecto en `_CLIENTS/LIBERTAD FINANCIERA/` es masivo (Python+Rust+DuckDB) y no se ha revisado en absoluto |
| **Vaultwarden sin configurar** | `pass.aurenix.cloud` está activo pero sin cuentas. Debería ser el gestor central de credenciales de la agencia |
| **Fail2ban muy activo** | 785 IPs baneadas históricamente. Nivel de ataque SSH constante. Considerar cambiar puerto SSH a uno no estándar |
| **n8n TLS_REJECT_UNAUTHORIZED=0** | n8n arranca con certificado SSL en modo inseguro (warning en logs). No es crítico pero es técnicamente incorrecto |

---

## 6. CONTEXTO CRÍTICO PARA LA PRÓXIMA SESIÓN

### Lo que el próximo Claude DEBE saber antes de actuar

**SOBRE EL EQUIPO:**
- **José** = el usuario de esta sesión. Responsable de automatizaciones e infraestructura interna. ID Telegram: `501092522`.
- **Sebas** = socio. Trabaja en el servidor en paralelo. Hoy cambió la password de Filebrowser sin avisar. El NEXO Manager fallando es suyo.
- **Hay un tercer socio** cuya identidad no se ha definido aún.
- **Regla de oro:** No tocar, no modificar, no desactivar workflows que no sean los S1-S12. Hay 29 workflows de otros proyectos (Investment Copilot, NEXO, Editorial, etc.) que son de los socios y están activos.

**SOBRE EL SERVIDOR:**
- `ssh vps-aurenix` funciona directamente (alias configurado en `~/.ssh/config`)
- Python para SSH: `/c/Users/Usuario/AppData/Local/Programs/Python/Python314/python`
- Paramiko para SSH remoto — las claves están en `_INFRA/Claves_contraseñas/` (ruta con ñ que causa encoding en Windows). Usar `cat` para leer el contenido y pasarlo como string a paramiko.
- Para queries DB en el servidor: `ssh vps-aurenix 'docker exec postgresql-ps48skwo848408oo8gg04k8k psql -U dVgL7FYPMsvrV5wk -d n8n -c "QUERY"'`
- Columnas camelCase en PostgreSQL requieren comillas dobles: `"workflowId"`, `"startedAt"`, etc.
- Para activar workflows en n8n: `UPDATE workflow_entity SET active=true WHERE id='ID'` + `docker restart n8n-*`. La API pública NO soporta activación vía PATCH.

**SOBRE N8N:**
- API Key en `.env.local` — expira 2026-04-01
- 42 workflows totales. S1, S2, S3 activos. S5-S12 inactivos (decisión del usuario)
- Credenciales enlazadas a S1-S5 hoy. S6-S12 sin credenciales aún.
- El `NEXO Manager - Unified` falla cada 5 min — ignorar, es de Sebas
- El nodo `githubReleaseTrigger` de S10 NO está instalado como nodo de comunidad

**SOBRE GITHUB:**
- Cuenta: `AURENIX-ADMIN` | PAT: en `.env.local` y `.mcp.json`
- SSH Key añadida hoy por el usuario
- 8 repos (3 públicos, 5 privados). Los privados críticos: `aurenix-platform` (vacío), `DESARROLLO-AURENIX`, `MIGRACION-COMPLETA`, `SIACompleto`, `Workspaces`
- **Antes de crear cualquier repo nuevo, revisar si `aurenix-platform` o `SIACompleto` ya contienen lo que se necesita**

**SOBRE EL TRABAJO PENDIENTE DE ESTA SEMANA (según José):**
1. Verificar S1-S3 funcionando end-to-end (primera prioridad)
2. Dashboard web FENIX conectado al stack (segunda prioridad)
3. S5-S12 cuando José lo indique (no antes)
4. Organizar archivos en Filebrowser del servidor
5. Estrategia de branching Git para los 3 socios

**SOBRE SERVICIOS EXTERNOS:**
- Stripe, Apollo.io, HubSpot, Zendesk, etc.: NO hay cuentas configuradas. Se crearán cuando se necesiten.
- Google Sheets: OAuth2 configurada en n8n (credencial `HZjZR5GMuUlJItfs`). No se sabe para qué se usa.
- La única credencial de IA funcional es **Groq** (llama3-70b). OpenAI y Anthropic tienen keys en `.env.local` pero sin valor.

**ARCHIVOS QUE SIEMPRE LEER AL INICIO DE SESIÓN:**
1. `CLAUDE.md` — arquitectura y stack completo
2. `handoff.md` — este archivo, estado al cierre de hoy
3. `.env.local` — todas las credenciales reales

**NUNCA HACER SIN CONFIRMACIÓN EXPLÍCITA:**
- Activar workflows S5-S12
- Tocar workflows que no sean S1-S12
- Hacer push a GitHub sin que José lo pida
- Reiniciar n8n en horario laboral (hay workflows activos de los socios)
- Borrar archivos en el servidor sin confirmación
- Modificar `authorized_keys` del servidor

---

*Generado al cierre de sesión del 6 de Marzo 2026 por IT Agent Senior AURENIX*
