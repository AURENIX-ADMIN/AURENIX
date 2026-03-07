export function Footer() {
  return (
    <footer className="bg-black border-t border-white/10 py-20">
      <div className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-12">
        <div className="space-y-4">
          <h3 className="text-xl font-bold">AURENIX</h3>
          <p className="text-sm text-neutral-500 max-w-xs">
            Personal AI Agentes para la automatización empresarial de vanguardia.
          </p>
        </div>
        
        <div className="space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-widest text-neutral-400">Plataforma</h4>
          <ul className="space-y-2">
            <li><a href="#" className="text-sm text-neutral-500 hover:text-white transition-colors">Vanguard OS</a></li>
            <li><a href="#" className="text-sm text-neutral-500 hover:text-white transition-colors">Marketplace</a></li>
            <li><a href="#" className="text-sm text-neutral-500 hover:text-white transition-colors">Ecosistema</a></li>
          </ul>
        </div>

        <div className="space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-widest text-neutral-400">Agencia</h4>
          <ul className="space-y-2">
            <li><a href="#" className="text-sm text-neutral-500 hover:text-white transition-colors">Servicios</a></li>
            <li><a href="#" className="text-sm text-neutral-500 hover:text-white transition-colors">Casos de Éxito</a></li>
            <li><a href="#" className="text-sm text-neutral-500 hover:text-white transition-colors">Contacto</a></li>
          </ul>
        </div>

        <div className="space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-widest text-neutral-400">Legal</h4>
          <ul className="space-y-2">
            <li><a href="#" className="text-sm text-neutral-500 hover:text-white transition-colors">Privacidad</a></li>
            <li><a href="#" className="text-sm text-neutral-500 hover:text-white transition-colors">Términos</a></li>
          </ul>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 mt-20 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
        <p className="text-xs text-neutral-600">© 2025 AURENIX AGENCY. Todos los derechos reservados.</p>
        <p className="text-xs text-neutral-700 uppercase tracking-widest">Built for the future</p>
      </div>
    </footer>
  );
}
