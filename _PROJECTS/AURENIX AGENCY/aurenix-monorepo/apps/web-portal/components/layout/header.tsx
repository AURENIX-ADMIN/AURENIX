'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Menu, X } from 'lucide-react';
import { SignInButton, SignUpButton, UserButton, useUser } from '@clerk/nextjs';
import { motion, AnimatePresence } from 'framer-motion';

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const { isSignedIn } = useUser();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 z-50 w-full transition-all duration-300 ${
        isScrolled ? 'bg-black/80 backdrop-blur-md border-b border-white/10' : 'bg-transparent'
      }`}
    >
      <div className='max-w-7xl mx-auto flex h-20 items-center justify-between px-4'>
        <Link href='/' className='text-2xl font-bold tracking-tighter text-white'>
          AURENIX
        </Link>

        <nav className='hidden md:flex items-center space-x-8'>
          <Link href='/#who' className='text-sm text-neutral-400 hover:text-white transition-colors'>Empresas</Link>
          <Link href='/#features' className='text-sm text-neutral-400 hover:text-white transition-colors'>Soluciones</Link>
          <Link href='/marketplace' className='text-sm text-neutral-400 hover:text-white transition-colors'>Marketplace</Link>
          <Link href='/demo' className='text-sm text-neutral-400 hover:text-white transition-colors'>Demo</Link>
        </nav>

        <div className='flex items-center space-x-4'>
          {isSignedIn ? (
            <>
              <Link href="/dashboard" className="text-sm text-neutral-400 hover:text-white">Dashboard</Link>
              <UserButton afterSignOutUrl="/" />
            </>
          ) : (
            <>
              <div className="hidden md:block">
                <SignInButton mode="modal">
                  <button className="text-sm text-neutral-400 hover:text-white mr-4">Entrar</button>
                </SignInButton>
              </div>
              <SignUpButton mode="modal">
                <Button size="sm" className="bg-white text-black hover:bg-neutral-200 rounded-full px-6">
                  Empezar
                </Button>
              </SignUpButton>
            </>
          )}

          <button className='md:hidden text-white' onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className='md:hidden bg-black border-b border-white/10'
          >
            <nav className='flex flex-col p-6 space-y-4'>
               <Link href='/#who' onClick={() => setIsMenuOpen(false)} className='text-lg text-neutral-400'>Empresas</Link>
               <Link href='/#features' onClick={() => setIsMenuOpen(false)} className='text-lg text-neutral-400'>Soluciones</Link>
               <Link href='/marketplace' onClick={() => setIsMenuOpen(false)} className='text-lg text-neutral-400'>Marketplace</Link>
               <Link href='/demo' onClick={() => setIsMenuOpen(false)} className='text-lg text-neutral-400'>Demo</Link>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
