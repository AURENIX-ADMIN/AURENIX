'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, 
  Upload, 
  Search, 
  Filter, 
  BrainCircuit, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  Eye,
  Download,
  MoreVertical,
  Plus
} from 'lucide-react';

interface KnowledgeResource {
  id: string;
  name: string;
  type: string;
  size: string;
  status: 'pending' | 'processing' | 'indexed' | 'error';
  insights: number;
  date: string;
}

const mockResources: KnowledgeResource[] = [
  {
    id: '1',
    name: 'Q3_Financial_Services_Report.pdf',
    type: 'PDF',
    size: '2.4 MB',
    status: 'indexed',
    insights: 12,
    date: '10 Ene 2026',
  },
  {
    id: '2',
    name: 'Invoice_Aurenix_JAN_2026.pdf',
    type: 'PDF',
    size: '450 KB',
    status: 'processing',
    insights: 0,
    date: 'Hace 5 min',
  },
  {
    id: '3',
    name: 'Legal_Contract_AcmeCorp.docx',
    type: 'DOCX',
    size: '1.1 MB',
    status: 'indexed',
    insights: 8,
    date: 'Yesterday',
  },
];

const statusStyles = {
  pending: 'bg-yellow-500/10 text-yellow-500',
  processing: 'bg-blue-500/10 text-blue-500 animate-pulse',
  indexed: 'bg-green-500/10 text-green-500',
  error: 'bg-red-500/10 text-red-500',
};

export default function VantagePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = () => {
    setIsUploading(true);
    setTimeout(() => setIsUploading(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
            <BrainCircuit className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">VANTAGE</h1>
            <p className="text-muted-foreground text-sm">Inteligencia Documental y RAG Corporativo</p>
          </div>
        </div>
        <button 
          onClick={handleUpload}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white text-black font-semibold hover:bg-white/90 transition-all"
        >
          <Upload className="h-4 w-4" />
          Subir Documento
        </button>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: 'Total Conocimiento', value: '124', detail: 'documentos indexados', icon: FileText, color: 'text-indigo-500' },
          { label: 'Insights Extraídos', value: '1,492', detail: 'entidades detectadas', icon: BrainCircuit, color: 'text-purple-500' },
          { label: 'Búsqueda Semántica', value: 'Activa', detail: 'RAG Pipeline Online', icon: CheckCircle2, color: 'text-green-500' },
        ].map((stat, i) => (
          <div key={i} className="p-5 rounded-2xl bg-card border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{stat.label}</span>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">{stat.value}</span>
              <span className="text-xs text-muted-foreground">{stat.detail}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content */}
      <div className="p-6 rounded-2xl bg-card border border-border">
        {/* Toolbar */}
        <div className="flex items-center justify-between mb-6 gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Pregunta a tu base de conocimiento..." 
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-secondary/50 border border-border focus:ring-2 focus:ring-indigo-500/30 outline-none transition-all"
            />
          </div>
          <div className="flex gap-2">
            <button className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors">
              <Filter className="h-4 w-4 text-muted-foreground" />
            </button>
            <button className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors">
              <Plus className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>
        </div>

        {/* Documents Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-muted-foreground border-b border-border">
                <th className="pb-4 font-medium">Nombre del Archivo</th>
                <th className="pb-4 font-medium">Estado VANTAGE</th>
                <th className="pb-4 font-medium">Insights</th>
                <th className="pb-4 font-medium">Tamaño</th>
                <th className="pb-4 font-medium">Fecha</th>
                <th className="pb-4 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {mockResources.map((doc) => (
                <tr key={doc.id} className="group hover:bg-white/[0.02] transition-colors">
                  <td className="py-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-secondary flex items-center justify-center text-muted-foreground group-hover:text-indigo-500 transition-colors">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div>
                        <div className="font-medium">{doc.name}</div>
                        <div className="text-xs text-muted-foreground uppercase">{doc.type}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-4">
                    <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${statusStyles[doc.status]}`}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="py-4">
                    <span className="flex items-center gap-1.5 text-indigo-400 font-medium">
                      <BrainCircuit className="h-3.5 w-3.5" />
                      {doc.insights}
                    </span>
                  </td>
                  <td className="py-4 text-muted-foreground">{doc.size}</td>
                  <td className="py-4 text-muted-foreground">{doc.date}</td>
                  <td className="py-4 text-right">
                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="p-1.5 rounded-lg hover:bg-secondary transition-colors" title="Ver Insights">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="p-1.5 rounded-lg hover:bg-secondary transition-colors" title="Descargar">
                        <Download className="h-4 w-4" />
                      </button>
                      <button className="p-1.5 rounded-lg hover:bg-secondary transition-colors">
                        <MoreVertical className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Search Section (RAG) */}
      <div className="p-8 rounded-3xl bg-gradient-to-br from-indigo-600/20 via-transparent to-purple-600/10 border border-indigo-500/20 relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row items-center gap-8">
          <div className="flex-1 space-y-4 text-center md:text-left">
            <h2 className="text-2xl font-bold">Asistente de Conocimiento</h2>
            <p className="text-muted-foreground">
              VANTAGE puede responder preguntas complejas basándose en toda tu documentación indexada. 
              Prueba con: <span className="text-indigo-400 italic">"¿Cuál es el resumen de pagos de Q3?"</span>
            </p>
            <div className="flex gap-2">
              <input 
                type="text" 
                placeholder="Haz una pregunta técnica o comercial..." 
                className="flex-1 px-4 py-3 rounded-xl bg-black/40 border border-white/10 outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button className="px-6 py-3 rounded-xl bg-indigo-500 text-white font-bold hover:bg-indigo-400 transition-all shadow-lg shadow-indigo-500/25">
                Preguntar
              </button>
            </div>
          </div>
          <div className="h-48 w-48 relative hidden md:block">
             {/* Decorative AI Icon */}
             <div className="absolute inset-0 bg-indigo-500/20 blur-3xl rounded-full" />
             <BrainCircuit className="h-full w-full text-indigo-500 animate-pulse relative z-10" />
          </div>
        </div>
      </div>
    </div>
  );
}
