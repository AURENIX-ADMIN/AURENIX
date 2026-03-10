'use client';

import { useState, useEffect } from 'react';
import {
  Server,
  ShieldAlert,
  Factory,
  Eye,
  CheckCircle2,
  AlertCircle,
  XCircle,
  HelpCircle,
  RefreshCw,
} from 'lucide-react';

interface SystemAgent {
  id: string;
  name: string;
  description: string;
  workflowId: string | null;
  active: boolean;
  status: string;
  updatedAt: string | null;
}

interface HealthData {
  status: string;
  errorCount24h: number;
  successCount24h: number;
  message: string;
  lastCheck: string;
}

const SYSTEM_ICONS: Record<string, typeof Server> = {
  s1: Server,
  s2: ShieldAlert,
  s3: Factory,
  s5: Eye,
};

const STATUS_CONFIG: Record<string, { color: string; label: string; Icon: typeof CheckCircle2 }> = {
  operational: { color: 'text-green-500', label: 'Operativo', Icon: CheckCircle2 },
  degraded: { color: 'text-yellow-500', label: 'Degradado', Icon: AlertCircle },
  alert: { color: 'text-red-500', label: 'Alerta', Icon: AlertCircle },
  down: { color: 'text-red-600', label: 'Caido', Icon: XCircle },
  unknown: { color: 'text-gray-500', label: 'Desconocido', Icon: HelpCircle },
};

export default function SystemsPage() {
  const [agents, setAgents] = useState<SystemAgent[]>([]);
  const [health, setHealth] = useState<Record<string, HealthData>>({});
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  async function fetchData() {
    setLoading(true);
    try {
      const [agentsRes, healthRes] = await Promise.all([
        fetch('/api/agents/status'),
        fetch('/api/health'),
      ]);

      if (agentsRes.ok) {
        const data = await agentsRes.json();
        setAgents(data.agents || []);
      }

      if (healthRes.ok) {
        const data = await healthRes.json();
        const { timestamp, ...systems } = data;
        setHealth(systems);
        setLastUpdate(timestamp);
      }
    } catch (e) {
      console.error('Systems fetch error:', e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();

    // SSE for live updates
    const es = new EventSource('/api/health/stream');
    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.timestamp) {
          const { timestamp, ...systems } = data;
          setHealth(systems);
          setLastUpdate(timestamp);
        }
      } catch { /* ignore parse errors */ }
    };

    return () => es.close();
  }, []);

  function timeAgo(dateStr: string | null): string {
    if (!dateStr) return 'N/A';
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60_000);
    if (mins < 1) return 'Justo ahora';
    if (mins < 60) return `Hace ${mins}min`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `Hace ${hours}h`;
    return `Hace ${Math.floor(hours / 24)}d`;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Sistemas Core</h1>
          <p className="text-muted-foreground mt-1">
            Estado en tiempo real de los sistemas S1-S5
          </p>
        </div>
        <div className="flex items-center gap-3">
          {lastUpdate && (
            <span className="text-xs text-muted-foreground">
              Actualizado: {timeAgo(lastUpdate)}
            </span>
          )}
          <button
            onClick={fetchData}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors text-sm"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refrescar
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {agents.map((agent) => {
          const Icon = SYSTEM_ICONS[agent.id] || Server;
          const healthKey = `${agent.id}_${agent.name.toLowerCase().replace(/\s+/g, '_')}`;
          const systemHealth = health[healthKey] || health[agent.id] || null;
          const statusKey = systemHealth?.status || (agent.active ? 'operational' : 'unknown');
          const config = STATUS_CONFIG[statusKey] || STATUS_CONFIG.unknown;
          const StatusIcon = config.Icon;

          return (
            <div
              key={agent.id}
              className="p-5 rounded-xl bg-card border border-border hover:border-border/80 transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-[hsl(45,93%,47%)]/10 flex items-center justify-center">
                    <Icon className="h-5 w-5 text-[hsl(45,93%,47%)]" />
                  </div>
                  <div>
                    <h3 className="font-medium">{agent.id.toUpperCase()}: {agent.name}</h3>
                    <p className="text-sm text-muted-foreground">{agent.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusIcon className={`h-4 w-4 ${config.color}`} />
                  <span className={`text-sm font-medium ${config.color}`}>{config.label}</span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-2 rounded-lg bg-secondary/50">
                  <p className="text-lg font-bold text-green-500">{systemHealth?.successCount24h ?? '-'}</p>
                  <p className="text-xs text-muted-foreground">Exitos 24h</p>
                </div>
                <div className="p-2 rounded-lg bg-secondary/50">
                  <p className="text-lg font-bold text-red-500">{systemHealth?.errorCount24h ?? '-'}</p>
                  <p className="text-xs text-muted-foreground">Errores 24h</p>
                </div>
                <div className="p-2 rounded-lg bg-secondary/50">
                  <p className="text-lg font-bold">{agent.active ? 'ON' : 'OFF'}</p>
                  <p className="text-xs text-muted-foreground">Workflow</p>
                </div>
              </div>

              <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                <span>Ultima check: {timeAgo(systemHealth?.lastCheck || agent.updatedAt)}</span>
                {agent.workflowId && (
                  <span className="font-mono">{agent.workflowId.substring(0, 8)}...</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
