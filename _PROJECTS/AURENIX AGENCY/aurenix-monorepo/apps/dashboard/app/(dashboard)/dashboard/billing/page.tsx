'use client';

import { motion } from 'framer-motion';
import {
  CreditCard,
  Zap,
  Check,
  TrendingUp,
  History,
  Info,
  ExternalLink,
  ArrowUpRight,
  Download,
} from 'lucide-react';

export default function BillingPage() {
  const currentPlan = {
    name: 'Plan Pro',
    price: '$99/mes',
    status: 'Active',
    nextBilling: '10 de Febrero, 2026',
    features: [
      'Agentes IA ilimitados',
      'Acceso a todas las herramientas',
      'Soporte prioritario 24/7',
      'API ilimitada',
    ],
  };

  const usage = {
    creditsUsed: 4250,
    creditsTotal: 10000,
    percent: 42.5,
  };

  const invoices = [
    { id: 'INV-001', date: 'Jan 10, 2026', amount: '$99.00', status: 'Paid' },
    { id: 'INV-002', date: 'Dec 10, 2025', amount: '$99.00', status: 'Paid' },
    { id: 'INV-003', date: 'Nov 10, 2025', amount: '$99.00', status: 'Paid' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Facturación y Suscripción</h1>
        <p className="text-muted-foreground mt-1">
          Gestiona tu plan, créditos y facturas
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Plan Overview */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-6 rounded-2xl bg-gradient-to-br from-card to-secondary border border-border overflow-hidden relative"
          >
            <div className="absolute top-0 right-0 p-8 opacity-10">
              <CreditCard className="h-48 w-48 rotate-12" />
            </div>

            <div className="relative flex flex-col md:flex-row justify-between gap-6">
              <div className="space-y-4">
                <div className="inline-flex items-center px-3 py-1 rounded-full bg-primary/20 text-primary text-xs font-bold uppercase tracking-wider">
                  Plan Actual
                </div>
                <h2 className="text-4xl font-bold">{currentPlan.name}</h2>
                <div className="flex items-center gap-4 text-muted-foreground">
                  <div className="flex items-center gap-1.5">
                    <Check className="h-4 w-4 text-primary" />
                    <span>{currentPlan.price}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Check className="h-4 w-4 text-primary" />
                    <span>Próximo cobro: {currentPlan.nextBilling}</span>
                  </div>
                </div>
                <div className="pt-4 flex flex-wrap gap-2">
                  <button className="px-6 py-2.5 rounded-xl bg-white text-black font-bold hover:bg-neutral-200 transition-all flex items-center gap-2">
                    Gestionar en Stripe
                    <ExternalLink className="h-4 w-4" />
                  </button>
                  <button className="px-6 py-2.5 rounded-xl bg-secondary text-white font-bold hover:bg-neutral-800 transition-all">
                    Cambiar Plan
                  </button>
                </div>
              </div>

              <div className="bg-background/40 backdrop-blur-md p-4 rounded-xl border border-white/5 w-full md:w-64">
                <p className="text-sm font-semibold mb-4 text-muted-foreground">Incluye:</p>
                <ul className="space-y-3">
                  {currentPlan.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <Check className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>

          {/* Credits Usage */}
          <div className="p-6 rounded-2xl bg-card border border-border">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-primary" />
                <h3 className="text-lg font-bold">Consumo de Créditos</h3>
              </div>
              <button className="text-sm text-primary font-bold hover:underline">
                Añadir Créditos
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-muted-foreground">Consumo este mes</span>
                <span className="font-bold">{usage.creditsUsed} / {usage.creditsTotal} créditos</span>
              </div>
              <div className="h-4 w-full bg-secondary rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${usage.percent}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className="h-full bg-gradient-to-r from-primary to-orange-500 rounded-full"
                />
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2">
                <Info className="h-4 w-4" />
                <span>Los créditos se reinician el primer día de cada mes natural.</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
              <div className="p-4 rounded-xl bg-secondary/30 border border-border/50">
                <p className="text-xs text-muted-foreground uppercase tracking-widest font-bold mb-1">Costo por Acción</p>
                <p className="text-sm">Promedio 1.2 créditos/acción</p>
              </div>
              <div className="p-4 rounded-xl bg-secondary/30 border border-border/50">
                <p className="text-xs text-muted-foreground uppercase tracking-widest font-bold mb-1">Ahorro Estimado</p>
                <p className="text-sm text-green-500 font-bold">-$450.00 este mes</p>
              </div>
            </div>
          </div>
        </div>

        {/* Invoices Sidebar */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-card border border-border">
            <div className="flex items-center gap-2 mb-6">
              <History className="h-5 w-5 text-muted-foreground" />
              <h3 className="text-lg font-bold">Historial de Facturas</h3>
            </div>
            
            <div className="space-y-4">
              {invoices.map((inv) => (
                <div key={inv.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-secondary/50 transition-colors group">
                  <div className="space-y-0.5">
                    <p className="text-sm font-bold">{inv.id}</p>
                    <p className="text-xs text-muted-foreground">{inv.date}</p>
                  </div>
                  <div className="text-right flex items-center gap-3">
                    <p className="text-sm font-bold">{inv.amount}</p>
                    <button className="h-8 w-8 rounded-lg bg-secondary flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <button className="w-full mt-6 py-2.5 rounded-xl border border-border text-sm font-bold hover:bg-secondary transition-all">
              Ver Historial Completo
            </button>
          </div>

          <div className="p-6 rounded-2xl bg-card border border-border">
            <h3 className="text-lg font-bold mb-4">Ayuda con Pagos</h3>
            <p className="text-sm text-muted-foreground mb-4">
              ¿Tienes problemas con tu facturación o quieres una factura personalizada para tu empresa?
            </p>
            <button className="w-full py-2.5 text-sm font-bold text-primary hover:underline flex items-center justify-center gap-2">
              Contactar Soporte
              <ArrowUpRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
