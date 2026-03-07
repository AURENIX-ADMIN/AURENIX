'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { CheckCircle2, ArrowRight, Sparkles, Loader2, XCircle } from 'lucide-react';
import Link from 'next/link';
import confetti from 'canvas-confetti';

interface SessionData {
  status: string;
  customerEmail?: string;
  subscriptionId?: string;
}

function SuccessContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setError('No session ID found');
      setLoading(false);
      return;
    }

    const fetchSession = async () => {
      try {
        const response = await fetch(`/api/checkout?session_id=${sessionId}`);
        const data = await response.json();

        if (response.ok) {
          setSessionData(data);
          // Trigger confetti on successful load
          if (data.status === 'complete') {
            triggerConfetti();
          }
        } else {
          setError(data.error || 'Failed to load session');
        }
      } catch (err) {
        setError('Error loading session data');
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, [sessionId]);

  const triggerConfetti = () => {
    const count = 200;
    const defaults = {
      origin: { y: 0.7 },
      zIndex: 1000,
    };

    function fire(particleRatio: number, opts: confetti.Options) {
      confetti({
        ...defaults,
        ...opts,
        particleCount: Math.floor(count * particleRatio),
      });
    }

    fire(0.25, { spread: 26, startVelocity: 55, colors: ['#D4AF37', '#FF6B35'] });
    fire(0.2, { spread: 60, colors: ['#D4AF37', '#FF6B35'] });
    fire(0.35, { spread: 100, decay: 0.91, scalar: 0.8, colors: ['#D4AF37', '#FF6B35'] });
    fire(0.1, { spread: 120, startVelocity: 25, decay: 0.92, scalar: 1.2, colors: ['#D4AF37', '#FF6B35'] });
    fire(0.1, { spread: 120, startVelocity: 45, colors: ['#D4AF37', '#FF6B35'] });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-phoenix-gold animate-spin mx-auto mb-4" />
          <p className="text-neutral-400">Verificando tu suscripción...</p>
        </div>
      </div>
    );
  }

  if (error || !sessionData) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <XCircle className="h-16 w-16 text-red-500 mx-auto mb-6" />
          <h1 className="text-2xl font-bold text-white mb-4">Algo salió mal</h1>
          <p className="text-neutral-400 mb-8">
            {error || 'No pudimos verificar tu suscripción. Por favor contacta a soporte.'}
          </p>
          <Link
            href="/pricing"
            className="inline-flex items-center px-6 py-3 bg-white text-black rounded-xl font-medium hover:bg-neutral-200 transition-all"
          >
            Volver a Precios
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="text-center max-w-lg"
      >
        {/* Success Icon */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          className="mb-8"
        >
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-phoenix-gold/20 to-phoenix-orange/20 border border-phoenix-gold/30">
            <CheckCircle2 className="h-12 w-12 text-phoenix-gold" />
          </div>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-3xl md:text-4xl font-bold text-white mb-4"
        >
          ¡Bienvenido a Aurenix!
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-lg text-neutral-400 mb-8"
        >
          Tu suscripción está activa. Es hora de{' '}
          <span className="text-phoenix-gold font-semibold">automatizar y escalar</span>.
        </motion.p>

        {/* Email confirmation */}
        {sessionData.customerEmail && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mb-8 p-4 bg-neutral-900 rounded-xl border border-neutral-800"
          >
            <p className="text-sm text-neutral-500 mb-1">Email de confirmación enviado a:</p>
            <p className="text-white font-medium">{sessionData.customerEmail}</p>
          </motion.div>
        )}

        {/* Next Steps */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mb-10"
        >
          <h3 className="text-sm font-semibold text-neutral-500 uppercase tracking-wider mb-4">
            Próximos Pasos
          </h3>
          <div className="space-y-3 text-left">
            {[
              'Configura tu primer Agente IA',
              'Conecta tus integraciones (CRM, Calendar)',
              'Define tus flujos de trabajo automatizados',
            ].map((step, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-neutral-900/50 rounded-lg border border-neutral-800"
              >
                <div className="w-6 h-6 rounded-full bg-phoenix-gold/20 flex items-center justify-center text-xs font-bold text-phoenix-gold">
                  {index + 1}
                </div>
                <span className="text-neutral-300 text-sm">{step}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center px-8 py-4 bg-phoenix-gold text-black rounded-xl font-semibold hover:bg-phoenix-gold/90 transition-all shadow-lg shadow-phoenix-gold/25"
          >
            <Sparkles className="mr-2 h-5 w-5" />
            Ir al Dashboard
          </Link>
          <Link
            href="/docs/getting-started"
            className="inline-flex items-center justify-center px-8 py-4 bg-neutral-900 text-white rounded-xl font-medium border border-neutral-800 hover:bg-neutral-800 transition-all"
          >
            Ver Guía de Inicio
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </motion.div>
      </motion.div>
    </div>
  );
}

export default function SuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-black flex items-center justify-center">
          <Loader2 className="h-12 w-12 text-phoenix-gold animate-spin" />
        </div>
      }
    >
      <SuccessContent />
    </Suspense>
  );
}
