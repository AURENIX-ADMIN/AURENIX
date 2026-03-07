import { HeroSection } from '@/components/landing/hero-section';
import { WhoSection } from '@/components/landing/who-section';
import { CTASection } from '@/components/landing/cta-section';
import { ROICalculator } from '@/components/roi-calculator';
import { LeadCaptureForm } from '@/components/landing/lead-capture-form';

export default function LandingPage() {
  return (
    <div className="bg-black text-white selection:bg-white/10">
      <HeroSection />
      
      {/* Visual Separator */}
      <div className="h-px w-full bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      
      <WhoSection />

      {/* ROI & Lead Capture Section */}
      <section className="py-32 px-4 bg-black relative overflow-hidden">
         <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
            <div className="space-y-8">
               <h2 className="text-4xl md:text-6xl font-black tracking-tighter">
                 ¿Cuánto vale <br/>
                 <span className="text-neutral-500">tu tiempo realmente?</span>
               </h2>
               <p className="text-lg text-neutral-400 leading-relaxed">
                 Nuestra tecnología no solo automatiza tareas, <span className="text-white font-bold">compra tiempo de vida</span>. 
                 Usa la calculadora para ver el impacto y permítenos diseñar tu primer Agente sin compromiso.
               </p>
               <div className="relative">
                 <div className="absolute inset-x-0 -top-20 h-40 bg-gradient-to-b from-white/5 to-transparent blur-3xl pointer-events-none" />
                 <ROICalculator />
               </div>
            </div>

            <div id="contact" className="relative group">
               <div className="absolute inset-0 bg-white/5 blur-3xl rounded-full scale-75 group-hover:scale-100 transition-transform duration-1000" />
               <LeadCaptureForm />
            </div>
         </div>
      </section>

      <CTASection />
    </div>
  );
}
