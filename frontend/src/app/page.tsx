// src/app/page.tsx
'use client';
import React from 'react';
import SignInButton from './components/SignInButton';
import SignOutButton from './components/SignOutButton';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 text-center z-10">
      <h1 className="text-6xl font-extrabold mb-8 leading-tight text-[#7ec8e3]">
        CS Office Hours 2.0
      </h1>
      <p className="text-2xl mb-12 text-gray-300 max-w-xl">
        A fresh Yale CS Office Hours experience awaits.
      </p>
      <div className="flex gap-6">
        <SignInButton />
        <SignOutButton />
      </div>
    </div>
  );
}
