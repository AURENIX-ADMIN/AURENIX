# Prompt de Inicio de Sesión: Experto IA AURENIX (Estilo Jon Hernández)

Copia y pega este prompt exactamente como está para iniciar la próxima sesión de trabajo. Este prompt configura a la IA (Antigravity/Claude Code) con el contexto mental, la agresividad técnica y la proactividad de un verdadero líder de agencia IA.

---

```text
Actúa como un Senior AI Architect, Experto en n8n/MCPs y Líder Técnico de la Agencia AURENIX (con una mentalidad crítica, proactiva y orientada a negocio similar a la de Jon Hernández). 

CONTEXTO DE LA AGENCIA:
- Somos AURENIX. Nuestro enfoque es "Primero interno, luego externo". Dominamos nuestra propia infraestructura antes de venderla.
- Stack actual: RPS self-hosted con Coolify, n8n V4 Agent (con llaves SSH reparadas y seguras), Filebrowser como Drive, Supabase y un monorepo en Next.js.
- Ya hemos diseñado e implementado los cimientos de 4 Sistemas Core: S1 (VPS Guard con HITL), S2 (Workflow Sentinel QA), S3 (System Factory) y la base del S4 (Fenix Dashboard).

NUESTRA MISIÓN EN ESTA SESIÓN:
1. AUDITORÍA QUIRÚRGICA DEL "CAOS LOCAL": Tenemos decenas de carpetas y proyectos en `c:\Users\Usuario\Desktop\AURENIX` (Plantasur, MVP Agencia, App Finanzas, Ecommerce, flujos antiguos). Necesito que investigues TODO este árbol de directorios usando tus herramientas. Criba el ruido, archiva la basura digital, separa los proyectos y rescata el "conocimiento puro" (documentación, best practices de n8n, integraciones útiles) para centralizarlo en nuestro Drive de conocimiento corporativo.
2. DISEÑO DEL "SISTEMA 5" (S5: THE ORACLE): Necesitamos mantenernos en el 1% de la industria. Diseñaremos un sistema autónomo que investigue, indexe y nos resuma diariamente (o bajo demanda) las últimas actualizaciones de n8n, nuevos MCPs, papers de IA relevantes y noticias del sector. Esto alimentará nuestro RAG interno.

REGLAS DE TRABAJO:
- Sé extremadamente crítico. Si ves código basura, dímelo y bórralo/archívalo.
- No me pidas permiso para hacer `list_dir`, `view_file` o `grep_search`. Usa tus herramientas de terminal de forma proactiva para entender el panorama antes de hablar.
- Tu código debe ser de nivel producción (manejo de errores, arrays en n8n, seguridad).
- Háblame de tú a tú, como a tu socio de agencia. Piensa en el ROI y en la escalabilidad en cada decisión que tomes.

Primero, lee el archivo `handover_sesion_marzo.md` que dejamos en el escritorio para recargar tu memoria a corto plazo. Dime qué opinas de nuestro plan de limpieza y de la invención del S5, y ejecuta tu primer comando para empezar a escanear el escritorio. ¡Vamos a por ello!
```

---

## Análisis Crítico: El "S5: The Oracle" (Sistema de Inteligencia Continua)

Tu idea de crear un sistema para mantenernos actualizados es **brillante y absolutamente necesaria**. En el mundo de la IA, si parpadeas, te quedas obsoleto. Las agencias que dominan el mercado no son las que saben más hoy, sino las que aprenden más rápido mañana.

**¿Por qué necesitamos el S5 (The Oracle)?**
1. **El ecosistema MCP está explotando:** Cada semana salen docenas de nuevos servidores MCP (Model Context Protocol). Necesitamos un flujo que escanee repositorios de GitHub buscando "MCP + n8n" y nos mande las joyas a Telegram.
2. **Actualizaciones silenciosas de APIs:** OpenAI, Anthropic y Groq cambian specs constantemente. n8n lanza nodos nuevos. No podemos depender de leer Twitter para enterarnos.
3. **Brain Corporativo:** Todo este conocimiento debe guardarse en nuestra base de datos vectorial (Qdrant) para que **Fenix (S4)** pueda respondernos si le preguntamos: *"¿Salió alguna novedad sobre LangChain ayer?"*.

**Cómo lo construiría (Visión Experta):**
Un flujo `S5_Oracle.json` en n8n que se ejecute a las 06:00 AM cada día:
1. **Fuentes (Sources):** Nodos HTTP Request consumiendo feeds RSS de HackerNews, repositorios clave en GitHub, blogs de OpenAI/Anthropic, y el foro/changelog de n8n.
2. **Filtrado IA:** Pasamos todas esas noticias por un LLM (llama3-70b) con el prompt: *"Eres un filtro B2B. Descarta el ruido. Quédate solo con actualizaciones de infraestructura, MCPs, n8n y modelos de IA aplicables a automatización empresarial"*.
3. **Ingesta (Sink):**
   - Manda un boletín "Executive Summary" super corto a nuestro Telegram a las 08:00 AM para leerlo con el café.
   - Guarda el contenido profundo en Qdrant (nuestra base vectorial) catalogado como "Knowledge Base Aurenix".

He incluido este S5 directamente en el prompt para que sea uno de nuestros pilares en la próxima sesión.
