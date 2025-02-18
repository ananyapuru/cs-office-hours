// frontend/src/app/goodbye/page.tsx
'use client';

import React from 'react';
import Button from '@mui/material/Button';
import { useRouter } from 'next/navigation';

const GoodbyePage: React.FC = () => {
  const router = useRouter();

  const handleGoHome = () => {
    router.push('/'); // Navigates back to the homepage (localhost:3000/)
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>Goodbye!</h1>
      <p>You have been signed out successfully.</p>
      <Button variant="contained" onClick={handleGoHome}>
        Go to Home
      </Button>
    </div>
  );
};

export default GoodbyePage;
