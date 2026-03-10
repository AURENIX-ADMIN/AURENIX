'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  Clock,
  Bot,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  CheckCircle2,
  AlertCircle,
  Play,
  Server,
  ShieldAlert,
} from 'lucide-react';
import Link from 'next/link';

const METRIC_ICONS: Record<string, typeof Clock> = {
  'Ejecuciones 24h': Zap,
  'Workflows Activos': Bot,
  'Workflows Totales': Activity,
  'Tasa de Exito': TrendingUp,
};

const METRIC_COLORS: Record<string, string> = {
  'Ejecuciones 24h': 'hsl(45, 93%, 47%)',
  'Workflows Activos': 'hsl(217, 91%, 60%)',
  'Workflows Totales': 'hsl(141, 71%, 48%)',
  'Tasa de Exito': 'hsl(20, 97%, 57%)',
};

interface AgentData {
  id: string;
  name: string;
  description: string;
  active: boolean;
  status: string;
  updatedAt: string | null;
}

function timeAgo(dateStr: string | null | undefined): string {
  if (!dateStr) return 'N/A';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'Justo ahora';
  if (mins < 60) return `Hace ${mins}min`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `Hace ${hours}h`;
  return `Hace ${Math.floor(hours / 24)}d`;
}

export default function DashboardOverview() {
  const [data, setData] = useState<Array<{ label: string; value: string; unit: string; change: string; trend: string; period: string; icon: typeof Clock; color: string }>>([]);
  const [healthData, setHealthData] = useState<Record<string, { status: string; errorCount24h: number; successCount24h: number; message: string }> | null>(null);
  const [agents, setAgents] = useState<AgentData[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const [metricsRes, healthRes, agentsRes] = await Promise.all([
          fetch('/api/metrics'),
          fetch('/api/health'),
          fetch('/api/agents/status'),
        ]);

        const metricsJson = await metricsRes.json();
        const healthJson = await healthRes.json();

        if (Array.isArray(metricsJson)) {
          const enriched = metricsJson.map((m: { label: string; value: string; unit: string; change: string; trend: string; period: string }) => ({
            ...m,
            icon: METRIC_ICONS[m.label] || Activity,
            color: METRIC_COLORS[m.label] || 'hsl(45, 93%, 47%)',
          }));
          setData(enriched);
        }

        if (healthJson && healthJson.timestamp) {
          const { timestamp, ...systems } = healthJson;
          setHealthData(systems);
        }

        if (agentsRes.ok) {
          const agentsJson = await agentsRes.json();
          setAgents(agentsJson.agents || []);
        }
      } catch (e) {
        console.error('Fetch error:', e);
      } finally {
        setIsLoading(false);
      }
    }
    fetchDashboardData();

    // SSE for live health updates
    const es = new EventSource('/api/health/stream');
    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.timestamp) {
          const { timestamp, ...systems } = data;
          setHealthData(systems);
        }
      } catch { /* ignore */ }
    };

    return () => es.close();
  }, []);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            {isLoading ? 'Cargando datos...' : 'Bienvenido de vuelta. Aquí está el resumen de tu automatización.'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard/agents/new"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[hsl(45,93%,47%)] text-black font-medium hover:bg-[hsl(45,93%,47%)]/90 transition-colors"
          >
            <Zap className="h-4 w-4" />
            Nuevo Agente
          </Link>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {data.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-5 rounded-xl bg-card border border-border hover:border-border/80 transition-all group ${isLoading ? 'animate-pulse' : ''}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div
                  className="p-2.5 rounded-lg"
                  style={{ backgroundColor: `${metric.color}15` }}
                >
                  <Icon className="h-5 w-5" style={{ color: metric.color }} />
                </div>
                {metric.change && (
                  <div
                    className={`flex items-center gap-1 text-sm font-medium ${
                      metric.trend === 'up' ? 'text-green-500' : 'text-red-500'
                    }`}
                  >
                    {metric.trend === 'up' ? (
                      <ArrowUpRight className="h-4 w-4" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4" />
                    )}
                    {metric.change}
                  </div>
                )}
              </div>
              <div>
                <div className="flex items-baseline gap-1.5">
                  <span className="text-2xl font-bold">{metric.value}</span>
                  <span className="text-muted-foreground text-sm">{metric.unit}</span>
                </div>
                <p className="text-sm text-muted-foreground mt-1">{metric.label}</p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* System Health Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { key: 's1_vps_guard', label: 'S1: VPS Guard', desc: 'Monitor de Infraestructura', Icon: Server },
          { key: 's2_workflow_sentinel', label: 'S2: Workflow Sentinel', desc: 'QA de Automatizaciones', Icon: ShieldAlert },
        ].map(({ key, label, desc, Icon: SysIcon }) => {
          const sys = healthData?.[key];
          const statusColor = !sys ? 'text-muted-foreground' :
            sys.status === 'operational' ? 'text-green-500' :
            sys.status === 'degraded' ? 'text-yellow-500' :
            sys.status === 'alert' || sys.status === 'down' ? 'text-red-500' : 'text-gray-500';
          const dotColor = statusColor.replace('text-', 'bg-');
          const statusLabel = !sys ? 'Verificando...' :
            sys.status === 'operational' ? 'Operativo' :
            sys.status === 'degraded' ? 'Degradado' :
            sys.status === 'alert' ? 'Alerta' :
            sys.status === 'down' ? 'Caido' : 'Desconocido';

          return (
            <div key={key} className="p-5 rounded-xl bg-card border border-border flex items-center justify-between hover:border-[hsl(45,93%,47%)]/30 transition-all group">
              <div className="flex items-center gap-4">
                <div className={`h-10 w-10 rounded-lg ${sys?.status === 'operational' ? 'bg-green-500/10' : 'bg-yellow-500/10'} flex items-center justify-center`}>
                  <SysIcon className={`h-5 w-5 ${statusColor}`} />
                </div>
                <div>
                  <h3 className="font-medium">{label}</h3>
                  <p className="text-sm text-muted-foreground">{desc}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-sm font-medium ${statusColor}`}>{statusLabel}</span>
                <div className={`h-2 w-2 rounded-full ${dotColor} animate-pulse`} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        {/* Agents Section */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Tus Agentes</h2>
            <Link
              href="/dashboard/agents"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Ver todos →
            </Link>
          </div>
          <div className="space-y-3">
            {agents.length === 0 && !isLoading && (
              <div className="p-4 rounded-xl bg-card border border-border text-center text-muted-foreground">
                No se encontraron agentes. Verifica la conexion con n8n.
              </div>
            )}
            {agents.map((agent, index) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="p-4 rounded-xl bg-card border border-border hover:border-[hsl(45,93%,47%)]/30 transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-[hsl(45,93%,47%)]/20 to-[hsl(20,97%,57%)]/20 flex items-center justify-center">
                      <Bot className="h-5 w-5 text-[hsl(45,93%,47%)]" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium">{agent.id.toUpperCase()}: {agent.name}</h3>
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                            agent.active
                              ? 'bg-green-500/10 text-green-500'
                              : agent.status === 'not_found'
                              ? 'bg-red-500/10 text-red-500'
                              : 'bg-yellow-500/10 text-yellow-500'
                          }`}
                        >
                          <span
                            className={`h-1.5 w-1.5 rounded-full ${
                              agent.active ? 'bg-green-500' : agent.status === 'not_found' ? 'bg-red-500' : 'bg-yellow-500'
                            }`}
                          />
                          {agent.active ? 'Activo' : agent.status === 'not_found' ? 'No encontrado' : 'Pausado'}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">{agent.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">{timeAgo(agent.updatedAt)}</span>
                    <div
                      className={`p-2 rounded-lg ${
                        agent.active
                          ? 'bg-secondary text-foreground'
                          : 'bg-secondary/50 text-muted-foreground'
                      }`}
                    >
                      {agent.active ? (
                        <Activity className="h-4 w-4" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Activity Feed */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Actividad Reciente</h2>
            <Link
              href="/dashboard/activity"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Ver todo →
            </Link>
          </div>
          <div className="p-4 rounded-xl bg-card border border-border space-y-4">
            {recentActivity.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="flex items-start gap-3"
              >
                <div
                  className={`mt-1 h-2 w-2 rounded-full shrink-0 ${
                    item.status === 'success'
                      ? 'bg-green-500'
                      : item.status === 'pending'
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm">
                    <span className="font-medium text-[hsl(45,93%,47%)]">{item.agent}</span>
                    {' · '}
                    <span className="text-muted-foreground">{item.action}</span>
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5">{item.time}</p>
                </div>
                {item.status === 'pending' && (
                  <button className="text-xs px-2 py-1 rounded bg-[hsl(45,93%,47%)]/10 text-[hsl(45,93%,47%)] hover:bg-[hsl(45,93%,47%)]/20 transition-colors">
                    Revisar
                  </button>
                )}
              </motion.div>
            ))}
          </div>

          {/* System Links */}
          <div className="p-4 rounded-xl bg-gradient-to-br from-[hsl(45,93%,47%)]/10 to-[hsl(20,97%,57%)]/10 border border-[hsl(45,93%,47%)]/20">
            <h3 className="font-medium mb-3">Acceso Rapido</h3>
            <div className="space-y-2">
              <Link href="/dashboard/systems" className="flex items-center justify-between text-sm hover:text-[hsl(45,93%,47%)] transition-colors">
                <span className="text-muted-foreground">Sistemas Core (S1-S5)</span>
                <span className="font-medium">Ver estado →</span>
              </Link>
              <a href="https://n8n.aurenix.cloud" target="_blank" rel="noopener noreferrer" className="flex items-center justify-between text-sm hover:text-[hsl(45,93%,47%)] transition-colors">
                <span className="text-muted-foreground">n8n Panel</span>
                <span className="font-medium">Abrir →</span>
              </a>
              <a href="https://files.aurenix.cloud" target="_blank" rel="noopener noreferrer" className="flex items-center justify-between text-sm hover:text-[hsl(45,93%,47%)] transition-colors">
                <span className="text-muted-foreground">Filebrowser</span>
                <span className="font-medium">Abrir →</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
