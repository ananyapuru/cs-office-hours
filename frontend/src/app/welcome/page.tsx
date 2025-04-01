'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
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
  const [greetingIndex, setGreetingIndex] = useState(0);
  const [typedGreeting, setTypedGreeting] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const router = useRouter();

  const greetings = ['Hello', 'Bonjour', 'Hola', 'Ciao', 'नमस्ते', 'こんにちは', '안녕하세요', 'مرحبا', 'Hej', 'Salut'];

  // Typewriter effect
  useEffect(() => {
    let typingTimeout: NodeJS.Timeout;
    const currentGreeting = greetings[greetingIndex];

    if (isDeleting) {
      typingTimeout = setTimeout(() => {
        setTypedGreeting((prev) => prev.slice(0, -1));
      }, 50);
    } else {
      typingTimeout = setTimeout(() => {
        setTypedGreeting((prev) => currentGreeting.slice(0, prev.length + 1));
      }, 100);
    }

    // When finished typing
    if (!isDeleting && typedGreeting === currentGreeting) {
      setTimeout(() => setIsDeleting(true), 2000); // pause before deleting
    }

    // When finished deleting
    if (isDeleting && typedGreeting === '') {
      setIsDeleting(false);
      setGreetingIndex((prev) => (prev + 1) % greetings.length);
    }

    return () => clearTimeout(typingTimeout);
  }, [typedGreeting, isDeleting, greetingIndex]);

  // Fetch user
  useEffect(() => {
    const fetchUser = async () => {
      try {
        await new Promise((resolve) => setTimeout(resolve, 100));
        const res = await axios.get<{ auth: boolean; user?: User }>(
          `${API_ENDPOINTS.BACKEND_URL}/check`,
          { withCredentials: true }
        );
        setUser(res.data.auth ? res.data.user ?? null : null);
      } catch (error) {
        console.error('Error checking auth:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  // Fetch roles
  useEffect(() => {
    if (!user) return;
    const fetchRoles = async () => {
      try {
        const res = await axios.get<Roles>(
          `${API_ENDPOINTS.BACKEND_URL}/person/${user.netId}/roles`,
          { withCredentials: true }
        );
        setRoles(res.data);
      } catch (error) {
        console.error('Error fetching roles:', error);
      }
    };

    fetchRoles();
  }, [user]);

  if (loading) return <p>Loading...</p>;
  if (!user) return <p>You are not logged in.</p>;

  const nameDisplay = user.firstName || user.netId;

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center bg-[#0e1c2c] text-white px-4">
      <div className="absolute top-6 right-10">
        <SignOutButton />
      </div>
      <h1
        className="text-4xl sm:text-5xl md:text-6xl mb-6 text-center font-light"
        style={{ fontFamily: 'Avenir, sans-serif' }}
      >
        <span className="font-bold text-yellow-300 whitespace-nowrap">
          {typedGreeting}
          <span className="blinking-cursor"></span>
        </span>{' '}
        {nameDisplay}, nice to meet you!
      </h1>
  
      {/* Role Buttons */}
      <div className="flex flex-wrap gap-4 mt-4 justify-center">
        <button
          className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-200 transition"
          disabled={!roles.isStudent}
        >
          Student
        </button>
        <button
          className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-200 transition"
          disabled={!roles.isULA && !roles.isAdmin}
        >
          Teaching Staff
        </button>
        <button
          className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-200 transition"
          disabled={!roles.isAdmin}
          onClick={() => router.push('/instructor')}
        >
          Instructor
        </button>
        <button
          onClick={() => router.push('/superuser')}
          className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-200 transition"
          disabled={!roles.isSuperuser}
        >
          Superuser
        </button>
      </div>
    </div>
  );
  
};

export default WelcomePage;
