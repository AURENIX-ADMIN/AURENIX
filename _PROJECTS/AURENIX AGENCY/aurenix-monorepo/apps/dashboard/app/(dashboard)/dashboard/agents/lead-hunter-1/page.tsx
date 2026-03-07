'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Bot, 
  Settings, 
  Target, 
  Users, 
  Globe, 
  BarChart3, 
  Play, 
  Save,
  CheckCircle2,
  Trash2,
  Plus
} from 'lucide-react';

export default function LeadHunterConfigPage() {
  const [activeTab, setActiveTab] = useState<'config' | 'leads' | 'analytics'>('config');
  const [isRunning, setIsRunning] = useState(false);
  const [lastExecution, setLastExecution] = useState<string | null>(null);

  const [config, setConfig] = useState({
    industries: ['SAAS', 'Inteligencia Artificial'],
    location: 'España / Europa',
    minEmployees: 10,
    icp: 'Empresas B2B tech con menos de 50 empleados que busquen optimizar procesos con IA.',
    frequency: 'daily'
  });

  const handleRunAgent = async () => {
    setIsRunning(true);
    try {
      const response = await fetch('/api/agents/lead-hunter/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...config,
          organizationId: 'replace-with-real-org-id' // TODO: Get from context/params
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setLastExecution(new Date().toLocaleString());
      } else {
        alert('Error al iniciar el agente: ' + (data.error || 'Desconocido'));
      }
    } catch (err) {
      console.error(err);
      alert('Error de conexión');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-[hsl(45,93%,47%)] to-[hsl(20,97%,57%)] flex items-center justify-center text-black">
            <Bot className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Lead Hunter Pro</h1>
            <p className="text-muted-foreground text-sm">Gestiona la configuración y resultados de tu agente de prospección</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={handleRunAgent}
            disabled={isRunning}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              isRunning 
                ? 'bg-secondary text-muted-foreground cursor-not-allowed' 
                : 'bg-[hsl(45,93%,47%)] text-black hover:shadow-[0_0_20px_rgba(255,191,0,0.3)]'
            }`}
          >
            <Play className={`h-4 w-4 ${isRunning ? 'animate-pulse' : ''}`} />
            {isRunning ? 'Ejecutando...' : 'Ejecutar Ahora'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border">
        {(['config', 'leads', 'analytics'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 text-sm font-medium transition-colors relative ${
              activeTab === tab ? 'text-[hsl(45,93%,47%)]' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab === 'config' && 'Configuración'}
            {tab === 'leads' && 'Leads Encontrados'}
            {tab === 'analytics' && 'Métricas'}
            {activeTab === tab && (
              <motion.div 
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-[hsl(45,93%,47%)]" 
              />
            )}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {activeTab === 'config' && (
          <>
            <div className="lg:col-span-2 space-y-6">
              {/* ICP & Mission */}
              <div className="p-6 rounded-2xl bg-card border border-border space-y-4">
                <div className="flex items-center gap-2 text-[hsl(45,93%,47%)] mb-2">
                  <Target className="h-5 w-5" />
                  <h2 className="font-semibold">Perfil de Cliente Ideal (ICP)</h2>
                </div>
                <p className="text-sm text-muted-foreground">
                  Describe detalladamente el tipo de empresas y perfiles que el agente debe buscar. La IA usará esto para calificar cada lead.
                </p>
                <textarea 
                  value={config.icp}
                  onChange={(e) => setConfig({...config, icp: e.target.value})}
                  className="w-full h-32 p-4 rounded-xl bg-secondary/50 border border-border focus:ring-2 focus:ring-[hsl(45,93%,47%)]/30 focus:border-[hsl(45,93%,47%)] outline-none transition-all"
                  placeholder="Ej: CEOs de agencias de marketing en Madrid con más de 10 empleados..."
                />
              </div>

              {/* Advanced Parameters */}
              <div className="p-6 rounded-2xl bg-card border border-border space-y-6">
                <div className="flex items-center gap-2 text-[hsl(45,93%,47%)] mb-2">
                  <Settings className="h-5 w-5" />
                  <h2 className="font-semibold">Parámetros de Búsqueda</h2>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium flex items-center gap-2">
                      <Globe className="h-4 w-4 text-muted-foreground" />
                      Ubicación Target
                    </label>
                    <input 
                      type="text" 
                      value={config.location}
                      onChange={(e) => setConfig({...config, location: e.target.value})}
                      className="w-full p-3 rounded-lg bg-secondary/30 border border-border"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium flex items-center gap-2">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      Tamaño Mín. Empresa
                    </label>
                    <select 
                      value={config.minEmployees}
                      onChange={(e) => setConfig({...config, minEmployees: parseInt(e.target.value)})}
                      className="w-full p-3 rounded-lg bg-secondary/30 border border-border"
                    >
                      <option value={1}>1-10 empleados</option>
                      <option value={11}>11-50 empleados</option>
                      <option value={51}>51-200 empleados</option>
                      <option value={201}>+200 empleados</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Sectores / Keywords</label>
                  <div className="flex flex-wrap gap-2">
                    {config.industries.map((industry, i) => (
                      <span key={i} className="px-3 py-1 rounded-full bg-[hsl(45,93%,47%)]/10 text-[hsl(45,93%,47%)] text-xs border border-[hsl(45,93%,47%)]/20 flex items-center gap-2">
                        {industry}
                        <Trash2 className="h-3 w-3 cursor-pointer" onClick={() => setConfig({...config, industries: config.industries.filter((_, idx) => idx !== i)})} />
                      </span>
                    ))}
                    <button className="px-3 py-1 rounded-full border border-dashed border-border text-muted-foreground text-xs hover:border-foreground transition-all flex items-center gap-1">
                      <Plus className="h-3 w-3" /> Añadir
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Sidebar Config */}
            <div className="space-y-6">
              <div className="p-6 rounded-2xl bg-card border border-border space-y-4">
                <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">Estado y Logs</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Última ejecución</span>
                    <span className="font-medium">{lastExecution || 'Nunca'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Frecuencia</span>
                    <span className="font-medium">Diaria</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Créditos por Run</span>
                    <span className="font-medium text-[hsl(45,93%,47%)]">5 créditos</span>
                  </div>
                </div>
                <button className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all font-medium">
                  <Save className="h-4 w-4" /> Guardar Cambios
                </button>
              </div>

              <div className="p-6 rounded-2xl bg-gradient-to-br from-[hsl(45,93%,47%)]/10 to-transparent border border-[hsl(45,93%,47%)]/20">
                <div className="flex items-center gap-2 text-[hsl(45,93%,47%)] mb-3">
                  <BarChart3 className="h-5 w-5" />
                  <h3 className="font-semibold">Resumen de Valor</h3>
                </div>
                <p className="text-xs text-muted-foreground mb-4">
                  Este agente ha generado un valor estimado de <span className="text-white font-medium">$4,720</span> en los últimos 30 días.
                </p>
                <div className="h-2 w-full bg-black/40 rounded-full overflow-hidden">
                  <div className="h-full bg-[hsl(45,93%,47%)] w-3/4 shadow-[0_0_10px_rgba(255,191,0,0.5)]" />
                </div>
                <div className="flex justify-between mt-2 text-[10px] text-muted-foreground uppercase">
                  <span>Meta leads</span>
                  <span>75% completado</span>
                </div>
              </div>
            </div>
          </>
        )}

        {activeTab === 'leads' && (
          <div className="lg:col-span-3">
            <div className="p-6 rounded-2xl bg-card border border-border">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold">Leads Generados</h2>
                <div className="flex gap-2">
                  <button className="px-4 py-2 rounded-lg bg-secondary text-sm">Exportar CSV</button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground">
                      <th className="pb-3 font-medium">Empresa / Nombre</th>
                      <th className="pb-3 font-medium">Puntuación IA</th>
                      <th className="pb-3 font-medium">Ubicación</th>
                      <th className="pb-3 font-medium">Estado</th>
                      <th className="pb-3 font-medium">Acción</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {[1,2,3,4,5].map((i) => (
                      <tr key={i} className="group hover:bg-white/5 transition-colors">
                        <td className="py-4">
                          <div className="font-medium">Lead {i} Tech Corp</div>
                          <div className="text-xs text-muted-foreground">CEO - techcorp.ai</div>
                        </td>
                        <td className="py-4">
                          <span className="flex items-center gap-1.5 text-green-500 font-medium">
                            {95 - i*2}% <CheckCircle2 className="h-3.5 w-3.5" />
                          </span>
                        </td>
                        <td className="py-4 text-muted-foreground">Madrid, ES</td>
                        <td className="py-4">
                          <span className="px-2 py-1 rounded-md bg-green-500/10 text-green-500 text-[10px] font-bold uppercase">Nuevo</span>
                        </td>
                        <td className="py-4">
                          <button className="text-[hsl(45,93%,47%)] hover:underline">Ver detalles</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
