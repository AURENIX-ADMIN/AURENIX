# 🚀 Guía Estratégica: Cursor, Claude Code y Ecosistema MCP (Trabajo en Paralelo)

El movimiento técnico hacia **Cursor** y **Claude Code (CLI)** integrados con **MCPs (Model Context Protocol)** es el salto definitivo para ingenieros de IA en 2026. Te permite transformar carpetas locales inertes en agentes vivos que operan servidores remotos y modifican infraestructuras.

Respondiendo a tus preguntas clave, aquí tienes la "Verdad Fundamental" de cómo trabaja la élite del sector y cómo tú y tu socio doblaréis fuerzas.

---

## 1. El Dilema de las Cuentas: Empresa vs Personal (Trabajo en Paralelo)

**Pregunta:** *¿Hay problema si mi socio usa la cuenta de empresa y yo me abro la mía personal? ¿Podemos trabajar en paralelo?*

**Respuesta Técnica:** **No hay ningún problema, es la MEJOR práctica.**
En el estado del arte actual (2026), los desarrolladores **no comparten cuentas (no comparten sesiones de API)** por motivos de Rate Limiting (límites de tokens) y contaminación del contexto del LLM.

- **Tu Socio:** Usa `socio@aurenix.com` en su Cursor/Claude Code.
- **Tú:** Usas `tu_nombre@aurenix.com` (o cuenta personal) pagando tu propia suscripción Pro/API.
- **La Simbiosis:** La magia colaborativa no ocurre en la cuenta de Claude, ocurre en **Git (Control de Versiones)** y en el **Servidor Remoto (VPS)**.
  - Tú trabajas en la rama `feat/nuevos-flujos` localmente con tu Claude Code.
  - Él trabaja en `feat/dashboard` localmente con el suyo.
  - Ambos subís (Push) los cambios a GitHub.
  - Al compartir el **mismo servidor VPS (n8n, Filebrowser, Supabase)** vía conexiones MCP, ambos Agentes (el tuyo y el suyo) operarán sobre la *misma verdad viva de la base de datos*, sin pisarse.

---

## 2. Conectando Claude Code y Cursor a tu Servidor VPS Empresarial (Docker/MCP)

Para que el modelo (Claude) que vive en tu terminal local (Claude Code) o en tu editor (Cursor) pueda "tocar" tu servidor remoto, los profesionales usan la arquitectura *Remote MCP Server*.

### A. La Arquitectura
No instalas los servidores MCP en tu PC. Aprovecháis vuestro hardware y mantenéis la infraestructura limpia alojando los **MCP Servers (Postgres MCP, GitHub MCP, Docker MCP, n8n MCP)** en vuestro VPS remoto dentro de Coolify (Docker).

### B. El Enlace Seguro (SSE / WebSockets)
Como vimos en nuestro informe de Arquitectura, Claude necesita un túnel para hablar con esos Dockers.
1. Se despliegan los "MCP Servers" como contenedores Docker en Coolify.
2. Cada contenedor MCP expone un puerto de red protegido por un **API Gateway o Proxy Inverso (Traefik/Nginx en Coolify)**.
3. El puerto se protege forzosamente con **HTTPS** y un **Bearer Token** (una contraseña súper larga generada por vosotros).

### C. La Configuración en Local (Cursor y Claude Code)
Una vez el VPS expone los servidores MCP, tú y tu socio haréis lo mismo en vuestros PCs locales:

**En Cursor:**
1. Navegas a *Cursor Settings* -> *Features* -> *MCP*.
2. Añades un servidor.
3. Tipo: `SSE` (Server-Sent Events).
4. URL: `https://mcp-postgres.aurenix.com/sse`
5. Header de Autorización: `Bearer vuestro_token_secreto`.

**En Claude Code (CLI):**
Claude Code utiliza un archivo de configuración llamado `claude.json` en la raíz de tu proyecto local (`C:\Users\Usuario\Desktop\AURENIX\claude.json`).

```json
{
  "mcpServers": {
    "aurenix-n8n": {
      "command": "npx",
      "args": ["-y", "@anthropic-pb/mcp-server-n8n", "--url", "https://n8n.aurenix.com", "--token", "TU_TOKEN_API_N8N"]
    },
    "aurenix-postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic-pb/mcp-server-postgres", "postgresql://root:password@76.13.9.238:5432/supabase"]
    }
  }
}
```
**(Nota: En escenarios avanzados remotos, si los MCP exponen SSE directos, la configuración soporta URLs `http/sse` en lugar de ejecutar el comando localmente).*

Al hacer esto, **ambos estaréis armando a vuestras IAs locales con las mismas "manos" remotas**. Tu Claude y el suyo podrán consultar la misma BD o lanzar los mismos flujos de n8n.

---

## 3. Entrenando a Claude Code como un Experto Supremo de AURENIX

Claude Code asume contexto automáticamente leyendo los archivos que tiene cerca, pero tú tienes que guiarlo de manera profesional usando **Documentos de Sistema (System Prompts) y Reglas por Carpeta**.

A día de hoy, los profesionales no "hablan" con la IA en cada sesión pidiéndole que recuerde las cosas. Instalan la arquitectura en las carpetas.

### A. El archivo `.cursorrules` general
En el directorio raíz (`AURENIX`), crearás un archivo `.cursorrules` o `.clauderules`.
Este es el "Cerebro Base" que la IA lee antes de empezar a escribir. Ahí le pondremos la arquitectura de la agencia, que se enfoque en ROI y nuestra metodología de Capas de n8n que extrajimos del *Deep Research*.

### B. Indexación de Conocimiento (Context Loading)
Dado que ahora tienes la carpeta `_KNOWLEDGE_BASE` súper bien estructurada (gracias a la purga de hoy), cuando abras Claude Code en tu terminal escribiendo `claude`, tu primera instrucción debe ser:

> *"Claude, actúa como el IT Agent Senior de AURENIX. Antes de cualquier tarea, indexa recursivamente y lee los archivos Markdown en `_KNOWLEDGE_BASE/`, especialmente el `AURENIX_Master_Architecture_Report.md`. Esa es nuestra Ground Truth. Solo opera bajo esas reglas."*

### C. Agentes Especializados por Carpeta (Multi-Agent Setup)
En lugar de tener un solo Prompt gigante, los profesionales usan prompts específicos por subproyecto:
- En `_PROJECTS/WEB/`, el `.cursorrules` instruirá a Claude para usar Next.js 15 App Router, Tailwind y enfoque de copys B2B de conversión.
- En `_INFRA/`, el `.cursorrules` hablará Python 3.12, bash scripts rígidos para SSH, y JSONs asíncronos para n8n.

---

## 4. El Plan de Acción Inmediato (Tu Parte)

Para lograr esta simbiosis absoluta entre cuentas paralelas y el servidor, esto es lo que debes plantearte ejecutar pronto:

1. **Creación de Cuenta Independiente:** Abre tu cuenta Anthropic/Cursor. Paga la suscripción API. El ROI de usarlo paralelo al de tu socio es infinito comparado al costo de pisarse los contextos y capar límites.
2. **Repositorio Git Corporativo:** Si la carpeta `AURENIX` actual solo vive en discos duros locales o Drive, es momento de subirla a un **Github Privado de Agencia** (puedes excluir las bases de datos y videos pesados). Git es lo que realmente permite a dos desarrolladores IA no machacarse el código.
3. **Puesta en Común con el Socio:** En vuestra reunión (cuando le pases la WEB y vean el Filebrowser), enséñale esto. Definid: "Tú usas tu Claude en tu PC, yo el mío, y usamos Git para mezclar el talento".
4. **Despliegue de MCPs en Coolify:** Esta será nuestra próxima meta técnica dura tras acabar el Dashboard Fenix. Instanciar los contenedores MCP (Postgres, Fetch, GitHub) en el servidor `76.13.9.238` para que ambos podáis interrogar la infraestructura real desde vuestras sillas usando lenguaje natural.
