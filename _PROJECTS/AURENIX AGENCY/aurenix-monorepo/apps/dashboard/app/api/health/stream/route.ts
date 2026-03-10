import { NextRequest } from 'next/server';

const N8N_API_URL = process.env.N8N_API_URL || 'https://n8n.aurenix.cloud';
const N8N_API_KEY = process.env.N8N_API_KEY || '';

const WORKFLOW_IDS: Record<string, string> = {
  s1_vps_guard: process.env.S1_WORKFLOW_ID || '',
  s2_workflow_sentinel: process.env.S2_WORKFLOW_ID || '',
  s3_system_factory: process.env.S3_WORKFLOW_ID || '',
  s5_the_oracle: process.env.S5_WORKFLOW_ID || '',
};

async function fetchHealthSnapshot() {
  const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  const systems: Record<string, unknown> = {};

  for (const [key, wfId] of Object.entries(WORKFLOW_IDS)) {
    if (!wfId || !N8N_API_KEY) {
      systems[key] = { status: 'unknown', errorCount24h: 0, successCount24h: 0 };
      continue;
    }

    try {
      const [errRes, okRes] = await Promise.all([
        fetch(`${N8N_API_URL}/api/v1/executions?workflowId=${wfId}&limit=10&status=error&startedAfter=${since}`, {
          headers: { 'X-N8N-API-KEY': N8N_API_KEY },
        }),
        fetch(`${N8N_API_URL}/api/v1/executions?workflowId=${wfId}&limit=10&status=success&startedAfter=${since}`, {
          headers: { 'X-N8N-API-KEY': N8N_API_KEY },
        }),
      ]);

      const errData = errRes.ok ? await errRes.json() : { data: [] };
      const okData = okRes.ok ? await okRes.json() : { data: [] };
      const errors = errData.data?.length || 0;
      const successes = okData.data?.length || 0;

      systems[key] = {
        status: errors === 0 ? 'operational' : errors / (errors + successes) > 0.5 ? 'alert' : 'degraded',
        errorCount24h: errors,
        successCount24h: successes,
        lastExecution: okData.data?.[0]?.stoppedAt || null,
      };
    } catch {
      systems[key] = { status: 'down', errorCount24h: 0, successCount24h: 0 };
    }
  }

  return { ...systems, timestamp: new Date().toISOString() };
}

export async function GET(req: NextRequest) {
  const encoder = new TextEncoder();
  let closed = false;

  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: unknown) => {
        if (closed) return;
        try {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
        } catch {
          closed = true;
        }
      };

      // Send initial data immediately
      try {
        const snapshot = await fetchHealthSnapshot();
        send(snapshot);
      } catch {
        send({ error: 'Failed to fetch initial data' });
      }

      // Send updates every 30 seconds
      const interval = setInterval(async () => {
        if (closed) { clearInterval(interval); return; }
        try {
          const snapshot = await fetchHealthSnapshot();
          send(snapshot);
        } catch {
          send({ error: 'Failed to fetch update' });
        }
      }, 30_000);

      // Cleanup after 5 minutes (client should reconnect)
      setTimeout(() => {
        closed = true;
        clearInterval(interval);
        try { controller.close(); } catch { /* already closed */ }
      }, 5 * 60 * 1000);
    },
    cancel() {
      closed = true;
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
