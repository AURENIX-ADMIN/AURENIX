import { NextResponse } from 'next/server';

const N8N_API_URL = process.env.N8N_API_URL || 'https://n8n.aurenix.cloud';
const N8N_API_KEY = process.env.N8N_API_KEY || '';

export async function GET() {
  let totalWorkflows = 42;
  let activeWorkflows = 3;
  let totalExecutions = 0;
  let errorCount = 0;

  if (N8N_API_KEY) {
    try {
      // Get workflow count
      const wfRes = await fetch(`${N8N_API_URL}/api/v1/workflows?limit=250`, {
        headers: { 'X-N8N-API-KEY': N8N_API_KEY },
        next: { revalidate: 300 },
      });
      if (wfRes.ok) {
        const wfData = await wfRes.json();
        totalWorkflows = wfData.data?.length || totalWorkflows;
        activeWorkflows = wfData.data?.filter((w: any) => w.active).length || activeWorkflows;
      }

      // Get recent executions (last 24h)
      const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
      const execRes = await fetch(
        `${N8N_API_URL}/api/v1/executions?limit=250&startedAfter=${since}`,
        {
          headers: { 'X-N8N-API-KEY': N8N_API_KEY },
          next: { revalidate: 300 },
        }
      );
      if (execRes.ok) {
        const execData = await execRes.json();
        const executions = execData.data || [];
        totalExecutions = executions.length;
        errorCount = executions.filter((e: any) => e.status === 'error').length;
      }
    } catch {
      // Fall through to defaults
    }
  }

  const metrics = [
    {
      label: 'Ejecuciones 24h',
      value: String(totalExecutions),
      unit: 'ejecuciones',
      change: errorCount > 0 ? `${errorCount} errores` : 'Sin errores',
      trend: errorCount > 0 ? 'down' : 'up',
      period: 'ultimas 24h',
    },
    {
      label: 'Workflows Activos',
      value: String(activeWorkflows),
      unit: `de ${totalWorkflows}`,
      change: '',
      trend: 'neutral',
      period: 'S1-S3 activos',
    },
    {
      label: 'Workflows Totales',
      value: String(totalWorkflows),
      unit: 'total',
      change: '',
      trend: 'neutral',
      period: 'en n8n',
    },
    {
      label: 'Tasa de Exito',
      value: totalExecutions > 0
        ? `${Math.round(((totalExecutions - errorCount) / totalExecutions) * 100)}%`
        : 'N/A',
      unit: '',
      change: '',
      trend: errorCount === 0 ? 'up' : 'down',
      period: 'ultimas 24h',
    },
  ];

  return NextResponse.json(metrics);
}
