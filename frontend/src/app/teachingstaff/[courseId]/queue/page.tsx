'use client';

import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import { useParams, useRouter } from 'next/navigation';
import { API_ENDPOINTS } from '@/app/constants';
import SignOutButton from '@/app/components/SignOutButton';
import { formatCourseId } from '@/app/utils/formatters';

const socket = io(API_ENDPOINTS.BACKEND_URL);

interface QueueEntry {
    queue_entry_id: number;
    net_id: string;
    first_name: string;
    last_name: string;
    topic_name: string;
    status: string;
    time_entered: string | null;
}




const StaffQueuePage: React.FC = () => {
    const { courseId } = useParams() as { courseId: string };
    const router = useRouter();
    const [queueEntries, setQueueEntries] = useState<QueueEntry[]>([]);
    const [queueActive, setQueueActive] = useState<boolean>(false);
    const [error, setError] = useState<string>('');

    const fetchQueueEntries = async () => {
        try {
            const res = await axios.get<QueueEntry[]>(
                `${API_ENDPOINTS.BACKEND_URL}/queue/course/${courseId}/entries`,
                { withCredentials: true }
            );
            setQueueEntries(res.data);
        } catch (err) {
            console.error('Error fetching queue entries:', err);
        }
    };


    useEffect(() => {
        if (!courseId) return;

        socket.emit('join_room', { course_id: courseId });

        socket.on('queue_updated', (data) => {
            setQueueEntries(data.entries);
        });

        socket.on('queue_status_updated', (data) => {
            setQueueActive(data.is_active); // 🛠 Update instantly when queue status changes
        });

        socket.on('error', (data) => {
            setError(data.message);
        });

        fetchQueueStatus();
        fetchQueueEntries();

        return () => {
            socket.off('queue_updated');
            socket.off('queue_status_updated'); // 🛠 Clean up
            socket.off('error');
        };
    }, [courseId]);



    const fetchQueueStatus = async () => {
        try {
            const res = await axios.get<{ course_id: string; is_active: boolean }>(
                `${API_ENDPOINTS.BACKEND_URL}/queue/course/${courseId}/status`,
                { withCredentials: true }
            );
            setQueueActive(res.data.is_active);
        } catch (err) {
            console.error('Error fetching queue status:', err);
        }
    };

    const toggleQueue = (active: boolean) => {
        setQueueActive(active); // Optimistic update
        socket.emit('staff_toggle_queue', {
            course_id: courseId,
            is_active: active,
        });
    };




    const clearQueue = async () => {
        try {
            await axios.delete(
                `${API_ENDPOINTS.BACKEND_URL}/queue/course/${courseId}/clear`,
                { withCredentials: true }
            );
        } catch (err) {
            console.error('Error clearing queue:', err);
        }
    };

    return (
        <div className="min-h-screen bg-[#0e1c2c] text-white p-6 flex flex-col items-center relative">
            <div className="absolute top-4 right-6">
                <SignOutButton />
            </div>

            <h1 className="text-4xl font-bold mb-6">
                {formatCourseId(courseId)} Queue (Teaching Staff View)
            </h1>

            {error && <p className="text-red-500">{error}</p>}

            <div className="flex gap-4 mb-6">
                {queueActive ? (
                    <button
                        onClick={() => toggleQueue(false)}
                        className="px-6 py-3 bg-yellow-400 text-[#0e1c2c] rounded-xl font-bold hover:bg-yellow-500"
                    >
                        Pause Queue
                    </button>
                ) : (
                    <button
                        onClick={() => toggleQueue(true)}
                        className="px-6 py-3 bg-green-500 text-white rounded-xl font-bold hover:bg-green-600"
                    >
                        Start Queue
                    </button>
                )}
                <button
                    onClick={clearQueue}
                    className="px-6 py-3 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700"
                >
                    Clear Queue
                </button>
            </div>

            {queueEntries.length === 0 ? (
                <p>No students in the queue yet.</p>
            ) : (
                <ul className="w-full max-w-2xl">
                    {queueEntries.map((entry) => (
                        <li key={entry.queue_entry_id} className="p-4 border-b border-gray-600">
                            <strong>{entry.net_id}</strong> - {entry.topic_name} - <em>{entry.status}</em>
                            <br />
                            <small>Joined at: {entry.time_entered}</small>
                        </li>
                    ))}
                </ul>
            )}

            <button
                onClick={() => router.back()}
                className="mt-8 px-6 py-3 bg-white text-[#0e1c2c] rounded-xl font-semibold hover:bg-gray-200 transition"
            >
                Back
            </button>
        </div>
    );
};

export default StaffQueuePage;
