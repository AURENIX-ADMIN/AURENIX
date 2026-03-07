# EL MANIFIESTO DE AURENIX: Arquitectura para la Agencia Autónoma y el Roadmap de Escalabilidad Computacional

## Introducción: La Transición de Servicios a Sistema Operativo

La industria de la inteligencia artificial aplicada se encuentra en un punto de inflexión crítico. El modelo tradicional de agencia, basado en la facturación por horas hombre y el desarrollo artesanal de soluciones ("time-and-materials"), está siendo rápidamente obsoleto por la economía de la automatización. Para que Aurenix Agency no solo sobreviva, sino que domine este nuevo paradigma, debemos ejecutar una transformación estructural profunda: dejar de ser una consultora de servicios para convertirnos en una plataforma de orquestación de inteligencia.

Este documento, denominado "El Manifiesto de Aurenix", no es simplemente un plan técnico; es la constitución estratégica que regirá nuestra expansión durante los próximos seis meses. Nuestra tesis central es que la escalabilidad en la era de la IA no se logra añadiendo más ingenieros, sino abstrayendo la complejidad operativa en un "Agency OS" (Sistema Operativo de Agencia). Este sistema desacoplará la definición del producto de su ejecución, permitiéndonos desplegar miles de agentes autónomos con una gobernanza financiera estricta y una capacidad de I+D automatizada.

El objetivo es construir una infraestructura multi-tenant (multi-inquilino) robusta, capaz de gestionar la volatilidad inherente de los costes de inferencia de los LLMs mediante un sistema de contabilidad de doble entrada, mientras estandarizamos la creación de flujos de trabajo complejos a través de configuraciones dinámicas interpretadas por Temporal.io. A continuación, se detalla la arquitectura, la estrategia de producto y el plan de ejecución táctico que nos llevará a la supremacía operativa.

---

## 1. Arquitectura del "Agency OS": El Núcleo Financiero y Administrativo

La piedra angular de cualquier operación de IA a escala no es el modelo de lenguaje en sí, sino la capacidad de gestionar sus unit economics (economía unitaria) con precisión quirúrgica. Los modelos de precios tradicionales de SaaS (suscripción plana) son fundamentalmente incompatibles con la naturaleza variable del consumo de tokens en la IA generativa.

Por lo tanto, el núcleo del Agency OS de Aurenix será un **Ledger de Créditos de Doble Entrada**. Implementaremos un sistema contable estricto inspirado en los estándares bancarios y la arquitectura interna de Stripe o Twilio, garantizando que cada token consumido tenga una trazabilidad financiera auditable.

### 1.1 El Imperativo del Libro Mayor de Doble Entrada (Double-Entry Ledger)
Adoptar el principio de "Code is Law, Ledger is Truth" implica que nunca modificamos un saldo directamente; siempre registramos un movimiento que debe balancear perfectamente.

**1.1.1 Filosofía de Diseño y Seguridad Transaccional**
El sistema se basa en la ecuación fundamental: **Activos = Pasivos + Patrimonio**.
*   **Activos (Assets):** Dinero real en Stripe o bancos.
*   **Pasivos (Liabilities):** Créditos comprados por clientes (nuestra deuda de servicio).
*   **Ingresos (Revenue):** Valor reconocido tras la ejecución exitosa de una tarea.

**1.1.2 Implementación Técnica de la Atomicidad**
Utilizaremos Stored Procedures en PL/pgSQL para manejar el bloqueo optimista. La función `record_usage_transaction` bloqueará la fila de la cuenta, verificará el saldo (actuando como Kill Switch financiero), insertará la entrada y confirmará las dos líneas de movimiento (débito/crédito) atómicamente.

### 1.2 Dashboard de Administración y Métricas de Rentabilidad
Utilizaremos **Supabase** para reflejar el consumo en tiempo real.
*   **Aislamiento Multi-Tenant:** Implementación de **Row Level Security (RLS)** nativo de PostgreSQL para garantizar que ningún cliente acceda a datos de otro.
*   **Métricas Clave (KPIs):** Margen por Workflow (coste API vs. créditos cobrados), Burn Rate de créditos y análisis de Latencia vs. Coste.

---

## 2. Estandarización de Productos: La Fábrica de Bots con Temporal.io

Para evitar el "sprawl" de código, adoptaremos un patrón de **Bot Factory**. Desarrollaremos un Motor de Interpretación Universal sobre **Temporal.io** que lea configuraciones (JSON/YAML) y ejecute la lógica dinámicamente.

### 2.1 El Patrón del Intérprete Dinámico (Dynamic Workflow Interpreter)
Temporal garantiza durabilidad y ejecución determinista. El sistema se compone de:
*   **El Plano (Blueprint):** Archivo YAML que define la lógica.
*   **El Intérprete:** Código en Temporal que orquesta las tareas.
*   **Actividades Atómicas:** Biblioteca de funciones reutilizables (`ScrapeUrl`, `LLMInference`, `SlackNotify`, etc.).

### 2.2 Estrategias de Aislamiento y Manejo de Errores
*   **Particionamiento de Colas:** Tier Standard (cola global) y Tier Enterprise (colas y workers dedicados para evitar el problema del "vecino ruidoso").
*   **Sagas (Compensación):** Lógica automática para reembolsar créditos si un paso crítico del flujo falla irremediablemente.

---

## 3. Motor de I+D Automatizado: El Agente "Sentinel"

"Sentinel" es un sistema multi-agente que simula el flujo de trabajo de un investigador humano para mantener a la agencia en la frontera tecnológica.

*   **Fase 1 (Scanner):** Escaneo diario de Arxiv, GitHub Trending y Hugging Face.
*   **Fase 2 (Filter):** Patrón "LLM-as-a-Judge" para puntuar la aplicabilidad práctica de los hallazgos.
*   **Fase 3 (Researcher):** Análisis profundo de papers seleccionados, descarga de código y síntesis técnica.
*   **Fase 4 (Dissemination):** Notificación en Slack (#intel-daily) e inyección de conocimiento en el RAG interno de la agencia.

---

## 4. Stack de Herramientas e Integraciones

| Capa | Herramienta | Justificación |
| :--- | :--- | :--- |
| **Orquestación** | Temporal.io (Python SDK) | Durabilidad y manejo de estados complejos. |
| **Base de Datos** | Supabase (PostgreSQL) | DB, Auth, Realtime y Vector Store integrado. |
| **Observabilidad** | Arize Phoenix | Tracing agnóstico y evaluación de alucinaciones. |
| **Integraciones** | Slack / WhatsApp API | Canales B2B y de alto volumen. |
| **CRM Sync** | HubSpot API | Fuente de verdad para datos de clientes. |

---

## 5. Plan de Ejecución Táctico: Roadmap a 6 Meses

### Época 1: Cimientos y Control Financiero (Meses 1-2)
*   **Sprints 1-2:** Despliegue de infraestructura core y Ledger atómico.
*   **Sprints 3-4:** Intérprete v0.1 y Dashboard administrativo básico.

### Época 2: La Fábrica y el Centinela (Meses 3-4)
*   **Sprints 5-6:** Activación de Sentinel (Scanner e Intel en Slack).
*   **Sprints 7-8:** Expansión de la librería de actividades y Beta Release con 5 clientes.

### Época 3: Optimización, Gobierno y Escala (Meses 5-6)
*   **Sprints 9-10:** UI "Workflow Builder" y colas dedicadas Enterprise.
*   **Sprints 11-12:** Implementación de "Circuit Breakers" de seguridad y lanzamiento de la API pública.

---

## 6. Estructura de Carpetas y Especificaciones Técnicas

Se adoptará un **Monorepo** (`aurenix-os/`) estructurado en:
*   `apps/dashboard`: Next.js para administración.
*   `services/temporal-worker`: El núcleo lógico en Python (actividades y workflows).
*   `services/sentinel`: Módulos de investigación.
*   `infra/supabase`: Migraciones de base de datos y esquema financiero.

---

## 7. Gobernanza y Gestión de Riesgos: El "Kill Switch"

*   **Nivel Financiero:** Bloqueo de ejecución si el saldo es insuficiente o negativo.
*   **Nivel Técnico:** Timeouts duros en Temporal para evitar bucles infinitos costosos.
*   **Nivel Administrativo:** Endpoint de parada de emergencia por `tenant_id`.
*   **Privacidad:** Redacción de PII (datos personales) antes de enviar información a LLMs públicos.
