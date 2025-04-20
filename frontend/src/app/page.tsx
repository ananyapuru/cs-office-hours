// src/app/page.tsx
'use client';

import React, { useEffect, useState } from 'react';
import SignInButton from './components/SignInButton';
import SignOutButton from './components/SignOutButton';
import { API_ENDPOINTS } from './constants';

interface User { netId: string; }

export default function HomePage() {
  const [user, setUser] = useState<User | null>(null);

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#0e1c2c]/75 text-white flex items-center justify-center px-4 text-center">
      <div className="curtain-left" />
      <div className="curtain-right" />
      <div className="relative z-10 fade-pop">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold mb-6 leading-tight animate-float">
          Welcome to <br className="sm:hidden" />
          <span className="shimmer">CS Office Hours 2.0</span>
        </h1>

        <p className="text-lg sm:text-xl md:text-2xl mb-10 text-gray-300 max-w-xl mx-auto">
          A fresh Yale CS Office Hours experience awaits.
        </p>

        <div className="flex flex-col sm:flex-row gap-6 justify-center">
          <SignInButton />
          <SignOutButton />
        </div>
      </div>
    </div>
  );
}
