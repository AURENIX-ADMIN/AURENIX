import { NextRequest, NextResponse } from 'next/server';

const N8N_API_URL = process.env.N8N_API_URL || 'https://n8n.aurenix.cloud';
const N8N_API_KEY = process.env.N8N_API_KEY || '';

const WORKFLOW_IDS: Record<string, string> = {
  s1_vps_guard: process.env.S1_WORKFLOW_ID || '',
  s2_workflow_sentinel: process.env.S2_WORKFLOW_ID || '',
  s3_system_factory: process.env.S3_WORKFLOW_ID || '',
  s5_the_oracle: process.env.S5_WORKFLOW_ID || '',
};

type SystemStatus = 'operational' | 'degraded' | 'down' | 'alert' | 'unknown';

interface SystemHealth {
  status: SystemStatus;
  lastCheck: string;
  message: string;
  errorCount24h: number;
  successCount24h: number;
  lastExecution?: {
    id: string;
    finished: boolean;
    status: string;
    stoppedAt: string;
  };
}

async function getWorkflowHealth(workflowId: string, systemName: string): Promise<SystemHealth> {
  if (!workflowId || !N8N_API_KEY) {
    return {
      status: 'unknown',
      lastCheck: new Date().toISOString(),
      message: `${systemName}: API key o workflow ID no configurado`,
      errorCount24h: 0,
      successCount24h: 0,
    };
  }

  try {
    // FIX: Filter by last 24h to avoid marking old errors as current alerts
    const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

    const [errorRes, successRes] = await Promise.all([
      fetch(
        `${N8N_API_URL}/api/v1/executions?workflowId=${workflowId}&limit=50&status=error&startedAfter=${since}`,
        {
          headers: { 'X-N8N-API-KEY': N8N_API_KEY },
          next: { revalidate: 60 },
        }
      ),
      fetch(
        `${N8N_API_URL}/api/v1/executions?workflowId=${workflowId}&limit=50&status=success&startedAfter=${since}`,
        {
          headers: { 'X-N8N-API-KEY': N8N_API_KEY },
          next: { revalidate: 60 },
        }
      ),
    ]);

    if (!errorRes.ok || !successRes.ok) {
      return {
        status: 'unknown',
        lastCheck: new Date().toISOString(),
        message: `n8n API error: ${errorRes.status}/${successRes.status}`,
        errorCount24h: 0,
        successCount24h: 0,
      };
    }

    const errorData = await errorRes.json();
    const successData = await successRes.json();
    const errorCount = errorData.data?.length || 0;
    const successCount = successData.data?.length || 0;
    const lastSuccess = successData.data?.[0];
    const totalExecs = errorCount + successCount;

    let status: SystemStatus;
    if (totalExecs === 0) {
      status = 'unknown';
    } else if (errorCount === 0) {
      status = 'operational';
    } else if (errorCount > 0 && successCount > 0) {
      status = errorCount / totalExecs > 0.5 ? 'alert' : 'degraded';
    } else {
      status = 'down';
    }

    const lastCheck = lastSuccess?.stoppedAt || new Date().toISOString();

    return {
      status,
      lastCheck,
      message: status === 'operational'
        ? `Operativo. ${successCount} ejecuciones exitosas (24h)`
        : `${errorCount} error(es) en 24h, ${successCount} exitosas`,
      errorCount24h: errorCount,
      successCount24h: successCount,
      lastExecution: lastSuccess ? {
        id: lastSuccess.id,
        finished: lastSuccess.finished,
        status: lastSuccess.status,
        stoppedAt: lastSuccess.stoppedAt,
      } : undefined,
    };
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Unknown error';
    return {
      status: 'down',
      lastCheck: new Date().toISOString(),
      message: `Error conectando a n8n: ${msg}`,
      errorCount24h: 0,
      successCount24h: 0,
    };
  }
}

export async function GET() {
  const entries = Object.entries(WORKFLOW_IDS);
  const results = await Promise.all(
    entries.map(([key, id]) => getWorkflowHealth(id, key))
  );

  const systems: Record<string, SystemHealth> = {};
  entries.forEach(([key], i) => { systems[key] = results[i]; });

  return NextResponse.json({
    ...systems,
    timestamp: new Date().toISOString(),
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    return NextResponse.json({ success: true, received: body });
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
