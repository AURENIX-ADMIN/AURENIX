import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export const metadata = {
  title: 'Política de Privacidad | Aurenix',
  description: 'Información sobre cómo Aurenix Agency recopila, usa y protege sus datos personales',
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-white">
            Aurenix<span className="text-phoenix-gold">.</span>
          </Link>
          <Link
            href="/"
            className="flex items-center text-neutral-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Link>
        </div>
      </nav>

      {/* Content */}
      <main className="pt-24 pb-16 px-4">
        <article className="max-w-4xl mx-auto prose prose-invert prose-neutral">
          <h1 className="text-4xl font-bold text-white mb-4">Política de Privacidad</h1>
          <p className="text-neutral-500 mb-8">Última actualización: 10 de enero de 2026</p>

          <div className="bg-phoenix-gold/10 border border-phoenix-gold/30 rounded-xl p-6 mb-10">
            <p className="text-phoenix-gold font-medium mb-2">Compromiso con su Privacidad</p>
            <p className="text-neutral-300">
              En Aurenix, la privacidad de nuestros usuarios es una prioridad fundamental.
              Esta política describe cómo recopilamos, usamos y protegemos su información
              personal de acuerdo con el Reglamento General de Protección de Datos (RGPD)
              y otras normativas aplicables.
            </p>
          </div>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">1. Responsable del Tratamiento</h2>
            <p className="text-neutral-300 leading-relaxed">
              El responsable del tratamiento de sus datos personales es:
            </p>
            <div className="bg-neutral-900 rounded-lg p-4 mt-4 text-neutral-300">
              <p><strong className="text-white">Aurenix Agency</strong></p>
              <p>Email: privacy@aurenix.agency</p>
              <p>Domicilio: Madrid, España</p>
            </div>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">2. Datos que Recopilamos</h2>
            <p className="text-neutral-300 leading-relaxed mb-4">
              Recopilamos los siguientes tipos de información:
            </p>
            
            <h3 className="text-lg font-semibold text-white mt-6 mb-2">2.1 Datos proporcionados directamente</h3>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li>Nombre y apellidos</li>
              <li>Dirección de correo electrónico</li>
              <li>Número de teléfono (opcional)</li>
              <li>Información de la empresa</li>
              <li>Datos de facturación y pago</li>
            </ul>

            <h3 className="text-lg font-semibold text-white mt-6 mb-2">2.2 Datos recopilados automáticamente</h3>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li>Dirección IP y ubicación geográfica aproximada</li>
              <li>Tipo de navegador y dispositivo</li>
              <li>Páginas visitadas y patrones de uso</li>
              <li>Datos de rendimiento y logs del servicio</li>
            </ul>

            <h3 className="text-lg font-semibold text-white mt-6 mb-2">2.3 Datos de integraciones</h3>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li>Datos de CRM (contactos, deals) cuando conecta integraciones</li>
              <li>Datos de calendario (eventos, disponibilidad)</li>
              <li>Contenido de correos procesados por los agentes IA</li>
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">3. Finalidades del Tratamiento</h2>
            <p className="text-neutral-300 leading-relaxed mb-4">
              Utilizamos sus datos para:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li><strong className="text-white">Prestación del servicio:</strong> Ejecutar los agentes IA y proporcionar las funcionalidades contratadas</li>
              <li><strong className="text-white">Facturación:</strong> Gestionar pagos y suscripciones</li>
              <li><strong className="text-white">Comunicaciones:</strong> Enviar notificaciones del servicio y, con su consentimiento, información comercial</li>
              <li><strong className="text-white">Mejora del servicio:</strong> Analizar el uso para mejorar nuestros productos</li>
              <li><strong className="text-white">Seguridad:</strong> Prevenir fraudes y proteger la plataforma</li>
              <li><strong className="text-white">Cumplimiento legal:</strong> Cumplir con obligaciones legales y fiscales</li>
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">4. Base Legal del Tratamiento</h2>
            <p className="text-neutral-300 leading-relaxed mb-4">
              El tratamiento de sus datos se basa en:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li><strong className="text-white">Ejecución de contrato:</strong> Para la prestación de los servicios contratados (Art. 6.1.b RGPD)</li>
              <li><strong className="text-white">Interés legítimo:</strong> Para la mejora del servicio y seguridad (Art. 6.1.f RGPD)</li>
              <li><strong className="text-white">Consentimiento:</strong> Para comunicaciones comerciales (Art. 6.1.a RGPD)</li>
              <li><strong className="text-white">Obligación legal:</strong> Para el cumplimiento de requisitos fiscales (Art. 6.1.c RGPD)</li>
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">5. Procesamiento de IA</h2>
            <div className="bg-neutral-900 rounded-lg p-6 border border-neutral-800">
              <p className="text-neutral-300 leading-relaxed mb-4">
                Los agentes de IA de Aurenix procesan datos para automatizar tareas empresariales.
                Es importante saber que:
              </p>
              <ul className="list-disc pl-6 text-neutral-300 space-y-2">
                <li>Sus datos se procesan en servidores seguros con cifrado en tránsito y en reposo</li>
                <li>No vendemos ni compartimos sus datos con terceros para fines comerciales</li>
                <li>Los modelos de IA no se entrenan con sus datos específicos sin consentimiento explícito</li>
                <li>Puede solicitar que ciertos datos no sean procesados por IA</li>
              </ul>
            </div>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">6. Conservación de Datos</h2>
            <p className="text-neutral-300 leading-relaxed">
              Conservamos sus datos durante el tiempo necesario para cumplir con las
              finalidades descritas, y posteriormente durante los plazos legales establecidos:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2 mt-4">
              <li><strong className="text-white">Datos de cuenta:</strong> Durante la relación contractual + 5 años</li>
              <li><strong className="text-white">Datos de facturación:</strong> 6 años (obligación fiscal)</li>
              <li><strong className="text-white">Logs del servicio:</strong> 2 años</li>
              <li><strong className="text-white">Cookies analíticas:</strong> 13 meses</li>
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">7. Sus Derechos</h2>
            <p className="text-neutral-300 leading-relaxed mb-4">
              Conforme al RGPD, usted tiene derecho a:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li><strong className="text-white">Acceso:</strong> Obtener confirmación sobre si tratamos sus datos y acceder a ellos</li>
              <li><strong className="text-white">Rectificación:</strong> Corregir datos inexactos o incompletos</li>
              <li><strong className="text-white">Supresión:</strong> Solicitar la eliminación de sus datos (&quot;derecho al olvido&quot;)</li>
              <li><strong className="text-white">Oposición:</strong> Oponerse al tratamiento de sus datos</li>
              <li><strong className="text-white">Portabilidad:</strong> Recibir sus datos en un formato estructurado</li>
              <li><strong className="text-white">Limitación:</strong> Solicitar la limitación del tratamiento</li>
              <li><strong className="text-white">Retirar consentimiento:</strong> En cualquier momento, sin efecto retroactivo</li>
            </ul>
            <p className="text-neutral-300 mt-4">
              Para ejercer estos derechos, contacte a: <span className="text-phoenix-gold">privacy@aurenix.agency</span>
            </p>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">8. Transferencias Internacionales</h2>
            <p className="text-neutral-300 leading-relaxed">
              Algunos de nuestros proveedores de servicios (como Google Cloud, Stripe) pueden
              procesar datos fuera del Espacio Económico Europeo. En estos casos, garantizamos
              la protección de sus datos mediante:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2 mt-4">
              <li>Cláusulas contractuales tipo aprobadas por la Comisión Europea</li>
              <li>Decisiones de adecuación de la UE donde apliquen</li>
              <li>Certificaciones como SOC 2 Tipo II e ISO 27001</li>
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">9. Cookies</h2>
            <p className="text-neutral-300 leading-relaxed mb-4">
              Utilizamos cookies para mejorar su experiencia. Los tipos de cookies que usamos son:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li><strong className="text-white">Esenciales:</strong> Necesarias para el funcionamiento del sitio</li>
              <li><strong className="text-white">Analíticas:</strong> Para entender cómo se usa el sitio (con su consentimiento)</li>
              <li><strong className="text-white">De funcionalidad:</strong> Para recordar sus preferencias</li>
            </ul>
            <p className="text-neutral-300 mt-4">
              Puede gestionar sus preferencias de cookies en cualquier momento.
            </p>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">10. Seguridad</h2>
            <p className="text-neutral-300 leading-relaxed">
              Implementamos medidas de seguridad técnicas y organizativas para proteger sus datos,
              incluyendo:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2 mt-4">
              <li>Cifrado AES-256 para datos en reposo</li>
              <li>TLS 1.3 para datos en tránsito</li>
              <li>Autenticación multifactor</li>
              <li>Auditorías de seguridad periódicas</li>
              <li>Aislamiento multi-tenant a nivel de base de datos</li>
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">11. Cambios en esta Política</h2>
            <p className="text-neutral-300 leading-relaxed">
              Podemos actualizar esta Política de Privacidad periódicamente. Los cambios
              significativos serán notificados por correo electrónico o mediante un aviso
              destacado en nuestro sitio web.
            </p>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">12. Contacto y Reclamaciones</h2>
            <p className="text-neutral-300 leading-relaxed">
              Para cualquier consulta sobre esta política o para ejercer sus derechos:
            </p>
            <p className="text-phoenix-gold mt-2 mb-4">privacy@aurenix.agency</p>
            <p className="text-neutral-300 leading-relaxed">
              Si considera que sus derechos no han sido atendidos satisfactoriamente,
              puede presentar una reclamación ante la Agencia Española de Protección de Datos (AEPD):
              <a href="https://www.aepd.es" className="text-phoenix-gold ml-1 hover:underline" target="_blank" rel="noopener noreferrer">
                www.aepd.es
              </a>
            </p>
          </section>
        </article>
      </main>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-neutral-800">
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-neutral-500 text-sm">
            © 2026 Aurenix Agency. Todos los derechos reservados.
          </div>
          <div className="flex items-center gap-6 text-sm">
            <Link href="/legal/terms" className="text-neutral-500 hover:text-white transition-colors">
              Términos de Servicio
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
