'use client';

import React, { useEffect, useState } from 'react';
import SignInButton from './components/SignInButton';
import SignOutButton from './components/SignOutButton';
import { API_ENDPOINTS } from './constants';

interface User {
  netId: string;
}

const HomePage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#0e1c2c] text-white px-4 text-center">
      <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold mb-8 leading-tight">
        Welcome to <br className="sm:hidden" />
        <span className="text-[#7ec8e3]">CS Office Hours 2.0</span>
      </h1>

      <p className="text-lg sm:text-xl md:text-2xl mb-12 text-gray-300 max-w-2xl">
        A fresh Yale CS Office Hours experience awaits.
      </p>

      <div className="flex flex-col sm:flex-row gap-6">
        <SignInButton />
        <SignOutButton />
      </div>
    </div>
  );
};

export default HomePage;
