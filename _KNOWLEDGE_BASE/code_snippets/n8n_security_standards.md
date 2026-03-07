# Estándares de Seguridad n8n (Agencia AURENIX)

Basado en el `Flujo_Agente_IT_n8n_v4.json`, todos los flujos que involucren agentes autónomos de IA con capacidad de ejecución (HITL o completamente autónomos) deben implementar la siguiente arquitectura de "Defensa en Profundidad":

## 1. Zero Trust Filter (Autenticación Dura)
El primer nodo después del Trigger (como Telegram) debe ser un condicional estricto que valide el ID del remitente. No se confía en nombres de usuario, solo en IDs numéricos.

```javascript
// Si Telegram:
{{ $json.message.from.id }} === ID_AUTORIZADO
```

## 2. Inyección de Prompt del Cerebro AI (Guardarraíles de Contexto)
El LLM (preferentemente Llama-3 a través de Groq para baja latencia) debe tener instrucciones explícitas sobre su rol y el formato de salida obligatorio (JSON).

**Ejemplo de System Prompt:**
```text
Eres el Agente IT de AURENIX.
REGLAS CRÍTICAS:
1. Solo puedes ejecutar comandos de monitorización.
2. SIEMPRE debes responder en formato JSON: {"command": "tu_comando", "explanation": "..."}.
3. No intentes ejecutar comandos destructivos.
```

## 3. Escudo de Seguridad (Validación Determinista en JS)
Independientemente de lo inteligente que sea el LLM, *nunca* se debe pasar su output directo al nodo ejecutor (SSH, HTTP, Bash). Debe pasar por un nodo de código `Code` que valide determinísticamente contra una lista blanca o negra.

**Ejemplo JS Validator:**
```javascript
const allowedPrefixes = ['docker ps', 'free', 'uptime', 'ls', 'python scripts/'];
const blockedKeywords = ['rm ', 'dd ', 'mkfs', '>', 'shutdown', 'chmod 777'];

try {
  // Parseo Seguro
  const aiResponse = JSON.parse($node["Cerebro AI"].json.text);
  const cmd = aiResponse.command.trim();
  
  // Condición Estricta
  let isAllowed = allowedPrefixes.some(p => cmd.startsWith(p));
  let hasForbidden = blockedKeywords.some(k => cmd.includes(k));

  if (isAllowed && !hasForbidden) {
    return { command: cmd, safe: true };
  } else {
    // Retorno de Error con bloqueo para el siguiente nodo
    return { error: "Comando bloqueado", command: cmd, safe: false };
  }
} catch (e) {
  return { error: "JSON Inválido" };
}
```

## 4. Alertas Separadas 
Debe existir una rama separada para gestionar incidencias. Si el nodo anterior retorna `safe: false`, se envía un mensaje inmediato de "ALERTA DE SEGURIDAD" al canal de logging en Slack/Telegram alertando al arquitecto.
