# AURENIX - Handoff Inter-Sesion
**Ultima actualizacion:** 7 Marzo 2026
**Sesion anterior:** 6 Marzo 2026 (ver handoff.md en raiz para detalle completo)

## Estado Actual

### Infraestructura - OPERATIVA
- VPS 76.13.9.238 con Coolify v4, todos los contenedores healthy (7+ dias up)
- SSH configurado: `vps-aurenix` (root), `vps-agent` (aurenix_it_agent)
- n8n v2.1.5: 42 workflows, S1/S2/S3 activados con credenciales

### Sistemas Core
| Sistema | Estado | Nota |
|---|---|---|
| S1 VPS Guard | ACTIVO | SSH credential corregida (Ed25519 root). Pendiente confirmar ejecucion exitosa |
| S2 Sentinel | ACTIVO | Funciona - capturo error de S1 correctamente |
| S3 Factory | ACTIVO | URL corregida. Pendiente test real con /create |
| S4 FENIX | BUILD OK | Next.js monorepo en _PROJECTS/. Pendiente deploy |
| S5 Oracle | INACTIVO | Credenciales enlazadas, usuario pidio NO activar aun |
| S6-S12 | INACTIVOS | JSONs en _INFRA/, sin credenciales asignadas |

### Git
- Repo inicializado, branch main, CERO commits
- Todo untracked. No se ha hecho commit inicial aun
- .gitignore existe y protege secretos

### MCPs (.mcp.json)
- aurenix-n8n: OK
- aurenix-postgres: OK
- aurenix-filesystem: OK
- aurenix-fetch: OK
- aurenix-github: OK (PAT configurado)

## Pendientes Prioritarios
1. Verificar S1 ejecuta correctamente (primer cron post-fix SSH)
2. Test S3 con /create en Telegram
3. Auditoria/limpieza del directorio local (caos de carpetas)
4. S5 The Oracle: implementar cuando Jose lo indique
5. Dashboard FENIX: deploy en VPS
6. Commit inicial del repo

## Alertas
- n8n API Key expira 2026-04-01 - renovar antes
- NEXO Manager (Sebas) falla cada 5min - no tocar
- Dos monorepos duplicados sin consolidar
- Vaultwarden sin configurar
