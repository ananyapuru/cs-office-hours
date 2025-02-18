// frontend/src/app/page.tsx
'use client';

import React from 'react';
import SignInButton from './components/SignInButton';
import SignOutButton from './components/SignOutButton';

const HomePage: React.FC = () => {
  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>CAS Authentication Demo</h1>
      <div style={{ marginBottom: '1rem' }}>
        <SignInButton />
      </div>
      <div>
        <SignOutButton />
      </div>
    </div>
  );
};

export default HomePage;
