'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Loader2 } from 'lucide-react';

interface LeadCaptureFormProps {
  source?: string;
}

export function LeadCaptureForm({ source = 'WEBSITE' }: LeadCaptureFormProps) {
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    message: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, source }),
      });

      if (response.ok || response.status === 409) {
        setSubmitted(true);
      } else {
        alert('Error al enviar formulario');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('Error de conexión. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  if (submitted) {
    return (
      <div className='p-8 text-center bg-white/5 border border-white/10 rounded-2xl'>
         <p className="text-xl font-bold mb-2">¡Recibido!</p>
         <p className="text-neutral-400 text-sm">Nuestro equipo te contactará en menos de 24h.</p>
      </div>
    );
  }

  return (
    <Card className="bg-white/5 border-white/10 text-white shadow-2xl">
      <CardHeader>
        <CardTitle>Comienza tu Transformación</CardTitle>
        <CardDescription className="text-neutral-400">
          Analizaremos tus procesos y diseñaremos tu primer Agente gratis.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className='space-y-6'>
          <div className='grid gap-6 md:grid-cols-2'>
            <div className='space-y-2'>
              <Label htmlFor='name'>Nombre</Label>
              <Input
                id='name'
                name='name'
                value={formData.name}
                onChange={handleChange}
                placeholder='Elon Musk'
                required
              />
            </div>

            <div className='space-y-2'>
              <Label htmlFor='email'>Email Profesional</Label>
              <Input
                id='email'
                name='email'
                type='email'
                value={formData.email}
                onChange={handleChange}
                placeholder='ceo@tuempresa.com'
                required
              />
            </div>
          </div>

          <div className='space-y-2'>
            <Label htmlFor='message'>¿Qué te gustaría automatizar?</Label>
            <Textarea
              id='message'
              name='message'
              value={formData.message}
              onChange={handleChange}
              placeholder='Describe una tarea que te quite mucho tiempo...'
              rows={4}
            />
          </div>

          <Button type='submit' className='w-full bg-white text-black hover:bg-neutral-200 py-6 text-lg' disabled={loading}>
            {loading ? <Loader2 className='mr-2 h-4 w-4 animate-spin' /> : 'Solicitar Auditoría de IA'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
