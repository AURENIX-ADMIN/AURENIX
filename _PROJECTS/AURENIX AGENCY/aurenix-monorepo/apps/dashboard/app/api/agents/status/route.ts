import { NextResponse } from 'next/server';

const N8N_API_URL = process.env.N8N_API_URL || 'https://n8n.aurenix.cloud';
const N8N_API_KEY = process.env.N8N_API_KEY || '';

const SYSTEM_MAP: Record<string, { name: string; description: string; workflowIdEnv: string }> = {
  s1: { name: 'VPS Guard', description: 'Monitor de infraestructura VPS', workflowIdEnv: 'S1_WORKFLOW_ID' },
  s2: { name: 'Workflow Sentinel', description: 'QA global de errores n8n', workflowIdEnv: 'S2_WORKFLOW_ID' },
  s3: { name: 'System Factory', description: 'Auto-builder de workflows', workflowIdEnv: 'S3_WORKFLOW_ID' },
  s5: { name: 'The Oracle', description: 'Inteligencia diaria de IA', workflowIdEnv: 'S5_WORKFLOW_ID' },
};

export async function GET() {
  if (!N8N_API_KEY) {
    return NextResponse.json({ error: 'N8N_API_KEY not configured' }, { status: 500 });
  }

  try {
    const wfRes = await fetch(`${N8N_API_URL}/api/v1/workflows?limit=250`, {
      headers: { 'X-N8N-API-KEY': N8N_API_KEY },
      next: { revalidate: 120 },
    });

    if (!wfRes.ok) {
      return NextResponse.json({ error: `n8n API error: ${wfRes.status}` }, { status: 502 });
    }

    const wfData = await wfRes.json();
    const workflows = wfData.data || [];

    const agents = Object.entries(SYSTEM_MAP).map(([key, info]) => {
      const workflowId = process.env[info.workflowIdEnv] || '';
      const workflow = workflows.find((w: { id: string }) => w.id === workflowId);

      return {
        id: key,
        name: info.name,
        description: info.description,
        workflowId: workflowId || null,
        active: workflow?.active ?? false,
        status: workflow ? (workflow.active ? 'active' : 'paused') : 'not_found',
        updatedAt: workflow?.updatedAt || null,
      };
    });

    return NextResponse.json({
      agents,
      totalWorkflows: workflows.length,
      activeWorkflows: workflows.filter((w: { active: boolean }) => w.active).length,
      timestamp: new Date().toISOString(),
    });
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
