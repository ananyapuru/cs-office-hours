// frontend/src/app/page.tsx
'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import SignInButton from './components/SignInButton';
import SignOutButton from './components/SignOutButton';
import { API_ENDPOINTS } from './constants';

interface User {
  netId: string;
}

const HomePage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>CAS Authentication Demo</h1>
      <SignInButton/>
      <SignOutButton/>
    </div>
  );
};

export default HomePage;
