# AURENIX - Plan de Trabajo

## Fase 1: Estabilizacion (Actual)
- [ ] Verificar S1/S3 end-to-end
- [ ] Commit inicial del repo con .gitignore limpio
- [ ] Auditoria quirurgica del directorio local
- [ ] Consolidar monorepos duplicados (AURENIX AGENCY/ vs _PROJECTS/AURENIX AGENCY/)
- [ ] Renovar n8n API Key antes de 2026-04-01

## Fase 2: Core Systems Online
- [ ] S5 The Oracle: implementar pipeline RSS->Groq->Jina->Qdrant->Telegram
- [ ] Dashboard FENIX: deploy en VPS via Coolify
- [ ] Conectar S1/S2 POST a /api/health del dashboard
- [ ] Configurar Vaultwarden como gestor central de credenciales

## Fase 3: Expansion (S6-S12)
- [ ] Crear cuentas en servicios externos (Stripe, Apollo.io, etc.)
- [ ] Importar y activar S6-S12 en n8n con credenciales reales
- [ ] Testear cada sistema individualmente

## Fase 4: Produccion y Clientes
- [ ] Estrategia de branching Git para 3 socios
- [ ] Pipeline CI/CD basico (GitHub -> VPS)
- [ ] Onboarding de nuevos clientes via S6
- [ ] Arquitectura FENIX: LangGraph + Temporal.io (cuando escale)

## Decisiones Pendientes del Usuario
- Cuando activar S5 Oracle
- Clerk auth para dashboard: cuenta real o quitar?
- Revisar repos privados GitHub (MIGRACION-COMPLETA, SIACompleto, Workspaces)
- Cambiar puerto SSH del VPS (785 IPs baneadas por Fail2ban)
