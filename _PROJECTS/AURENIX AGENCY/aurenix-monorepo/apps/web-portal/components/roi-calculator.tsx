"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Calculator, Users, DollarSign, TrendingUp, Sparkles } from "lucide-react"

interface ROIResult {
  projected_annual_hours_saved: number
  projected_annual_value_usd: number
  projected_monthly_value_usd: number
  roi_multiple: number
  payback_period_months: number
}

export function ROICalculator() {
  const [numEmployees, setNumEmployees] = useState(10)
  const [avgSalary, setAvgSalary] = useState(50000)
  const [tasksPerDay, setTasksPerDay] = useState(5)
  const [minutesSaved, setMinutesSaved] = useState(15)
  const [result, setResult] = useState<ROIResult | null>(null)
  const [isCalculating, setIsCalculating] = useState(false)

  const calculateROI = async () => {
    setIsCalculating(true)
    
    // Calculate locally for instant feedback (mirrors backend logic)
    const hourlyRate = avgSalary / (52 * 40)
    const hoursPerDay = (tasksPerDay * minutesSaved) / 60
    const annualHours = hoursPerDay * 250 * numEmployees // 250 working days
    const annualValue = annualHours * hourlyRate
    const monthlyValue = annualValue / 12
    const fenixAnnualCost = numEmployees * 99 * 12
    const roiMultiple = annualValue / fenixAnnualCost
    const paybackMonths = (numEmployees * 99) / (monthlyValue || 1)

    // Simulate API delay for premium feel
    await new Promise(resolve => setTimeout(resolve, 500))

    setResult({
      projected_annual_hours_saved: Math.round(annualHours * 10) / 10,
      projected_annual_value_usd: Math.round(annualValue * 100) / 100,
      projected_monthly_value_usd: Math.round(monthlyValue * 100) / 100,
      roi_multiple: Math.round(roiMultiple * 100) / 100,
      payback_period_months: Math.round(paybackMonths * 100) / 100
    })
    setIsCalculating(false)
  }

  // Auto-calculate on input change
  useEffect(() => {
    const debounce = setTimeout(calculateROI, 300)
    return () => clearTimeout(debounce)
  }, [numEmployees, avgSalary, tasksPerDay, minutesSaved])

  // Initial calculation
  useEffect(() => {
    calculateROI()
  }, [])

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  return (
    <div className="rounded-xl border bg-gradient-to-br from-slate-900 to-slate-800 text-white shadow-2xl p-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-500">
          <Calculator className="h-6 w-6" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight">ROI Calculator</h2>
            <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Aurenix Verified
            </span>
          </div>
          <p className="text-sm text-slate-400">See how much Fenix can save your team</p>
        </div>
      </div>

      {/* Input Sliders */}
      <div className="space-y-6 mb-8">
        {/* Number of Employees */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="flex items-center gap-2">
              <Users className="h-4 w-4 text-slate-400" />
              Number of Employees
            </span>
            <span className="font-mono text-emerald-400">{numEmployees}</span>
          </div>
          <input
            type="range"
            min="1"
            max="500"
            value={numEmployees}
            onChange={(e) => setNumEmployees(Number(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
        </div>

        {/* Average Salary */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-slate-400" />
              Average Annual Salary
            </span>
            <span className="font-mono text-emerald-400">{formatCurrency(avgSalary)}</span>
          </div>
          <input
            type="range"
            min="30000"
            max="200000"
            step="5000"
            value={avgSalary}
            onChange={(e) => setAvgSalary(Number(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
        </div>

        {/* Tasks per Day */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-slate-400" />
              AI-automatable tasks per employee/day
            </span>
            <span className="font-mono text-emerald-400">{tasksPerDay}</span>
          </div>
          <input
            type="range"
            min="1"
            max="20"
            value={tasksPerDay}
            onChange={(e) => setTasksPerDay(Number(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
        </div>

        {/* Minutes Saved */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-slate-400" />
              Minutes saved per task
            </span>
            <span className="font-mono text-emerald-400">{minutesSaved} min</span>
          </div>
          <input
            type="range"
            min="5"
            max="60"
            step="5"
            value={minutesSaved}
            onChange={(e) => setMinutesSaved(Number(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
        </div>
      </div>

      {/* Results */}
      <AnimatePresence mode="wait">
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="grid grid-cols-2 gap-4"
          >
            {/* Annual Value */}
            <motion.div
              className="col-span-2 p-4 rounded-lg bg-gradient-to-r from-emerald-600/20 to-cyan-600/20 border border-emerald-500/30"
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <p className="text-sm text-slate-400">Projected Annual Savings</p>
              <motion.p
                key={result.projected_annual_value_usd}
                initial={{ scale: 1.2, color: "#6ee7b7" }}
                animate={{ scale: 1, color: "#ffffff" }}
                className="text-4xl font-bold"
              >
                {formatCurrency(result.projected_annual_value_usd)}
              </motion.p>
              <p className="text-xs text-slate-500 mt-1">
                {result.projected_annual_hours_saved.toLocaleString()} hours saved annually
              </p>
            </motion.div>

            {/* Monthly Value */}
            <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700">
              <p className="text-xs text-slate-500">Monthly Value</p>
              <p className="text-lg font-semibold text-emerald-400">
                {formatCurrency(result.projected_monthly_value_usd)}
              </p>
            </div>

            {/* ROI Multiple */}
            <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700">
              <p className="text-xs text-slate-500">ROI Multiple</p>
              <p className="text-lg font-semibold text-cyan-400">
                {result.roi_multiple}x
              </p>
            </div>

            {/* Payback Period */}
            <div className="col-span-2 p-3 rounded-lg bg-slate-800/50 border border-slate-700 text-center">
              <p className="text-xs text-slate-500">Payback Period</p>
              <p className="text-lg font-semibold">
                {result.payback_period_months < 1 
                  ? "Less than 1 month" 
                  : `${result.payback_period_months.toFixed(1)} months`}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* CTA */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full mt-6 py-3 px-4 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-lg font-semibold text-white shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-shadow"
      >
        Start Your Free Trial
      </motion.button>
    </div>
  )
}
