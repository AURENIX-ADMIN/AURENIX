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

// Mock data - in production this would come from API
const metrics = [
  {
    label: 'Horas Ahorradas',
    value: '47.5',
    unit: 'horas',
    change: '+12.3%',
    trend: 'up',
    period: 'este mes',
    icon: Clock,
    color: 'hsl(45, 93%, 47%)',
  },
  {
    label: 'Tareas Completadas',
    value: '284',
    unit: 'tareas',
    change: '+8.2%',
    trend: 'up',
    period: 'este mes',
    icon: CheckCircle2,
    color: 'hsl(141, 71%, 48%)',
  },
  {
    label: 'Agentes Activos',
    value: '3',
    unit: 'de 5',
    change: '',
    trend: 'neutral',
    period: 'disponibles',
    icon: Bot,
    color: 'hsl(217, 91%, 60%)',
  },
  {
    label: 'ROI Generado',
    value: '$4,720',
    unit: '',
    change: '+23.1%',
    trend: 'up',
    period: 'este mes',
    icon: TrendingUp,
    color: 'hsl(20, 97%, 57%)',
  },
];

const recentActivity = [
  {
    id: 1,
    agent: 'Lead Hunter',
    action: 'Encontrado 12 nuevos leads cualificados',
    time: 'Hace 5 min',
    status: 'success',
  },
  {
    id: 2,
    agent: 'Email Assistant',
    action: 'Borrador pendiente de aprobación',
    time: 'Hace 15 min',
    status: 'pending',
  },
  {
    id: 3,
    agent: 'Meeting Scheduler',
    action: 'Reunión programada con Cliente ABC',
    time: 'Hace 1 hora',
    status: 'success',
  },
  {
    id: 4,
    agent: 'Lead Hunter',
    action: 'Escaneo diario completado',
    time: 'Hace 2 horas',
    status: 'success',
  },
];

const agents = [
  {
    id: 'lead-hunter',
    name: 'Lead Hunter',
    description: 'Busca y califica leads automáticamente',
    status: 'active',
    lastRun: 'Hace 5 min',
    metrics: { leads: 47, qualified: 12 },
  },
  {
    id: 'email-assistant',
    name: 'Email Assistant',
    description: 'Procesa y responde emails',
    status: 'active',
    lastRun: 'Hace 15 min',
    metrics: { processed: 23, drafts: 3 },
  },
  {
    id: 'meeting-scheduler',
    name: 'Meeting Scheduler',
    description: 'Gestiona tu calendario',
    status: 'paused',
    lastRun: 'Hace 1 hora',
    metrics: { scheduled: 5, pending: 2 },
  },
];

export default function DashboardOverview() {
  const [data, setData] = useState(metrics);
  const [healthData, setHealthData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const [metricsRes, healthRes] = await Promise.all([
          fetch('/api/metrics'),
          fetch('/api/health')
        ]);
        
        const metricsJson = await metricsRes.json();
        const healthJson = await healthRes.json();

        if (Array.isArray(metricsJson)) {
          const enriched = metricsJson.map(m => ({
            ...m,
            icon: metrics.find(mock => mock.label === m.label)?.icon || Activity
          }));
          setData(enriched);
        }

        if (healthJson && healthJson.s1_vps_guard) {
          setHealthData(healthJson);
        }
      } catch (e) {
        console.error('Fetch error:', e);
      } finally {
        setIsLoading(false);
      }
    }
    fetchDashboardData();
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
        <div className="p-5 rounded-xl bg-card border border-border flex items-center justify-between hover:border-[hsl(45,93%,47%)]/30 transition-all group">
          <div className="flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-green-500/10 flex items-center justify-center">
              <Server className="h-5 w-5 text-green-500" />
            </div>
            <div>
              <h3 className="font-medium">S1: VPS Guard</h3>
              <p className="text-sm text-muted-foreground">Sistema de Infraestructura</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {!healthData ? (
              <span className="text-sm font-medium text-muted-foreground">Verificando...</span>
            ) : healthData.s1_vps_guard.status === 'operational' ? (
              <>
                <span className="text-sm font-medium text-green-500">Operativo</span>
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              </>
            ) : (
               <>
                <span className="text-sm font-medium text-red-500">Alerta</span>
                <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
              </>
            )}
          </div>
        </div>

        <div className="p-5 rounded-xl bg-card border border-border flex items-center justify-between hover:border-[hsl(45,93%,47%)]/30 transition-all group">
          <div className="flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-green-500/10 flex items-center justify-center">
              <ShieldAlert className="h-5 w-5 text-green-500" />
            </div>
            <div>
              <h3 className="font-medium">S2: Workflow Sentinel</h3>
              <p className="text-sm text-muted-foreground">Calidad de Automatizaciones</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {!healthData ? (
              <span className="text-sm font-medium text-muted-foreground">Verificando...</span>
            ) : healthData.s2_workflow_sentinel.status === 'operational' ? (
              <>
                <span className="text-sm font-medium text-green-500">Sin Alertas</span>
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              </>
            ) : (
               <>
                <span className="text-sm font-medium text-yellow-500">Revisión Requerida</span>
                <div className="h-2 w-2 rounded-full bg-yellow-500 animate-pulse" />
              </>
            )}
          </div>
        </div>
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
                        <h3 className="font-medium">{agent.name}</h3>
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                            agent.status === 'active'
                              ? 'bg-green-500/10 text-green-500'
                              : 'bg-yellow-500/10 text-yellow-500'
                          }`}
                        >
                          <span
                            className={`h-1.5 w-1.5 rounded-full ${
                              agent.status === 'active' ? 'bg-green-500' : 'bg-yellow-500'
                            }`}
                          />
                          {agent.status === 'active' ? 'Activo' : 'Pausado'}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">{agent.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">{agent.lastRun}</span>
                    <button
                      className={`p-2 rounded-lg transition-colors ${
                        agent.status === 'active'
                          ? 'bg-secondary text-foreground hover:bg-secondary/80'
                          : 'bg-[hsl(45,93%,47%)] text-black hover:bg-[hsl(45,93%,47%)]/90'
                      }`}
                    >
                      {agent.status === 'active' ? (
                        <Activity className="h-4 w-4" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </button>
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

          {/* Quick Stats */}
          <div className="p-4 rounded-xl bg-gradient-to-br from-[hsl(45,93%,47%)]/10 to-[hsl(20,97%,57%)]/10 border border-[hsl(45,93%,47%)]/20">
            <h3 className="font-medium mb-3">Esta Semana</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Tiempo ahorrado</span>
                <span className="font-medium">12.5 horas</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Tareas automatizadas</span>
                <span className="font-medium">67</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Aprobaciones pendientes</span>
                <span className="font-medium text-yellow-500">3</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
