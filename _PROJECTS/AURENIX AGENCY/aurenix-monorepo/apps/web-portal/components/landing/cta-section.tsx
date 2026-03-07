'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Button } from '@/components/ui/button';
import { ArrowRight, Calendar, MessageSquare, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect } from 'react';

export function CTASection() {
  const [ref, inView] = useInView({
    threshold: 0.1,
    triggerOnce: true,
  });
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  return (
    <section className='py-20 md:py-32 bg-black relative overflow-hidden'>
      <div className='absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(212,175,55,0.05),transparent_70%)]' />

      <div className='max-w-7xl mx-auto relative z-10 px-4'>
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.8 }}
          className='max-w-5xl mx-auto'
        >
          <div className='p-8 md:p-12 lg:p-16 text-center border border-white/10 bg-white/5 rounded-3xl backdrop-blur-xl'>
            <div className='relative z-10'>
              <div className='inline-flex items-center px-4 py-2 bg-white/10 border border-white/20 rounded-full mb-8'>
                <Sparkles className='h-4 w-4 text-white mr-2' />
                <span className='text-sm font-medium text-white'>Escalado Infinito con IA</span>
              </div>

              <h2 className='text-3xl md:text-5xl lg:text-6xl font-bold text-white mb-6'>
                ¿Listo para la Nueva Era de<br />
                <span className='text-neutral-400'>Productividad Inteligente?</span>
              </h2>

              <p className='text-lg md:text-xl text-neutral-400 mb-12 max-w-3xl mx-auto leading-relaxed'>
                Únete a las empresas que ya están ahorrando cientos de horas integrando agentes de Aurenix en sus flujos diarios.
              </p>

              <div className='flex flex-col sm:flex-row gap-4 justify-center items-center'>
                <Button
                  size='lg'
                  className='w-full sm:w-auto bg-white text-black hover:bg-neutral-200 text-lg px-10 py-7 rounded-xl shadow-xl'
                  asChild
                >
                  <Link href='/demo'>
                    <MessageSquare className='mr-2 h-5 w-5' />
                    Ver Auditoría Gratuita
                    <ArrowRight className='ml-2 h-5 w-5' />
                  </Link>
                </Button>

                <Button
                  size='lg'
                  variant='outline'
                  className='w-full sm:w-auto text-lg px-10 py-7 border-neutral-700 bg-transparent text-white hover:bg-neutral-900 rounded-xl'
                  asChild
                >
                  <Link href='/sign-up'>
                    Comenzar Ahora
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
