import { NextResponse } from 'next/server';

const N8N_API_URL = process.env.N8N_API_URL || 'https://n8n.aurenix.cloud';
const N8N_API_KEY = process.env.N8N_API_KEY || '';

export async function GET() {
  if (!N8N_API_KEY) {
    return NextResponse.json({ error: 'N8N_API_KEY not configured' }, { status: 500 });
  }

  try {
    const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
    const execRes = await fetch(
      `${N8N_API_URL}/api/v1/executions?limit=100&startedAfter=${since}`,
      {
        headers: { 'X-N8N-API-KEY': N8N_API_KEY },
        next: { revalidate: 300 },
      }
    );

    if (!execRes.ok) {
      return NextResponse.json({ error: `n8n API error: ${execRes.status}` }, { status: 502 });
    }

    const execData = await execRes.json();
    const executions = execData.data || [];

    const timeline = executions.slice(0, 50).map((e: Record<string, unknown>) => ({
      id: e.id,
      workflowId: e.workflowId,
      workflowName: (e.workflowData as Record<string, unknown>)?.name || 'Unknown',
      status: e.status,
      startedAt: e.startedAt,
      stoppedAt: e.stoppedAt,
      mode: e.mode,
    }));

    const total = executions.length;
    const errors = executions.filter((e: Record<string, unknown>) => e.status === 'error').length;
    const successes = executions.filter((e: Record<string, unknown>) => e.status === 'success').length;

    return NextResponse.json({
      timeline,
      stats: {
        total,
        errors,
        successes,
        successRate: total > 0 ? Math.round((successes / total) * 100) : 0,
        period: '7d',
      },
      timestamp: new Date().toISOString(),
    });
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
