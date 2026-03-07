import { NextRequest, NextResponse } from 'next/server';

const N8N_API_URL = process.env.N8N_API_URL || 'https://n8n.aurenix.cloud';
const N8N_API_KEY = process.env.N8N_API_KEY || '';

// Workflow IDs for S1 and S2 — update after confirming in n8n
const WORKFLOW_IDS: Record<string, string> = {
  s1_vps_guard: process.env.S1_WORKFLOW_ID || '',
  s2_workflow_sentinel: process.env.S2_WORKFLOW_ID || '',
};

type SystemStatus = 'operational' | 'degraded' | 'down' | 'alert' | 'unknown';

interface SystemHealth {
  status: SystemStatus;
  lastCheck: string;
  message: string;
  lastExecution?: {
    id: string;
    finished: boolean;
    status: string;
  };
}

async function getWorkflowHealth(workflowId: string, systemName: string): Promise<SystemHealth> {
  if (!workflowId || !N8N_API_KEY) {
    return {
      status: 'unknown',
      lastCheck: new Date().toISOString(),
      message: `${systemName}: API key o workflow ID no configurado`,
    };
  }

  try {
    const res = await fetch(
      `${N8N_API_URL}/api/v1/executions?workflowId=${workflowId}&limit=1&status=error`,
      {
        headers: { 'X-N8N-API-KEY': N8N_API_KEY },
        next: { revalidate: 60 },
      }
    );

    if (!res.ok) {
      return {
        status: 'unknown',
        lastCheck: new Date().toISOString(),
        message: `n8n API error: ${res.status}`,
      };
    }

    const errorData = await res.json();
    const recentErrors = errorData.data?.length || 0;

    // Get last successful execution
    const successRes = await fetch(
      `${N8N_API_URL}/api/v1/executions?workflowId=${workflowId}&limit=1&status=success`,
      {
        headers: { 'X-N8N-API-KEY': N8N_API_KEY },
        next: { revalidate: 60 },
      }
    );

    let lastSuccess = null;
    if (successRes.ok) {
      const successData = await successRes.json();
      lastSuccess = successData.data?.[0];
    }

    const status: SystemStatus = recentErrors > 0 ? 'alert' : 'operational';
    const lastCheck = lastSuccess?.stoppedAt || new Date().toISOString();

    return {
      status,
      lastCheck,
      message: recentErrors > 0
        ? `${recentErrors} error(es) reciente(s)`
        : `Operativo. Ultima ejecucion: ${lastCheck}`,
      lastExecution: lastSuccess ? {
        id: lastSuccess.id,
        finished: lastSuccess.finished,
        status: lastSuccess.status,
      } : undefined,
    };
  } catch (error: any) {
    return {
      status: 'down',
      lastCheck: new Date().toISOString(),
      message: `Error conectando a n8n: ${error.message}`,
    };
  }
}

export async function GET() {
  const [s1, s2] = await Promise.all([
    getWorkflowHealth(WORKFLOW_IDS.s1_vps_guard, 'S1 VPS Guard'),
    getWorkflowHealth(WORKFLOW_IDS.s2_workflow_sentinel, 'S2 Workflow Sentinel'),
  ]);

  return NextResponse.json({
    s1_vps_guard: s1,
    s2_workflow_sentinel: s2,
    timestamp: new Date().toISOString(),
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    // Webhook endpoint for n8n to push status updates
    return NextResponse.json({ success: true, received: body });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
