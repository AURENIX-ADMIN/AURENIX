"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { TrendingUp, Euro, Clock, ArrowUpRight } from "lucide-react"

export function RealTimeROI() {
  const [data, setData] = useState<{ spent: number; saved: number; hoursSaved: number; roi: number } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchROI() {
      try {
        const res = await fetch('/api/stats/roi')
        const json = await res.json()
        setData(json)
      } catch (err) {
        console.error("Failed to fetch ROI", err)
      } finally {
        setLoading(false)
      }
    }
    fetchROI()
  }, [])

  if (loading) return <div className="h-64 animate-pulse bg-slate-800/50 rounded-xl" />
  if (!data) return null

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Spent */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="p-2 rounded-lg bg-red-500/10 text-red-500">
            <Euro className="h-5 w-5" />
          </div>
          <span className="text-xs font-medium text-slate-500">Inversión este mes</span>
        </div>
        <p className="text-3xl font-bold text-white">{data.spent.toFixed(2)}€</p>
        <p className="text-sm text-slate-500 mt-2">Coste operativo de IA</p>
      </div>

      {/* Saved */}
      <div className="p-6 rounded-xl bg-slate-900 border border-emerald-500/20 shadow-lg relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <TrendingUp className="h-24 w-24 text-emerald-500" />
        </div>
        <div className="flex items-center justify-between mb-4">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500">
            <TrendingUp className="h-5 w-5" />
          </div>
          <span className="text-xs font-medium text-emerald-500 flex items-center gap-1">
            Impacto generado <ArrowUpRight className="h-3 w-3" />
          </span>
        </div>
        <p className="text-3xl font-bold text-emerald-400">{data.saved.toFixed(0)}€</p>
        <p className="text-sm text-slate-400 mt-2">Valor generado por Aurenix</p>
      </div>

      {/* ROI */}
      <div className="p-6 rounded-xl bg-slate-900 border border-cyan-500/20 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-500">
            <Clock className="h-5 w-5" />
          </div>
          <span className="text-xs font-medium text-slate-500">Eficiencia operativa</span>
        </div>
        <p className="text-3xl font-bold text-white">{data.roi.toFixed(1)}x</p>
        <p className="text-sm text-slate-400 mt-2">{data.hoursSaved.toFixed(1)}h ahorradas este mes</p>
      </div>

      {/* Summary Banner */}
      <div className="md:col-span-3 p-4 rounded-lg bg-gradient-to-r from-emerald-600/20 to-cyan-600/20 border border-emerald-500/30 text-center">
        <p className="text-sm font-medium text-white">
          🚀 ¡Impresionante! Este mes, Aurenix te ha ahorrado <span className="text-emerald-400 font-bold">{data.saved.toFixed(0)}€</span> y ha liberado <span className="text-cyan-400 font-bold">{data.hoursSaved.toFixed(0)} horas</span> de tu equipo.
        </p>
      </div>
    </div>
  )
}
