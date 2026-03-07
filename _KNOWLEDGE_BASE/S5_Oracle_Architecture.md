# S5: THE ORACLE (Arquitectura de Inteligencia Continua)

## 1. Visión y Propósito (El ROI)
En el ecosistema B2B AI de AURENIX, quedarse atrás en tecnología significa perder clientes high-ticket. **The Oracle (S5)** es un sistema 100% autónomo ("Set it and forget it") que mapea diariamente el ecosistema de IA, extrae la "señal del ruido" y nutre nuestra base de conocimiento corporativa.

- **Frecuencia:** Ejecución diaria a las 06:00 AM.
- **Salida:** Un informe Ejecutivo en Telegram/Slack y Nodos Vectoriales en Qdrant.

---

## 2. Pipeline de n8n (Arquitectura de Nodos)

### Fase A: Ingesta (Sensors)
Usaremos nodos `RSS Feed Read` y `Webhook HTTP Request` para escanear fuentes de alto valor:
1. **GitHub Trending (Tags: AI, LLM, MCP, n8n):** Para detectar nuevas herramientas open-source.
2. **HackerNews (Filtro 'AI'):** Para comprender el sentimiento del mercado tech.
3. **OpenAI / Anthropic / Groq Release Notes:** Updates oficiales de modelos.
4. **Reddit (r/LocalLLaMA):** Tendencias underground y benchmarks reales.

### Fase B: Triage & Filtrado Zero-Shot (The Gatekeeper)
Pasaremos los títulos y extractos cortos por **Llama-3-8B-8192 (vía Groq por velocidad y coste casi $0)** con un prompt especializado:

```text
Evalúa esta noticia tecnológica. ¿Es altamente relevante para una agencia B2B que implementa automatizaciones con n8n, LLMs y RAG?
Responde SOLO en JSON: {"score": 0-10, "relevant": true/false, "reason": "..."}
```
*Si `score < 7` o `relevant == false`, la rama termina (Drop).*

### Fase C: Deep Extraction (The Scholar)
Para las noticias que sobreviven al filtro (Score 7-10), necesitamos su contenido completo:
- Usaremos **Jina Reader API (`https://r.jina.ai/[URL]`)** mediante un nodo HTTP Request. Jina extrae el texto limpio en formato Markdown optimizado para LLMs esquivando pop-ups y banners.
- Ese contenido en bruto se enviará a un LLM más pesado (ej. **Llama-3-70B** o **GPT-4o-mini**) para:
  1. Extraer el TL;DR (Problema y Solución).
  2. Identificar Oportunidades de Negocio B2B para AURENIX.
  3. Evaluar la "Complejidad Técnica".

### Fase D: Distribución Multicanal (The Broadcaster)
El Output final se bifurca en dos Storage Layers:
1. **Memoria a Corto Plazo (Ejecutiva):** Un mensaje consolidado en Telegram.
   *Formato:* `S5 THE ORACLE - Reporte Diario. [Emoji] Novedad: XYZ. ROI B2B: ...`
2. **Memoria a Largo Plazo (RAG):** Las conclusiones técnicas se estructuran y se insertan con Pinecone/Qdrant + Supabase Vector, indexadas bajo el namespace de `AURENIX_AGENCY_KNOWLEDGE`. 
   Cuando el *Agente IT* o el *S4 Dashboard Asistente* necesiten saber "qué es un MCP en n8n", el RAG recuperará estos documentos exactos.

---

## 3. Despliegue Técnico (To-Do List para la Próxima Sesión)
- [ ] Mapear las 5 URLs públicas de RSS cruciales.
- [ ] Obtener API Key de Jina Reader.
- [ ] Configurar Qdrant localmente vía Docker Compose en Coolify (o usar la instancia actual de Supabase si tiene `pgvector` activado).
- [ ] Ensamblar el workflow en n8n integrando el `Groq Chat Node`.
