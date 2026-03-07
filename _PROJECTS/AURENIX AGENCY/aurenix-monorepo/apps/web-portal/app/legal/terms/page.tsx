import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export const metadata = {
  title: 'Términos de Servicio | Aurenix',
  description: 'Términos y condiciones de uso de los servicios de Aurenix Agency',
};

export default function TermsPage() {
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
          <h1 className="text-4xl font-bold text-white mb-4">Términos de Servicio</h1>
          <p className="text-neutral-500 mb-8">Última actualización: 10 de enero de 2026</p>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">1. Aceptación de los Términos</h2>
            <p className="text-neutral-300 leading-relaxed">
              Al acceder y utilizar los servicios de Aurenix Agency (&quot;Aurenix&quot;, &quot;nosotros&quot;, &quot;nuestro&quot;),
              usted acepta estar sujeto a estos Términos de Servicio. Si no está de acuerdo con
              alguna parte de estos términos, no podrá acceder al servicio.
            </p>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">2. Descripción del Servicio</h2>
            <p className="text-neutral-300 leading-relaxed mb-4">
              Aurenix proporciona una plataforma de automatización empresarial basada en
              Inteligencia Artificial Agéntica. Nuestros servicios incluyen, pero no se limitan a:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li>Agentes de IA para automatización de procesos empresariales</li>
              <li>Integración con sistemas CRM, calendarios y herramientas de productividad</li>
              <li>Dashboard de control y monitoreo en tiempo real</li>
              <li>APIs para integración personalizada</li>
              <li>Soporte técnico según el plan contratado</li>
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">3. Cuentas de Usuario</h2>
            <p className="text-neutral-300 leading-relaxed mb-4">
              Para utilizar ciertos servicios, debe crear una cuenta. Usted es responsable de:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li>Mantener la confidencialidad de sus credenciales de acceso</li>
              <li>Proporcionar información precisa y actualizada</li>
              <li>Notificarnos inmediatamente sobre cualquier uso no autorizado</li>
              <li>Todo el uso que se haga de su cuenta</li>
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">4. Pagos y Facturación</h2>
            <p className="text-neutral-300 leading-relaxed mb-4">
              Los servicios de pago de Aurenix se facturan de forma anticipada mensual o anualmente.
              Al suscribirse:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li>Se le cobrará automáticamente en cada período de facturación</li>
              <li>Puede cancelar su suscripción en cualquier momento</li>
              <li>Las cancelaciones serán efectivas al final del período pagado actual</li>
              <li>No se realizan reembolsos por períodos parciales no utilizados</li>
              <li>Los precios pueden cambiar con notificación previa de 30 días</li>
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">5. Uso Aceptable</h2>
            <p className="text-neutral-300 leading-relaxed mb-4">
              Usted acepta no utilizar nuestros servicios para:
            </p>
            <ul className="list-disc pl-6 text-neutral-300 space-y-2">
              <li>Actividades ilegales o fraudulentas</li>
              <li>Envío de spam o comunicaciones no solicitadas</li>
              <li>Interferir con la seguridad o integridad del servicio</li>
              <li>Intentar acceder a datos de otros usuarios</li>
              <li>Revender o redistribuir el servicio sin autorización</li>
              <li>Crear contenido que viole derechos de terceros</li>
            </ul>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">6. Propiedad Intelectual</h2>
            <p className="text-neutral-300 leading-relaxed">
              Aurenix retiene todos los derechos de propiedad intelectual sobre la plataforma,
              incluyendo pero no limitado a: código fuente, diseño, algoritmos, marcas y
              documentación. Los contenidos generados por los usuarios siguen siendo propiedad
              de los usuarios. Al usar nuestros servicios, nos otorga una licencia limitada
              para procesar sus datos según sea necesario para proporcionar el servicio.
            </p>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">7. Limitación de Responsabilidad</h2>
            <p className="text-neutral-300 leading-relaxed">
              EN LA MÁXIMA MEDIDA PERMITIDA POR LA LEY APLICABLE, AURENIX NO SERÁ RESPONSABLE
              DE NINGÚN DAÑO INDIRECTO, INCIDENTAL, ESPECIAL, CONSECUENTE O PUNITIVO, NI DE
              NINGUNA PÉRDIDA DE BENEFICIOS O INGRESOS, YA SEA DIRECTA O INDIRECTAMENTE INCURRIDA,
              NI DE NINGUNA PÉRDIDA DE DATOS, USO, FONDO DE COMERCIO U OTRAS PÉRDIDAS
              INTANGIBLES. La responsabilidad total de Aurenix no excederá la cantidad pagada
              por usted en los últimos 12 meses.
            </p>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">8. Indemnización</h2>
            <p className="text-neutral-300 leading-relaxed">
              Usted acepta indemnizar y mantener indemne a Aurenix, sus afiliados, oficiales,
              directores, empleados y agentes de cualquier reclamación, demanda, pérdida o
              daño, incluyendo honorarios legales razonables, que surjan de su uso del servicio
              o cualquier violación de estos términos.
            </p>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">9. Modificaciones</h2>
            <p className="text-neutral-300 leading-relaxed">
              Nos reservamos el derecho de modificar estos términos en cualquier momento.
              Los cambios materiales serán notificados con al menos 30 días de anticipación.
              El uso continuado del servicio después de dichos cambios constituye su
              aceptación de los nuevos términos.
            </p>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">10. Ley Aplicable</h2>
            <p className="text-neutral-300 leading-relaxed">
              Estos términos se regirán e interpretarán de acuerdo con las leyes de España,
              sin referencia a sus disposiciones sobre conflictos de leyes. Cualquier disputa
              estará sujeta a la jurisdicción exclusiva de los tribunales de Madrid, España.
            </p>
          </section>

          <section className="mb-10">
            <h2 className="text-2xl font-semibold text-white mb-4">11. Contacto</h2>
            <p className="text-neutral-300 leading-relaxed">
              Para cualquier pregunta sobre estos Términos de Servicio, puede contactarnos en:
            </p>
            <p className="text-phoenix-gold mt-2">legal@aurenix.agency</p>
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
            <Link href="/legal/privacy" className="text-neutral-500 hover:text-white transition-colors">
              Política de Privacidad
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
