'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  Bot,
  Plus,
  Play,
  Pause,
  Settings,
  MoreVertical,
  Search,
  Filter,
  Clock,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
} from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  description: string;
  type: 'lead_hunter' | 'email_assistant' | 'meeting_scheduler' | 'custom';
  status: 'active' | 'paused' | 'error';
  lastRun: string;
  nextRun?: string;
  stats: {
    tasksCompleted: number;
    successRate: number;
    timeSaved: string;
  };
  config?: Record<string, unknown>;
}

const mockAgents: Agent[] = [
  {
    id: 'lead-hunter-1',
    name: 'Lead Hunter Pro',
    description: 'Busca leads en LinkedIn y webs de empresas, los enriquece y califica automáticamente.',
    type: 'lead_hunter',
    status: 'active',
    lastRun: 'Hace 5 min',
    nextRun: 'En 55 min',
    stats: {
      tasksCompleted: 1247,
      successRate: 94,
      timeSaved: '32h',
    },
  },
  {
    id: 'email-assistant-1',
    name: 'Email Assistant',
    description: 'Procesa emails entrantes, clasifica por urgencia y genera borradores de respuesta.',
    type: 'email_assistant',
    status: 'active',
    lastRun: 'Hace 15 min',
    stats: {
      tasksCompleted: 892,
      successRate: 98,
      timeSaved: '18h',
    },
  },
  {
    id: 'meeting-scheduler-1',
    name: 'Meeting Scheduler',
    description: 'Negocia horarios de reuniones y gestiona tu calendario automáticamente.',
    type: 'meeting_scheduler',
    status: 'paused',
    lastRun: 'Hace 2 días',
    stats: {
      tasksCompleted: 156,
      successRate: 87,
      timeSaved: '8h',
    },
  },
];

const agentTypeLabels: Record<Agent['type'], string> = {
  lead_hunter: 'Generación de Leads',
  email_assistant: 'Email',
  meeting_scheduler: 'Calendario',
  custom: 'Personalizado',
};

const statusConfig = {
  active: {
    label: 'Activo',
    color: 'bg-green-500',
    bgColor: 'bg-green-500/10',
    textColor: 'text-green-500',
  },
  paused: {
    label: 'Pausado',
    color: 'bg-yellow-500',
    bgColor: 'bg-yellow-500/10',
    textColor: 'text-yellow-500',
  },
  error: {
    label: 'Error',
    color: 'bg-red-500',
    bgColor: 'bg-red-500/10',
    textColor: 'text-red-500',
  },
};

export default function AgentsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | Agent['status']>('all');

  const filteredAgents = mockAgents.filter((agent) => {
    const matchesSearch =
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterStatus === 'all' || agent.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">AI Agents</h1>
          <p className="text-muted-foreground mt-1">
            Gestiona y monitorea tus agentes de automatización
          </p>
        </div>
        <Link
          href="/dashboard/agents/new"
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[hsl(45,93%,47%)] text-black font-medium hover:bg-[hsl(45,93%,47%)]/90 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Nuevo Agente
        </Link>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Buscar agentes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-10 rounded-lg bg-card border border-border pl-10 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-[hsl(45,93%,47%)]/30 focus:border-[hsl(45,93%,47%)]/50"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as typeof filterStatus)}
            className="h-10 px-3 rounded-lg bg-card border border-border text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(45,93%,47%)]/30"
          >
            <option value="all">Todos los estados</option>
            <option value="active">Activos</option>
            <option value="paused">Pausados</option>
            <option value="error">Con errores</option>
          </select>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredAgents.map((agent, index) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-5 rounded-xl bg-card border border-border hover:border-[hsl(45,93%,47%)]/30 transition-all group"
          >
            {/* Agent Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-[hsl(45,93%,47%)]/20 to-[hsl(20,97%,57%)]/20 flex items-center justify-center">
                  <Bot className="h-6 w-6 text-[hsl(45,93%,47%)]" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{agent.name}</h3>
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                        statusConfig[agent.status].bgColor
                      } ${statusConfig[agent.status].textColor}`}
                    >
                      <span className={`h-1.5 w-1.5 rounded-full ${statusConfig[agent.status].color}`} />
                      {statusConfig[agent.status].label}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {agentTypeLabels[agent.type]}
                  </p>
                </div>
              </div>
              <button className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors">
                <MoreVertical className="h-4 w-4" />
              </button>
            </div>

            {/* Description */}
            <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
              {agent.description}
            </p>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div className="p-3 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span className="text-xs">Completadas</span>
                </div>
                <span className="text-lg font-semibold">{agent.stats.tasksCompleted}</span>
              </div>
              <div className="p-3 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                  <TrendingUp className="h-3.5 w-3.5" />
                  <span className="text-xs">Éxito</span>
                </div>
                <span className="text-lg font-semibold">{agent.stats.successRate}%</span>
              </div>
              <div className="p-3 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                  <Clock className="h-3.5 w-3.5" />
                  <span className="text-xs">Ahorrado</span>
                </div>
                <span className="text-lg font-semibold">{agent.stats.timeSaved}</span>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-4 border-t border-border">
              <div className="text-xs text-muted-foreground">
                <span>Última ejecución: {agent.lastRun}</span>
                {agent.nextRun && (
                  <>
                    <span className="mx-1.5">·</span>
                    <span>Próxima: {agent.nextRun}</span>
                  </>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Link
                  href={`/dashboard/agents/${agent.id}`}
                  className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
                >
                  <Settings className="h-4 w-4" />
                </Link>
                <button
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    agent.status === 'active'
                      ? 'bg-secondary text-foreground hover:bg-secondary/80'
                      : 'bg-[hsl(45,93%,47%)] text-black hover:bg-[hsl(45,93%,47%)]/90'
                  }`}
                >
                  {agent.status === 'active' ? (
                    <>
                      <Pause className="h-3.5 w-3.5" />
                      Pausar
                    </>
                  ) : (
                    <>
                      <Play className="h-3.5 w-3.5" />
                      Iniciar
                    </>
                  )}
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {filteredAgents.length === 0 && (
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-secondary mb-4">
            <Bot className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-2">No se encontraron agentes</h3>
          <p className="text-muted-foreground mb-4">
            {searchQuery
              ? 'Intenta con otros términos de búsqueda'
              : 'Crea tu primer agente para empezar a automatizar'}
          </p>
          <Link
            href="/dashboard/agents/new"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[hsl(45,93%,47%)] text-black font-medium hover:bg-[hsl(45,93%,47%)]/90 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Crear Agente
          </Link>
        </div>
      )}
    </div>
  );
}
