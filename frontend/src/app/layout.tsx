'use client';

import * as React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import "./globals.css";
import dynamic from 'next/dynamic';

// Dynamically import ThreeDBackground with SSR disabled:
const ThreeDBackground = dynamic(() => import('./components/ThreeDBackground'), { ssr: false });


export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <title>CAS App - Yale Blue Edition</title>
      </head>
      <body>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <ThreeDBackground />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
