// frontend/src/app/welcome/page.tsx
'use client';

import React, { useEffect, useState } from 'react';
// import axios from '../utils/axios';
import axios from 'axios';
import SignOutButton from '../components/SignOutButton';
import { API_ENDPOINTS } from '../constants';

interface User {
  netId: string;
}

const WelcomePage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        // Optional: wait 100ms (remove if not needed)
        await new Promise((resolve) => setTimeout(resolve, 100));
        const checkUrl = `${API_ENDPOINTS.BACKEND_URL}/check`;
        const res = await axios.get<{ auth: boolean; user?: User }>(checkUrl, {
          withCredentials: true,
        });

        if (res.data.auth && res.data.user) {
          setUser(res.data.user);
        } else {
          setUser(null);
        }
      } catch (error) {
        console.error('Error checking auth:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
  
    fetchUser();
  }, []);
  

  if (loading) return <p>Loading...</p>;
  if (!user) return <p>You are not logged in.</p>;

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>Hello {user.netId}, nice to meet you!</h1>
      <SignOutButton />
    </div>
  );
};

export default WelcomePage;
