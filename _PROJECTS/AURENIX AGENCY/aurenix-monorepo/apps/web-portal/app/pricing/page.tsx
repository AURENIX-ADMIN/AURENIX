'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, Building2, Sparkles, ArrowRight, Shield, Clock, Users } from 'lucide-react';
import Link from 'next/link';

interface PricingTier {
  name: string;
  description: string;
  price: string;
  priceNote: string;
  priceId?: string;
  features: string[];
  cta: string;
  ctaLink: string;
  popular?: boolean;
  enterprise?: boolean;
}

const tiers: PricingTier[] = [
  {
    name: 'Starter',
    description: 'Perfecto para probar el poder de la IA',
    price: 'Gratis',
    priceNote: '14 días de prueba',
    features: [
      'Acceso a 1 Agente IA',
      '100 ejecuciones/mes',
      'Dashboard básico',
      'Soporte por email',
      'Documentación completa',
    ],
    cta: 'Comenzar Prueba',
    ctaLink: '/sign-up',
  },
  {
    name: 'Pro',
    description: 'Para equipos que buscan escalar',
    price: '$99',
    priceNote: 'por usuario/mes',
    priceId: process.env.NEXT_PUBLIC_STRIPE_PRO_PRICE_ID || 'price_pro',
    features: [
      'Todos los Agentes IA',
      'Ejecuciones ilimitadas',
      'Dashboard completo',
      'Human-in-the-Loop',
      'Integraciones (CRM, Calendar)',
      'Analytics avanzado',
      'Soporte prioritario',
      'API Access',
    ],
    cta: 'Suscribirse',
    ctaLink: '/api/checkout',
    popular: true,
  },
  {
    name: 'Enterprise',
    description: 'Solución completa para grandes empresas',
    price: 'Custom',
    priceNote: 'contactar ventas',
    features: [
      'Todo en Pro, más:',
      'Workers dedicados',
      'SLA garantizado (99.9%)',
      'Despliegue on-premise opcional',
      'Agentes personalizados',
      'Account Manager dedicado',
      'Cumplimiento EU AI Act',
      'Auditoría de seguridad',
      'Formación de equipo',
    ],
    cta: 'Contactar Ventas',
    ctaLink: '/contact',
    enterprise: true,
  },
];

const benefits = [
  {
    icon: Clock,
    title: '15+ horas/semana ahorradas',
    description: 'Automatiza tareas repetitivas y recupera tiempo valioso',
  },
  {
    icon: Shield,
    title: 'Seguridad Enterprise',
    description: 'Cifrado AES-256, aislamiento multi-tenant, cumplimiento RGPD',
  },
  {
    icon: Users,
    title: 'Human-in-the-Loop',
    description: 'La IA propone, tú apruebas. Control total sobre cada acción',
  },
];

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  const [isLoading, setIsLoading] = useState<string | null>(null);

  const handleCheckout = async (tier: PricingTier) => {
    if (!tier.priceId || tier.enterprise) return;
    
    setIsLoading(tier.name);
    
    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          priceId: tier.priceId,
          quantity: 1,
          billingCycle,
        }),
      });

      const data = await response.json();
      
      if (data.url) {
        window.location.href = data.url;
      } else {
        console.error('Checkout error:', data.error);
      }
    } catch (error) {
      console.error('Checkout failed:', error);
    } finally {
      setIsLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-white">
            Aurenix<span className="text-phoenix-gold">.</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/sign-in" className="text-neutral-400 hover:text-white transition-colors">
              Iniciar Sesión
            </Link>
            <Link
              href="/sign-up"
              className="px-4 py-2 bg-white text-black rounded-lg font-medium hover:bg-neutral-200 transition-colors"
            >
              Comenzar
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center px-4 py-2 bg-phoenix-gold/10 border border-phoenix-gold/30 rounded-full mb-6">
              <Sparkles className="h-4 w-4 text-phoenix-gold mr-2" />
              <span className="text-sm font-medium text-phoenix-gold">Precios Transparentes</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Invierte en{' '}
              <span className="bg-gradient-to-r from-phoenix-gold to-phoenix-orange bg-clip-text text-transparent">
                Productividad Real
              </span>
            </h1>
            
            <p className="text-xl text-neutral-400 mb-8 max-w-2xl mx-auto">
              Elige el plan que se adapta a tu empresa. Sin sorpresas, sin costes ocultos.
              Cancela cuando quieras.
            </p>

            {/* Billing Toggle */}
            <div className="inline-flex items-center bg-neutral-900 rounded-full p-1 border border-neutral-800">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
                  billingCycle === 'monthly'
                    ? 'bg-white text-black'
                    : 'text-neutral-400 hover:text-white'
                }`}
              >
                Mensual
              </button>
              <button
                onClick={() => setBillingCycle('annual')}
                className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
                  billingCycle === 'annual'
                    ? 'bg-white text-black'
                    : 'text-neutral-400 hover:text-white'
                }`}
              >
                Anual
                <span className="ml-2 text-xs text-phoenix-gold">-20%</span>
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="pb-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {tiers.map((tier, index) => (
              <motion.div
                key={tier.name}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={`relative rounded-2xl p-8 ${
                  tier.popular
                    ? 'bg-gradient-to-b from-phoenix-gold/20 to-neutral-900 border-2 border-phoenix-gold/50'
                    : 'bg-neutral-900 border border-neutral-800'
                }`}
              >
                {tier.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="px-4 py-1 bg-phoenix-gold text-black text-sm font-bold rounded-full">
                      Más Popular
                    </span>
                  </div>
                )}

                <div className="mb-6">
                  <h3 className="text-xl font-bold text-white mb-2">{tier.name}</h3>
                  <p className="text-neutral-400 text-sm">{tier.description}</p>
                </div>

                <div className="mb-6">
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-white">
                      {billingCycle === 'annual' && tier.price !== 'Gratis' && tier.price !== 'Custom'
                        ? '$79'
                        : tier.price}
                    </span>
                    {tier.price !== 'Gratis' && tier.price !== 'Custom' && (
                      <span className="text-neutral-400 text-sm">{tier.priceNote}</span>
                    )}
                  </div>
                  {tier.price === 'Gratis' && (
                    <span className="text-neutral-500 text-sm">{tier.priceNote}</span>
                  )}
                  {tier.price === 'Custom' && (
                    <span className="text-neutral-500 text-sm">{tier.priceNote}</span>
                  )}
                </div>

                <ul className="space-y-3 mb-8">
                  {tier.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-phoenix-gold shrink-0 mt-0.5" />
                      <span className="text-neutral-300 text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                {tier.enterprise ? (
                  <Link
                    href={tier.ctaLink}
                    className="block w-full py-3 px-4 text-center rounded-xl font-medium border border-neutral-700 text-white hover:bg-neutral-800 transition-all"
                  >
                    {tier.cta}
                    <ArrowRight className="inline-block ml-2 h-4 w-4" />
                  </Link>
                ) : tier.priceId ? (
                  <button
                    onClick={() => handleCheckout(tier)}
                    disabled={isLoading === tier.name}
                    className={`w-full py-3 px-4 rounded-xl font-medium transition-all ${
                      tier.popular
                        ? 'bg-phoenix-gold text-black hover:bg-phoenix-gold/90'
                        : 'bg-white text-black hover:bg-neutral-200'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {isLoading === tier.name ? (
                      <span className="flex items-center justify-center">
                        <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                        Procesando...
                      </span>
                    ) : (
                      <>
                        {tier.cta}
                        <ArrowRight className="inline-block ml-2 h-4 w-4" />
                      </>
                    )}
                  </button>
                ) : (
                  <Link
                    href={tier.ctaLink}
                    className="block w-full py-3 px-4 text-center rounded-xl font-medium bg-neutral-800 text-white hover:bg-neutral-700 transition-all"
                  >
                    {tier.cta}
                    <ArrowRight className="inline-block ml-2 h-4 w-4" />
                  </Link>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-20 px-4 border-t border-neutral-800">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            ¿Por qué elegir Aurenix?
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="text-center p-6"
                >
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-phoenix-gold/10 border border-phoenix-gold/30 mb-4">
                    <Icon className="h-7 w-7 text-phoenix-gold" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{benefit.title}</h3>
                  <p className="text-neutral-400 text-sm">{benefit.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* FAQ Teaser */}
      <section className="py-20 px-4 bg-neutral-900/50">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-white mb-4">¿Tienes preguntas?</h2>
          <p className="text-neutral-400 mb-6">
            Nuestro equipo está disponible para ayudarte a elegir el plan perfecto para tu empresa.
          </p>
          <Link
            href="/contact"
            className="inline-flex items-center px-6 py-3 bg-white text-black rounded-xl font-medium hover:bg-neutral-200 transition-all"
          >
            Hablar con Ventas
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-neutral-800">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-neutral-500 text-sm">
            © 2026 Aurenix Agency. Todos los derechos reservados.
          </div>
          <div className="flex items-center gap-6 text-sm">
            <Link href="/legal/terms" className="text-neutral-500 hover:text-white transition-colors">
              Términos de Servicio
            </Link>
            <Link href="/legal/privacy" className="text-neutral-500 hover:text-white transition-colors">
              Política de Privacidad
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
