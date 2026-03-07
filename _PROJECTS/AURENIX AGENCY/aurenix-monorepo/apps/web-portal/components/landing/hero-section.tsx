'use client';

import { useState, useEffect, useMemo } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, Play, Clock, TrendingUp, Zap, Sparkles } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { useUser } from '@clerk/nextjs';

export function HeroSection() {
  const [typedText, setTypedText] = useState('');
  const [hasMounted, setHasMounted] = useState(false);
  const { isSignedIn } = useUser();
  const prefersReducedMotion = useReducedMotion();

  const fullText = 'Soluciones de IA que Ahorran Tiempo Real';

  useEffect(() => {
    setHasMounted(true);
    if (prefersReducedMotion) {
      setTypedText(fullText);
      return;
    }

    let i = 0;
    const timer = setInterval(() => {
      if (i < fullText.length) {
        setTypedText(fullText.slice(0, i + 1));
        i++;
      } else {
        clearInterval(timer);
      }
    }, 50);

    return () => clearInterval(timer);
  }, [prefersReducedMotion]);

  const particles = useMemo(() => {
    if (!hasMounted || prefersReducedMotion) return [];
    const width = typeof window !== 'undefined' ? window.innerWidth : 1000;
    const height = typeof window !== 'undefined' ? window.innerHeight : 800;

    return Array.from({ length: 15 }, (_, i) => ({
      id: i,
      color:
        i % 3 === 0 ? 'rgba(212, 175, 55, 0.4)' : i % 3 === 1 ? 'rgba(255, 107, 53, 0.3)' : 'rgba(255, 255, 255, 0.2)',
      initialX: Math.random() * width,
      initialY: Math.random() * height,
      targetX: Math.random() * width,
      targetY: Math.random() * height,
      duration: Math.random() * 15 + 10,
    }));
  }, [hasMounted, prefersReducedMotion]);

  const stats = [
    {
      icon: Clock,
      value: '15h+',
      label: 'Ahorradas por Semana',
      color: 'phoenix-gold',
      bgColor: 'phoenix-gold/10',
      borderColor: 'phoenix-gold/30',
    },
    {
      icon: TrendingUp,
      value: '300%',
      label: 'ROI en Productividad',
      color: 'phoenix-orange',
      bgColor: 'phoenix-orange/10',
      borderColor: 'phoenix-orange/30',
    },
    {
      icon: Zap,
      value: '100%',
      label: 'Personalizado',
      color: 'neutral-300',
      bgColor: 'neutral-800',
      borderColor: 'neutral-700',
    },
  ];

  return (
    <section
      className='relative min-h-screen flex items-center justify-center overflow-hidden bg-black'
      aria-label='Hero section'
    >
      <div className='absolute inset-0' style={{ background: 'radial-gradient(circle at 50% 50%, rgba(212, 175, 55, 0.05), transparent 70%)' }} />

      <div
        className='absolute inset-0 bg-[linear-gradient(to_right,#1a1a1a_1px,transparent_1px),linear-gradient(to_bottom,#1a1a1a_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-20'
        aria-hidden='true'
      />

      {hasMounted && !prefersReducedMotion && (
        <div className='absolute inset-0' aria-hidden='true'>
          {particles.map(particle => (
            <motion.div
              key={particle.id}
              className='absolute w-1 h-1 rounded-full'
              style={{ background: particle.color }}
              initial={{ x: particle.initialX, y: particle.initialY, opacity: 0 }}
              animate={{ x: particle.targetX, y: particle.targetY, opacity: [0, 1, 0] }}
              transition={{ duration: particle.duration, repeat: Infinity, ease: 'linear' }}
            />
          ))}
        </div>
      )}

      <div className='relative z-10 max-w-7xl mx-auto text-center px-4'>
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
          <div className='mb-12 md:mb-20 flex flex-col items-center'>
            <motion.div
              className='inline-flex items-center px-4 py-2 bg-phoenix-gold/10 border border-phoenix-gold/30 rounded-full mb-6 md:mb-8'
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              <Sparkles className='h-4 w-4 text-phoenix-gold mr-2' aria-hidden='true' />
              <span className='text-sm font-medium text-phoenix-gold'>Plataforma Vanguard OS - Acceso Beta</span>
            </motion.div>

            <h1 className='text-4xl md:text-5xl lg:text-7xl font-bold text-white tracking-tight leading-tight mb-2'>
              {typedText}
              {hasMounted && !prefersReducedMotion && (
                <span className='animate-pulse text-phoenix-gold' aria-hidden='true'>
                  |
                </span>
              )}
            </h1>
          </div>

          <p className='text-lg md:text-xl lg:text-2xl text-neutral-300 mb-8 max-w-4xl mx-auto leading-relaxed'>
            Potenciamos tu empresa con Agentes de IA que trabajan 24/7.
            <br/><span className='text-phoenix-gold font-semibold'>Recupera tu tiempo.</span> Escala sin límites.
          </p>

          <div className='flex flex-col sm:flex-row gap-4 justify-center items-center mb-12 md:mb-20'>
            <Button
              size='lg'
              className='w-full sm:w-auto bg-white text-black hover:bg-neutral-200 text-lg px-12 py-7 rounded-xl transition-all'
              asChild
            >
              <Link href={isSignedIn ? '/dashboard' : '/sign-up'}>
                {isSignedIn ? 'Ir al Dashboard' : 'Comenzar Gratis'}
                <ArrowRight className='ml-2 h-5 w-5' />
              </Link>
            </Button>

            <Button
              size='lg'
              variant='outline'
              className='w-full sm:w-auto text-lg px-10 py-7 border-neutral-700 bg-transparent text-white hover:bg-neutral-900'
              asChild
            >
              <Link href='/demo'>
                <Play className='mr-2 h-5 w-5' />
                Ver Demo
              </Link>
            </Button>
          </div>

          <motion.div
            className='grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto'
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div key={index} className='text-center p-6 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-sm'>
                  <div className='flex items-center justify-center mb-3'>
                    <div className={`p-3 rounded-xl bg-white/5 border border-white/10`}>
                      <Icon className={`h-6 w-6 text-white`} aria-hidden='true' />
                    </div>
                  </div>
                  <span className='text-4xl font-bold text-white mb-1 block'>
                    {stat.value}
                  </span>
                  <p className='text-xs text-neutral-400 uppercase tracking-widest'>{stat.label}</p>
                </div>
              );
            })}
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
