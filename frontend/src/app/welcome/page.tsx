// frontend/src/app/welcome/page.tsx
'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import SignOutButton from '../components/SignOutButton';
import { API_ENDPOINTS } from '../constants';

interface User {
  netId: string;
  firstName?: string;
  lastName?: string;
}

interface Roles {
  isStudent: boolean;
  isULA: boolean;
  isAdmin: boolean;
  isSuperuser: boolean;
}


const WelcomePage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [roles, setRoles] = useState<Roles>({
    isStudent: false,
    isULA: false,
    isAdmin: false,
    isSuperuser: false,
  });

  const [loading, setLoading] = useState(true);

  // Get the user
  useEffect(() => {
    const fetchUser = async () => {
      try {
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


  // Get the user roles
  useEffect(() => {
    if (!user) return;
  
    const fetchRoles = async () => {
      try {
        const rolesUrl = `${API_ENDPOINTS.BACKEND_URL}/person/${user.netId}/roles`;
        const res = await axios.get<Roles>(rolesUrl, { withCredentials: true });
        setRoles(res.data);
      } catch (error) {
        console.error("Error fetching roles:", error);
      }
    };
  
    fetchRoles();
  }, [user]);
  
  

  if (loading) return <p>Loading...</p>;
  if (!user) return <p>You are not logged in.</p>;

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>
        Hello {user.firstName && user.lastName ? `${user.firstName} ${user.lastName}` : user.netId}, nice to meet you!
      </h1>
      <SignOutButton />

      <div style={{ marginTop: '1rem' }}>
      {roles.isStudent && <button>Student</button>}
      {roles.isULA && <button>Teaching Staff</button>}
      {roles.isAdmin && <button>Instructor</button>}
      {roles.isSuperuser && <button>Superuser</button>}
    </div>

    </div>
  );
};

export default WelcomePage;
