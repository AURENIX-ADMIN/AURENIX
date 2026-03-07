'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Settings,
  Bell,
  Lock,
  Globe,
  Database,
  Link as LinkIcon,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Smartphone,
  Mail,
  Zap,
} from 'lucide-react';
export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'profile' | 'integrations' | 'security' | 'notifications'>('profile');

  const tabs = [
    { id: 'profile', label: 'Perfil', icon: UserCircle },
    { id: 'integrations', label: 'Integraciones', icon: LinkIcon },
    { id: 'security', label: 'Seguridad', icon: Lock },
    { id: 'notifications', label: 'Notificaciones', icon: Bell },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Configuración</h1>
        <p className="text-muted-foreground mt-1">
          Personaliza tu experiencia y gestiona tus conexiones
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar Nav */}
        <div className="w-full lg:w-64 space-y-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  activeTab === tab.id
                    ? 'bg-primary/10 text-primary font-bold shadow-sm'
                    : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Content Area */}
        <div className="flex-1 bg-card border border-border rounded-2xl overflow-hidden min-h-[600px]">
          {activeTab === 'profile' && (
            <div className="p-8">
              <h2 className="text-xl font-bold mb-6">Información del Perfil</h2>
              <div className="max-w-3xl space-y-6">
                <div className="flex items-center gap-6 p-6 rounded-xl bg-secondary/30 border border-border">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-[hsl(45,93%,47%)] to-[hsl(20,97%,57%)] text-black text-2xl font-bold shrink-0">
                    A
                  </div>
                  <div>
                    <p className="text-lg font-bold">Administrador</p>
                    <p className="text-sm text-muted-foreground">admin@aurenix.cloud</p>
                    <p className="text-xs text-muted-foreground mt-1">Rol: Owner · Plan Pro</p>
                  </div>
                </div>
                <div className="p-6 rounded-xl bg-secondary/30 border border-border space-y-4">
                  <h3 className="font-bold">Información General</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <label className="text-muted-foreground block mb-1">Nombre</label>
                      <input type="text" defaultValue="José" className="w-full px-3 py-2 rounded-lg bg-card border border-border" />
                    </div>
                    <div>
                      <label className="text-muted-foreground block mb-1">Email</label>
                      <input type="email" defaultValue="jose@aurenix.cloud" className="w-full px-3 py-2 rounded-lg bg-card border border-border" />
                    </div>
                  </div>
                  <button className="px-4 py-2 rounded-lg bg-primary text-black font-bold text-sm mt-2">Guardar Cambios</button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'integrations' && (
            <div className="p-8">
              <h2 className="text-xl font-bold mb-2">Conexiones e Integraciones</h2>
              <p className="text-muted-foreground mb-8 text-sm">
                Conecta tus herramientas externas para que la IA pueda actuar sobre ellas.
              </p>

              <div className="space-y-6">
                <IntegrationItem
                  name="Google Workspace"
                  description="Acceso a Gmail, Calendar y Drive para automatización de tareas y reuniones."
                  icon={<Mail className="h-6 w-6 text-red-500" />}
                  connected={true}
                />
                <IntegrationItem
                  name="HubSpot CRM"
                  description="Sincroniza leads y actividades comerciales automáticamente."
                  icon={<div className="h-6 w-6 bg-orange-500 rounded flex items-center justify-center"><Zap className="h-4 w-4 text-white" /></div>}
                  connected={true}
                />
                <IntegrationItem
                  name="Slack"
                  description="Recibe notificaciones críticas y aprueba acciones directamente en Slack."
                  icon={<div className="h-6 w-6 bg-[#4A154B] rounded flex items-center justify-center text-white font-bold text-xs">S</div>}
                  connected={false}
                />
                <IntegrationItem
                  name="LinkedIn"
                  description="Requerido para la búsqueda activa de leads por el agente Lead Hunter."
                  icon={<div className="h-6 w-6 bg-[#0077B5] rounded flex items-center justify-center text-white"><Smartphone className="h-3.5 w-3.5" /></div>}
                  connected={false}
                />
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="p-8">
              <h2 className="text-xl font-bold mb-6">Seguridad de la Cuenta</h2>
              <div className="space-y-8 max-w-2xl">
                <div className="flex items-center justify-between p-4 rounded-xl bg-secondary/30 border border-border">
                  <div className="flex gap-4">
                    <Smartphone className="h-6 w-6 text-muted-foreground" />
                    <div>
                      <p className="font-bold">Doble Factor de Autenticación (2FA)</p>
                      <p className="text-sm text-muted-foreground">Recomendado para proteger acciones críticas de la IA.</p>
                    </div>
                  </div>
                  <button className="px-4 py-2 rounded-lg bg-primary text-black font-bold text-sm">Configurar</button>
                </div>

                <div className="space-y-4">
                  <h3 className="font-bold">Sesiones Activas</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-4 rounded-xl bg-secondary/30 border border-border text-sm">
                      <div className="flex items-center gap-3">
                        <Globe className="h-4 w-4 text-green-500" />
                        <span>Chrome en macOS · Madrid, ES</span>
                      </div>
                      <span className="text-xs text-green-500 font-bold">Sesión Actual</span>
                    </div>
                  </div>
                </div>

                <div className="pt-6 border-t border-border">
                  <button className="text-red-500 font-bold hover:underline text-sm">Eliminar Cuenta permanentemente</button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="p-8">
              <h2 className="text-xl font-bold mb-6">Preferencias de Notificación</h2>
              <div className="space-y-6 max-w-2xl">
                <NotificationToggle
                  title="Alertas Críticas"
                  description="Recibe avisos inmediatos si un agente encuentra un error o requiere intervención."
                  defaultOn={true}
                />
                <NotificationToggle
                  title="Resumen Diario"
                  description="Un informe diario de tiempo ahorrado y tareas completadas por tus agentes."
                  defaultOn={true}
                />
                <NotificationToggle
                  title="Notificaciones de Facturación"
                  description="Avisos de pago, facturas y uso de créditos."
                  defaultOn={true}
                />
                <NotificationToggle
                  title="Newsletter y Novedades"
                  description="Nuevos agentes disponibles y mejoras en la plataforma."
                  defaultOn={false}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function IntegrationItem({ name, description, icon, connected }: { name: string, description: string, icon: React.ReactNode, connected: boolean }) {
  return (
    <div className="flex items-center justify-between p-5 rounded-xl border border-border bg-secondary/20 hover:border-border/80 transition-all">
      <div className="flex gap-4">
        <div className="h-12 w-12 rounded-xl bg-card border border-border flex items-center justify-center shadow-sm">
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-bold">{name}</h4>
            {connected && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-500/10 text-green-500 text-[10px] font-bold uppercase tracking-wider border border-green-500/20">
                <CheckCircle2 className="h-2.5 w-2.5" />
                Conectado
              </span>
            )}
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed pr-8">{description}</p>
        </div>
      </div>
      <div>
        <button className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
          connected 
            ? 'text-muted-foreground hover:text-red-500 bg-secondary' 
            : 'bg-white text-black hover:bg-neutral-200'
        }`}>
          {connected ? 'Desconectar' : 'Conectar'}
        </button>
      </div>
    </div>
  );
}

function NotificationToggle({ title, description, defaultOn }: { title: string, description: string, defaultOn: boolean }) {
  const [on, setOn] = useState(defaultOn);
  return (
    <div className="flex items-center justify-between py-4 border-b border-border last:border-0">
      <div className="pr-8">
        <h4 className="font-bold mb-1">{title}</h4>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <button 
        onClick={() => setOn(!on)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
          on ? 'bg-primary' : 'bg-secondary'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            on ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
}

function UserCircle({ className }: { className?: string }) {
  return (
    <svg 
      className={className} 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    >
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}
