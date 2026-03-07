'use client';

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Loader2, Brain, CheckCircle2, AlertCircle, ShieldCheck } from "lucide-react"

interface AuditLog {
  id: string
  action: string
  resource: string
  details: any
  severity: string
  timestamp: string
}

export function ActivityFeed() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchLogs() {
      try {
        const res = await fetch('/api/stats/logs')
        const json = await res.json()
        if (Array.isArray(json)) {
            setLogs(json)
        }
      } catch (err) {
        console.error("Failed to fetch logs", err)
      } finally {
        setLoading(false)
      }
    }
    fetchLogs()
    
    // Polling for live feel
    const interval = setInterval(fetchLogs, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading && logs.length === 0) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-16 animate-pulse bg-slate-800/20 rounded-lg" />
        ))}
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-4 shadow-xl">
      <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-white/10">
        <AnimatePresence initial={false}>
          {logs.map((log) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-start space-x-4 border-b border-white/5 pb-4 last:border-0 last:pb-0"
            >
              <div className="mt-1 flex h-8 w-8 shrink-0 overflow-hidden rounded-full items-center justify-center bg-white/5">
                {log.severity === 'INFO' && <ShieldCheck className="h-4 w-4 text-cyan-400" />}
                {log.severity === 'WARNING' && <AlertCircle className="h-4 w-4 text-yellow-500" />}
                {log.severity === 'ERROR' && <AlertCircle className="h-4 w-4 text-red-500" />}
                {log.action.includes('START') && <Loader2 className="h-4 w-4 animate-spin text-blue-500" />}
                {!['INFO', 'WARNING', 'ERROR'].includes(log.severity) && <Brain className="h-4 w-4 text-slate-400" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{log.action.replace(/_/g, ' ')}</p>
                <p className="text-xs text-slate-500 mt-0.5">{log.resource}</p>
                <p className="text-[10px] text-slate-600 mt-1">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {logs.length === 0 && (
          <div className="py-10 text-center text-slate-500 italic text-sm">
            No se han registrado acciones aún.
          </div>
        )}
      </div>
    </div>
  )
}
