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
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#0e1c2c] text-white px-4">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6 text-center">
          Hello {user.firstName && user.lastName ? `${user.firstName} ${user.lastName}` : user.netId}, nice to meet you!
        </h1>

        <div className="flex flex-wrap gap-4 mt-4 justify-center">
          <button
            className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-200 transition"
            disabled={!roles.isStudent}
          >
            Student
          </button>
          <button
            className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-200 transition"
            disabled={!roles.isULA}
          >
            Teaching Staff
          </button>
          <button
            className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-200 transition"
            disabled={!roles.isAdmin}
          >
            Instructor
          </button>
          <button
            className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-200 transition"
            disabled={!roles.isSuperuser}
          >
            Superuser
          </button>
        </div>

        <div className="mt-10">
          <SignOutButton />
        </div>
      </div>
    );
  };


export default WelcomePage;
