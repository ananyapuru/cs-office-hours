// frontend/src/app/goodbye/page.tsx
'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { API_ENDPOINTS } from '../constants';

const GoodbyePage: React.FC = () => {
  const router = useRouter();
  const handleGoHome = () => router.push(API_ENDPOINTS.HOME);

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center bg-[#0e1c2c]/75 text-white px-4">
      <h1 className="text-5xl sm:text-6xl font-bold mb-4">Goodbye!</h1>
      <p className="text-lg sm:text-xl mb-8 text-gray-300">
        You have been signed out successfully.
      </p>
      <button
        onClick={handleGoHome}
        className="px-6 py-3 bg-white text-[#0e1c2c] rounded-xl font-semibold hover:bg-gray-200 transition"
      >
        Go to Home
      </button>
    </div>
  );
};

export default GoodbyePage;
