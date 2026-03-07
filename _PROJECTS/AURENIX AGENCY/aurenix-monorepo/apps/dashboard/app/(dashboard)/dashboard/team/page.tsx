'use client';

import { motion } from 'framer-motion';
import {
  Users,
  Plus,
  Mail,
  Shield,
  MoreVertical,
  UserPlus,
  ArrowUpRight,
} from 'lucide-react';

const members = [
  {
    id: '1',
    name: 'Tú',
    email: 'ceo@aurenix.agency',
    role: 'Admin',
    status: 'Active',
    avatar: 'https://github.com/nutlope.png', // Placeholder
  },
  {
    id: '2',
    name: 'Maria Garcia',
    email: 'm.garcia@empresa.com',
    role: 'Editor',
    status: 'Active',
    avatar: '',
  },
];

export default function TeamPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Equipo y Colaboradores</h1>
          <p className="text-muted-foreground mt-1">
            Gestiona quién tiene acceso a tus agentes y flujos de automatización
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-black font-bold text-sm hover:bg-primary/90 transition-all">
          <UserPlus className="h-4 w-4" />
          Invitar Miembro
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Members List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
            <div className="grid grid-cols-12 p-4 border-b border-border text-xs font-bold text-muted-foreground uppercase tracking-wider">
              <div className="col-span-6">Nombre</div>
              <div className="col-span-3">Rol</div>
              <div className="col-span-3 text-right">Acciones</div>
            </div>
            
            <div className="divide-y divide-border">
              {members.map((member) => (
                <div key={member.id} className="grid grid-cols-12 p-4 items-center hover:bg-secondary/20 transition-colors">
                  <div className="col-span-6 flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-secondary border border-border flex items-center justify-center font-bold overflow-hidden">
                      {member.avatar ? (
                        <img src={member.avatar} alt={member.name} className="h-full w-full object-cover" />
                      ) : (
                        member.name.charAt(0)
                      )}
                    </div>
                    <div className="min-w-0">
                      <p className="font-bold text-sm truncate">{member.name}</p>
                      <p className="text-xs text-muted-foreground truncate">{member.email}</p>
                    </div>
                  </div>
                  <div className="col-span-3">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary text-xs font-medium border border-border">
                      {member.role === 'Admin' && <Shield className="h-3 w-3 text-primary" />}
                      {member.role}
                    </span>
                  </div>
                  <div className="col-span-3 text-right">
                    <button className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors">
                      <MoreVertical className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-secondary/20 border border-dashed border-border flex flex-col items-center justify-center text-center">
            <div className="h-12 w-12 rounded-full bg-secondary flex items-center justify-center mb-4">
              <Users className="h-6 w-6 text-muted-foreground" />
            </div>
            <h3 className="font-bold mb-1">Ahorra tiempo juntos</h3>
            <p className="text-sm text-muted-foreground max-w-sm mb-6">
              Invita a tu equipo de ventas o asistentes para que revisen los borradores de la IA y gestionen los leads directamente.
            </p>
            <button className="text-sm font-bold text-primary hover:underline">
              Saber más sobre roles y permisos
            </button>
          </div>
        </div>

        {/* Info Sidebar */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-card border border-border">
            <h3 className="font-bold mb-4">Límites de Equipo</h3>
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Miembros</span>
                <span className="font-bold">2 / 5</span>
              </div>
              <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div className="h-full w-[40%] bg-primary rounded-full" />
              </div>
              <p className="text-xs text-muted-foreground">
                Tu plan actual permite hasta 5 miembros. Para equipos más grandes, contacta con ventas.
              </p>
              <button className="w-full py-2.5 rounded-xl border border-primary text-primary text-sm font-bold hover:bg-primary/10 transition-all flex items-center justify-center gap-2">
                Mejorar Plan
                <ArrowUpRight className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-card border border-border">
            <h3 className="font-bold mb-4">Actividad de Equipo</h3>
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="h-8 w-8 rounded-full bg-secondary shrink-0" />
                <div className="text-xs">
                  <p className="font-bold text-foreground">Maria Garcia</p>
                  <p className="text-muted-foreground">Aprobó borrador de Lead Hunter</p>
                  <p className="text-neutral-600 mt-1">Hace 2 horas</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
