'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  Filter,
  Search,
  CheckCircle2,
  Clock,
  AlertCircle,
  ArrowRight,
  Download,
  Bot,
  Mail,
  Calendar,
  Zap,
} from 'lucide-react';

interface ActivityItem {
  id: string;
  agent: string;
  action: string;
  details: string;
  time: string;
  status: 'success' | 'pending' | 'error';
  type: 'execution' | 'approval' | 'system';
  icon: React.ComponentType<{ className?: string }>;
}

const mockActivity: ActivityItem[] = [
  {
    id: '1',
    agent: 'Lead Hunter Pro',
    action: 'Cualificación completada',
    details: '12 leads movidos a CRM HubSpot con score > 85',
    time: 'Hace 5 min',
    status: 'success',
    type: 'execution',
    icon: Zap,
  },
  {
    id: '2',
    agent: 'Email Assistant',
    action: 'Aprobación requerida',
    details: 'Borrador de respuesta para "Inversiones Globales" listo para revisión',
    time: 'Hace 15 min',
    status: 'pending',
    type: 'approval',
    icon: Mail,
  },
  {
    id: '3',
    agent: 'Meeting Scheduler',
    action: 'Reunión confirmada',
    details: 'Demo técnica programada con Juan Pérez para el 15/01 a las 10:00',
    time: 'Hace 1 hora',
    status: 'success',
    type: 'execution',
    icon: Calendar,
  },
  {
    id: '4',
    agent: 'System',
    action: 'Integración sincronizada',
    details: 'Sincronización con Google Calendar completada con éxito',
    time: 'Hace 3 horas',
    status: 'success',
    type: 'system',
    icon: Activity,
  },
  {
    id: '5',
    agent: 'Lead Hunter Pro',
    action: 'Error de conexión',
    details: 'Fallo al autenticar en LinkedIn. Se requiere intervención manual.',
    time: 'Hace 5 horas',
    status: 'error',
    type: 'system',
    icon: AlertCircle,
  },
];

const statusStyles = {
  success: {
    icon: CheckCircle2,
    color: 'text-green-500',
    bg: 'bg-green-500/10',
    border: 'border-green-500/20',
  },
  pending: {
    icon: Clock,
    color: 'text-yellow-500',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/20',
  },
  error: {
    icon: AlertCircle,
    color: 'text-red-500',
    bg: 'bg-red-500/10',
    border: 'border-red-500/20',
  },
};

export default function ActivityPage() {
  const [filter, setFilter] = useState<'all' | 'execution' | 'approval' | 'system'>('all');

  const filteredActivity = mockActivity.filter(
    (item) => filter === 'all' || item.type === filter
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Actividad</h1>
          <p className="text-muted-foreground mt-1">
            Historial detallado de todas las acciones realizadas por tus agentes
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-secondary border border-border text-sm font-medium hover:bg-secondary/80 transition-colors">
          <Download className="h-4 w-4" />
          Exportar Log
        </button>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Buscar en el historial..."
            className="w-full h-11 rounded-xl bg-card border border-border pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
        </div>
        <div className="flex items-center gap-2 bg-card border border-border p-1 rounded-xl">
          {[
            { id: 'all', label: 'Todo' },
            { id: 'execution', label: 'Ejecuciones' },
            { id: 'approval', label: 'Aprobaciones' },
            { id: 'system', label: 'Sistema' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id as any)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === tab.id
                  ? 'bg-secondary text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Activity Timeline */}
      <div className="relative space-y-4">
        {/* Timeline line */}
        <div className="absolute left-[27px] top-2 bottom-2 w-px bg-border hidden sm:block" />

        {filteredActivity.map((item, index) => {
          const StatusIcon = statusStyles[item.status].icon;
          const AgentIcon = item.icon;

          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="relative flex flex-col sm:flex-row gap-4 items-start group"
            >
              {/* Agent Icon */}
              <div className="z-10 flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-card border border-border group-hover:border-primary/50 transition-colors shadow-sm">
                <AgentIcon className="h-6 w-6 text-primary" />
              </div>

              {/* Content Card */}
              <div className="flex-1 w-full bg-card border border-border rounded-2xl p-4 sm:p-5 hover:border-border/80 transition-all shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-foreground">{item.agent}</span>
                    <span className="text-muted-foreground">·</span>
                    <span className="text-sm font-medium">{item.action}</span>
                  </div>
                  <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusStyles[item.status].bg} ${statusStyles[item.status].color} ${statusStyles[item.status].border} border`}>
                    <StatusIcon className="h-3 w-3" />
                    {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                  </div>
                </div>

                <p className="text-sm text-muted-foreground mb-4">
                  {item.details}
                </p>

                <div className="flex item-center justify-between">
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {item.time}
                  </span>
                  
                  {item.status === 'pending' && (
                    <button className="flex items-center gap-1 text-xs font-bold text-primary hover:underline group/btn">
                      Revisar Ahora
                      <ArrowRight className="h-3 w-3 transition-transform group-hover/btn:translate-x-1" />
                    </button>
                  )}
                  
                  {item.status === 'success' && item.type === 'execution' && (
                    <button className="text-xs text-muted-foreground hover:text-foreground transition-colors">
                      Ver Detalles
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Load More */}
      <div className="flex justify-center pt-4">
        <button className="text-sm text-muted-foreground hover:text-foreground py-2 px-4 rounded-lg border border-border hover:bg-secondary transition-all">
          Cargar más actividad
        </button>
      </div>
    </div>
  );
}
