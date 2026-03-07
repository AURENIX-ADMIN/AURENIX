# AURENIX Master Architecture Report (2024-2026)
*Basado en el Deep Research de la élite B2B AI Agency.*

Este documento establece la "Verdad Fundamental" (Ground Truth) para la escalabilidad de AURENIX. Define cómo se deben construir los flujos de n8n y cómo Next.js interactúa con ellos para ofrecer una experiencia de cliente Mágica e Instantánea.

---

## 1. El Paradigma de las Capas (Layered Automation)
Nunca más construiremos "flujos espagueti". Todo microservicio de n8n se dividirá estrictamente en 4 capas aislando responsabilidades:

1. **Capa de Ingesta (Asíncrona):** El nodo de webhook *nunca* procesa. Solo recibe el payload, lo empuja a una base de datos en memoria (Redis `LPUSH`) y devuelve un `200 OK` al cliente iterando en <50ms para evitar timeouts.
2. **Capa Lógica/Cognitiva (Agentic):** Un `Cron` o Worker saca elementos de Redis (`RPOP`). Aquí operan los LLMs en patrones como *Chained Requests* o *Stateful Agents*. Todo sub-proceso genérico (limpiar strings, fechas) debe ir en un sub-workflow (`Execute Workflow`).
3. **Capa de Acción (Batching):** Centraliza las llamadas a APIs externas (CRM, Stripe). No se insertan datos 1 a 1 síncronamente; se agrupan en lotes (batching de 50-150 registros) para evitar bloqueos por rate limits.
4. **Capa de Fallback (Global Error Workflow):** Todo nodo crítico (HTTP, Switch) debe tener enrutamiento de errores activado. Si algo falla cataastróficamente, el flujo deriva a un subflujo global que guarda el log en *Workflow Sentinel*, reencola el payload en un Dead Letter Queue y alerta a Slack/Telegram.

---

## 2. El Ecosistema "Core 12" de la Agencia
AURENIX evoluciona de 5 a 12 sistemas esenciales. Estos 7 nuevos sistemas son el estándar de oro de la industria en ROI:

- **S6: Autonomous Integration (Onboarding Técnico):** Automatiza creación de carpetas (Drive), extracción de briefing (LLMs) y configuración CRM. *Aceleración del ciclo de días a 15 mins.*
- **S7: Intelligent Billing Engine (Facturación Autónoma):** Conecta Stripe con QuickBooks/Xero. Crea recibos, consolida discrepancias contables y emite facturas PDF. *Ahorra 10hrs semanales al equipo financiero.*
- **S8: AI Demand Generation (Lead Scoring):** Apollo.io + LinkedIn API -> LLMs hacen scoring de +50 variables -> Envío de cold emails ultra personalizados. *Aumenta la conversión B2B un 30%.*
- **S9: Retention Oracle (Prevención de Churn):** Telemetría + Análisis de Sentimiento en Zendesk. Detecta riesgo de abandono y aplica descuentos autónomos vía Stripe. *Reduce el churn un 20-40%.*
- **S10: Autonomous DevOps (CI/CD Agéntico):** Al abrir un Pull Request en GitHub, un LLM Frontera analiza el diff, detecta vulnerabilidades y comenta el código inline ("Reviewed by AI"). *Aumenta la velocidad de fusión un 98%.*
- **S11: Cognitive Support Gateway (Inbox Zero):** Triage semántico de la bandeja de entrada. Convierte correos a Markdown, extrae contexto de pantallazos con ChatGPT Vision, etiqueta y genera borradores de respuesta usando RAG. *Soluciona el 80% de tickets genéricos.*
- **S12: Data Unification Bus (Sincronización CRM Maestra):** Bus de datos asíncrono que unifica HubSpot, Salesforce y Bases propias con operaciones Upsert y deduplicación semántica.

*(Estrategia: Importaremos los IDs oficiales de plantillas de n8n sugeridos en el reporte para S7, S8, S10, S11 y S12 en lugar de programarlos desde cero).*

---

## 3. Arquitectura FENIX Dashboard (El Control Plane)
Cómo integrar Next.js 15 (App Router) con n8n/Supabase en B2B:

1. **Patrón Backend-for-Frontend (BFF):**
   - El cliente de React *nunca* hace llamadas a webhooks de n8n directos.
   - El cliente llama a los *Route Handlers* de Next.js (`/api/server/...`).
   - El servidor de Next.js inyecta los *secrets* (BEARER TOKENS), aplica Rate Limiting, sanitiza (Zod) y hace proxy al n8n. Adiós problemas de CORS y claves expuestas.
2. **Unidirectional Streaming (SSE):**
   - Para respuestas largas de IA (ej. un análisis del Oracle S5), usamos Server-Sent Events. El BFF devuelve un `ReadableStream` para hacer el efecto de tipeado progresivo sin long-polling obsoleto.
3. **Colaboración Bidireccional (Supabase Realtime):**
   - Para estados complejos asíncronos: El cliente envía peticion a BFF -> n8n encola en Redis -> n8n hace el trabajo pesado -> n8n **actualiza Supabase directamente** -> Supabase bombea el cambio a Next.js por **WebSockets (cambio de estado)**. Se asume instantáneo gracias al RLS (Row Level Security) que blinda el canal multiusuario con el JWT de la sesión.

---

## 4. MCP (Model Context Protocol) 
Es el cambio de juego para 2026. Al activar nodos MCP en n8n:
- **n8n como Acción (Server):** Claude Desktop puede "descubrir" los flujos de AURENIX a través de JSON Schemas y ejecutarlos directamente desde el chat ("Hazme el informe de churn de hoy", y el LLM llama a n8n por debajo).
- **n8n como Orquestador (Client):** n8n puede pedir ayuda a servidores externos (ej. Python estadístico local) para tareas matemáticas sin tener que picar nodos custom.
*Requiere túneles SSE inexpugnables, HTTPS forzado y Sticky Sessions en Coolify/Docker.*
