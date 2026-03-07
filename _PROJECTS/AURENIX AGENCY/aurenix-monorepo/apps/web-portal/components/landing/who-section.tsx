'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { User, Briefcase, Building2, ArrowRight, Clock, Target, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

const audiences = [
  {
    icon: User,
    title: 'Individuales',
    description: 'Recupera el control de tu tiempo diario con asistentes que gestionan tus tareas repetitivas.',
    benefits: ['Asistente de email personal', 'Gestión de agenda inteligente', 'Automatización de recados digitales'],
    timesSaved: 'Recupera ~5h/semana',
  },
  {
    icon: Briefcase,
    title: 'Autónomos',
    description: 'Escala tu productividad sin aumentar tu carga de trabajo. Fénix es tu brazo derecho operativo.',
    benefits: ['Gestión de clientes y leads', 'Facturación automatizada', 'Marketing de contenidos con IA'],
    timesSaved: 'Recupera ~15h/semana',
  },
  {
    icon: Building2,
    title: 'Empresas & PYMEs',
    description: 'Transforma tu organización en una entidad de alto rendimiento con agentes especializados por departamento.',
    benefits: ['Operaciones 24/7 sin bajas', 'Análisis de datos en tiempo real', 'Atención al cliente multicanal'],
    timesSaved: 'Recupera ~40h/semana por equipo',
  },
];

export function WhoSection() {
  const [ref, inView] = useInView({ threshold: 0.1, triggerOnce: true });

  return (
    <section className='py-32 bg-black relative'>
       <div className='max-w-7xl mx-auto px-4 relative z-10'>
          <motion.div
            ref={ref}
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8 }}
            className='text-center mb-20'
          >
            <h2 className='text-3xl md:text-5xl font-bold text-white mb-6'>Diseñado para la<br/><span className='text-neutral-500'>Nueva Fuerza Laboral Digital</span></h2>
            <p className='text-lg text-neutral-400 max-w-2xl mx-auto'>Aurenix se adapta a tu escala, desde la gestión personal hasta la automatización industrial de procesos.</p>
          </motion.div>

          <div className='grid grid-cols-1 md:grid-cols-3 gap-8'>
             {audiences.map((audience, index) => (
                <motion.div
                  key={audience.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={inView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                  className='p-8 rounded-3xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-colors group'
                >
                   <div className='mb-6 p-3 rounded-2xl bg-white/5 w-fit border border-white/10 group-hover:scale-110 transition-transform'>
                      <audience.icon className='h-6 w-6 text-white' />
                   </div>
                   <h3 className='text-xl font-bold text-white mb-4'>{audience.title}</h3>
                   <p className='text-sm text-neutral-400 mb-6 leading-relaxed'>{audience.description}</p>
                   
                   <ul className='space-y-3 mb-8'>
                      {audience.benefits.map(benefit => (
                         <li key={benefit} className='flex items-center text-xs text-neutral-300'>
                            <Sparkles className='h-3 w-3 text-white/40 mr-2' />
                            {benefit}
                         </li>
                      ))}
                   </ul>

                   <div className='flex items-center justify-between mt-auto pt-6 border-t border-white/5'>
                      <span className='text-[10px] uppercase tracking-widest text-neutral-500 font-bold'>{audience.timesSaved}</span>
                      <Button variant="ghost" size="sm" className="text-xs group-hover:translate-x-1 transition-transform" asChild>
                         <Link href="/sign-up">Comenzar <ArrowRight className="ml-1 h-3 w-3" /></Link>
                      </Button>
                   </div>
                </motion.div>
             ))}
          </div>
       </div>
    </section>
  );
}
