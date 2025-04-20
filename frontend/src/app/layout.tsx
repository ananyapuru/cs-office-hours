'use client';

import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import './globals.css';

import ParticlesBackground from './components/ParticlesBackground';
import WaveFooter from './components/WaveFooter';
import { usePathname } from 'next/navigation';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const showEffects = pathname !== '/bare-route';

  return (
    <html lang="en">
      <head>
        <title>CS Office Hours 2.0</title>
      </head>
      <body className="relative bg-[#0e1c2c]/75 text-white">
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {showEffects && <ParticlesBackground />}
          {showEffects && <WaveFooter />}
          <main className="relative z-10 min-h-screen flex flex-col">
            {children}
          </main>
        </ThemeProvider>
      </body>
    </html>
  );
}
