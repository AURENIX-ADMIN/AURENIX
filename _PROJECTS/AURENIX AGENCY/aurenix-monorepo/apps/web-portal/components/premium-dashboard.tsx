"use client"

import { motion } from "framer-motion"
import { TrendingUp, Clock, DollarSign, Zap } from "lucide-react"

interface MetricCardProps {
  title: string
  value: string | number
  subValue: string
  icon: React.ReactNode
  delay: number
}

function MetricCard({ title, value, subValue, icon, delay }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl transition-all hover:bg-white/10"
    >
      <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-primary/10 blur-3xl" />
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <h3 className="mt-2 text-3xl font-bold tracking-tight text-white">{value}</h3>
          <p className="mt-1 text-xs text-primary/80">{subValue}</p>
        </div>
        <div className="rounded-xl bg-white/5 p-3 text-primary">
          {icon}
        </div>
      </div>
    </motion.div>
  )
}

import { RealTimeROI } from "./real-time-roi"
import { ActivityFeed } from "./activity-feed"
import { ApprovalCard } from "./approval-card"

export function PremiumDashboard() {
  return (
    <div className="space-y-10">
      {/* Real-Time ROI Section */}
      <section>
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white tracking-tight">Impacto de Negocio</h2>
          <p className="text-slate-400">Visualización en tiempo real del ahorro y retorno generado por Aurenix.</p>
        </div>
        <RealTimeROI />
      </section>

      {/* Main Grid */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Quick Stats & Controls */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <MetricCard
              title="Velocidad de Escalamiento"
              value="4.2x"
              subValue="Workflows autónomos activos"
              icon={<TrendingUp className="h-6 w-6" />}
              delay={0.1}
            />
            <MetricCard
              title="Boost de Eficiencia"
              value="85%"
              subValue="+5% este mes"
              icon={<Zap className="h-6 w-6" />}
              delay={0.2}
            />
          </div>
          
          {/* Placeholder for future charts */}
          <div className="h-80 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl flex items-center justify-center">
            <p className="text-slate-500 font-medium">Gráfico de Tendencia de Ahorro (Próximamente)</p>
          </div>
        </div>

        {/* Audit Logs / Activity Feed */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white tracking-tight">Registro de Auditoría</h2>
            <span className="text-[10px] uppercase font-bold text-cyan-400 border border-cyan-400/30 px-2 py-0.5 rounded">Inmutable</span>
          </div>
          <ActivityFeed />
        </div>
      </div>

      {/* HITL Section */}
      <section className="mt-12">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white tracking-tight">Centro de Control de Decisiones</h2>
          <p className="text-slate-400">Revisión y aprobación humana para acciones de IA de alta sensibilidad.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <ApprovalCard 
             workflowId="audit-shield-123"
             title="Anomalía Detectada: Factura Provedor X"
             description="AuditShield ha detectado una discrepancia del 15% en los cargos."
             content="DETALLES DE LA AUDITORÍA:\n- Vendor: TechGlobal Inc.\n- Total: 12,450.00€\n- Expected: 10,800.00€\n\nAI RECOMMENDATION: Rechazar y solicitar desglose."
          />
          <ApprovalCard 
             workflowId="lead-hunter-456"
             title="Lead de Alta Prioridad: Acme Corp"
             description="LeadHunter ha encontrado un perfil con 95% de coincidencia."
             content="PERFIL DEL LEAD:\n- Name: Carlos Rodriguez\n- Title: CTO @ Acme Corp\n- Pain Point: Escalabilidad de infraestructura AI.\n\nAI RECOMMENDATION: Enviar propuesta de auditoría gratuita."
          />
        </div>
      </section>
    </div>
  )
}
