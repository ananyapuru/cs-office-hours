'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { API_ENDPOINTS } from '../constants';
import SignOutButton from '../components/SignOutButton';

interface User {
    netId: string;
    firstName?: string;
    lastName?: string;
}

const SuperuserPage: React.FC = () => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const fetchUser = async () => {
            try {
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

    if (loading) return <p>Loading...</p>;
    if (!user) return <p>You are not logged in.</p>;

    const firstName = user.firstName ? `${user.firstName}` : user.netId;

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-[#0e1c2c] text-white text-center px-4">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6">
                Hey {firstName}, welcome to the Superuser page!
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-gray-300 max-w-2xl mb-12">
                Here you can add, delete, and manage instructors/admins for all courses.
            </p>

            <button
                onClick={() => router.push('/superuser/manage-admin')}
                className="mb-6 px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold hover:bg-gray-200 transition"
            >
                Manage Admin
            </button>

            {/* Back Button */}
            <button
                onClick={() => router.push('/welcome')}
                className="mb-6 px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold hover:bg-gray-200 transition"
            >
                Back to Welcome Page
            </button>

            <SignOutButton />
        </div>
    );
};

export default SuperuserPage;
