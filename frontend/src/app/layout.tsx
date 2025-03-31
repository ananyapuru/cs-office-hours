// frontend/src/app/layout.tsx
'use client';

import * as React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import './globals.css';
import dynamic from 'next/dynamic';
import { usePathname } from 'next/navigation';

const ThreeDBackground = dynamic(() => import('./components/ThreeDBackground'), { ssr: false });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const shouldShowBackground = pathname !== '/welcome';

  return (
    <html lang="en">
      <head>
        <title>CAS App - Yale Blue Edition</title>
      </head>
      <body className="bg-[#0e1c2c] text-white">
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {shouldShowBackground && <ThreeDBackground />}
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
