import { ActivityFeed } from "@/components/activity-feed"
import { ApprovalCard } from "@/components/approval-card"
import { PremiumDashboard } from "@/components/premium-dashboard"
import { UserButton } from "@clerk/nextjs"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center p-8 lg:p-24 bg-[#050505] text-white selection:bg-primary/30">
      {/* Dynamic Background Effect */}
      <div className="fixed inset-0 z-0 bg-[radial-gradient(circle_at_50%_0%,rgba(50,50,255,0.05),transparent_50%)] pointer-events-none" />

      {/* Header */}
      <div className="z-10 max-w-7xl w-full flex items-center justify-between mb-16 px-4">
        <div className="flex items-center space-x-4">
           <div className="h-8 w-8 bg-primary rounded-lg rotate-12 flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.5)]">
              <div className="h-4 w-4 bg-white rounded-full animate-pulse" />
           </div>
           <p className="text-2xl font-black tracking-tighter">
             AURENIX <span className="text-primary/80 font-extralight tracking-[0.2em] uppercase text-xs ml-1">Vanguard OS</span>
           </p>
        </div>
        
        <div className="flex items-center space-x-6">
             <div className="hidden md:flex px-4 py-1.5 rounded-full border border-white/5 bg-white/5 backdrop-blur-md text-[10px] uppercase tracking-widest text-primary/80">
                <span className="mr-2 h-1.5 w-1.5 rounded-full bg-green-500 inline-block animate-ping" />
                Network Healthy
             </div>
             <UserButton afterSignOutUrl="/"/>
        </div>
      </div>

      {/* Dashboard Metrics */}
      <div className="z-10 w-full max-w-7xl mb-12">
        <PremiumDashboard />
      </div>

      {/* Main Grid */}
      <div className="z-10 w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Nerve Center */}
        <div className="lg:col-span-7 space-y-8">
            <div className="rounded-3xl border border-white/5 bg-white/[0.02] p-8 backdrop-blur-2xl">
                <ActivityFeed />
            </div>
        </div>

        {/* Right Column: Decisions & Context */}
        <div className="lg:col-span-5 space-y-8">
            <div className="rounded-3xl border border-white/5 bg-white/[0.02] p-8 backdrop-blur-2xl ring-1 ring-white/5">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">Critical Actions</h2>
                        <p className="text-xs text-muted-foreground mt-1 uppercase tracking-widest">Awaiting Human-in-the-Loop Approval</p>
                    </div>
                    <span className="px-2 py-1 rounded bg-amber-500/10 text-amber-500 text-[10px] font-bold">URGENT</span>
                </div>
                <ApprovalCard />
            </div>

            <div className="rounded-3xl border border-white/5 bg-white/[0.02] p-8 backdrop-blur-2xl opacity-50 hover:opacity-100 transition-opacity">
                 <h3 className="text-lg font-bold mb-4">Internal Knowledge</h3>
                 <p className="text-sm text-muted-foreground italic font-extralight">
                    "AI systems are not replacements for human agency, but force multipliers for human potential." 
                    <span className="block mt-2 text-primary/60 not-italic">— Aurenix Master Guide</span>
                 </p>
            </div>
        </div>
      </div>
      
      {/* Subtle Footer */}
      <footer className="mt-auto pt-24 pb-8 text-center opacity-20 text-[10px] uppercase tracking-[0.5em] font-light">
          Secured by Aurenix Fortress Protocol • 2026
      </footer>
    </main>
  )
}
