// src/app/student/[courseId]/page.tsx
'use client';

import React, { useEffect, useState, useRef } from 'react';
import io, { Socket } from 'socket.io-client';
import axios from 'axios';
import { useParams, useRouter } from 'next/navigation';
import SignOutButton from '@/app/components/SignOutButton';
import { API_ENDPOINTS } from '@/app/constants';
import ChatBox from '@/app/components/Chat'; 

interface QueueEntry {
  queue_entry_id: number;
  net_id: string;
  first_name: string;
  last_name: string;
  topic_name: string;
  status: string;
  time_entered: string | null;
}

interface User {
  netId: string;
  firstName?: string;
  lastName?: string;
}

const StudentQueuePage: React.FC = () => {
  const { courseId } = useParams() as { courseId: string };
  const router = useRouter();

  const [queueEntries, setQueueEntries] = useState<QueueEntry[]>([]);
  const [queueActive, setQueueActive] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [topic, setTopic] = useState<string>('');
  const [myEntryId, setMyEntryId] = useState<number | null>(null);
  const [myNetId, setMyNetId] = useState<string>('');
  const [showChat, setShowChat] = useState<boolean>(false);

  const socketRef = useRef<Socket | null>(null);

  const toggleChat = () => {
    setShowChat(prev => !prev);
  };

  // Establish socket & fetch initial data
  useEffect(() => {
    if (!courseId || !myNetId) return;

    const token = localStorage.getItem('jwtToken');
    if (!token) {
      setError('Not authenticated');
      return;
    }

    const socket = io(API_ENDPOINTS.BACKEND_URL, {
      query: { token },
      transports: ['websocket'],
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      socket.emit('join_room', { course_id: courseId });
    });

    socket.on('queue_updated', (data) => {
      setQueueEntries(data.entries);
      const myEntry = data.entries.find((e: any) =>
        e.net_id === myNetId && ['In Queue','In Progress'].includes(e.status)
      );
      setMyEntryId(myEntry ? myEntry.queue_entry_id : null);
    });

    socket.on('queue_status_updated', (data) => {
      setQueueActive(data.is_active);
    });

    socket.on('error', (err: { message: string }) => {
      setError(err.message);
    });

    socket.on('disconnect', (reason: string) => {
      if (reason === 'io server disconnect') {
        setError('Disconnected: authentication failed');
      }
    });

    fetchQueueStatus();
    fetchQueueEntries();

    return () => {
      socket.off('connect');
      socket.off('queue_updated');
      socket.off('queue_status_updated');
      socket.off('error');
      socket.disconnect();
    };
  }, [courseId, myNetId]);

  // Helper to send socket events
  const emit = (event: string, data: any) => {
    if (!socketRef.current) {
      setError('Socket not connected');
      return;
    }
    socketRef.current.emit(event, data);
  };

  // Load user netId
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const token = localStorage.getItem('jwtToken');
        const res = await axios.get<{ auth: boolean; user?: User }>(
          `${API_ENDPOINTS.BACKEND_URL}/check`,
          {
            headers: { 'Authorization': `Bearer ${token}` },
            withCredentials: true,
          }
        );
        if (res.data.auth && res.data.user) {
          setMyNetId(res.data.user.netId);
        }
      } catch (err) {
        console.error('Error fetching user info:', err);
        setError('Failed to load user info.');
      }
    };
    fetchUser();
  }, []);

  const fetchQueueStatus = async () => {
    try {
      const token = localStorage.getItem('jwtToken');
      const res = await axios.get<{ course_id: string; is_active: boolean }>(
        `${API_ENDPOINTS.BACKEND_URL}/queue/course/${courseId}/status`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
          withCredentials: true,
        }
      );
      setQueueActive(res.data.is_active);
    } catch (err) {
      console.error('Error fetching queue status:', err);
    }
  };

  const fetchQueueEntries = async () => {
    try {
      const token = localStorage.getItem('jwtToken');
      const res = await axios.get<QueueEntry[]>(
        `${API_ENDPOINTS.BACKEND_URL}/queue/course/${courseId}/active-entries`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
          withCredentials: true,
        }
      );
      setQueueEntries(res.data);
      const myEntry = res.data.find((entry) =>
        entry.net_id === myNetId &&
        (entry.status === 'In Queue' || entry.status === 'In Progress')
      );
      setMyEntryId(myEntry ? myEntry.queue_entry_id : null);
    } catch (err) {
      console.error('Error fetching queue entries:', err);
    }
  };

  const handleJoinQueue = () => {
    if (!queueActive) {
      setError('Queue is currently paused. Please wait for it to open.');
      return;
    }
    if (topic.trim() === '') {
      setError('Please enter a topic before joining.');
      return;
    }
    emit('student_join_queue', {
      course_id: courseId,
      net_id: myNetId,
      topic_name: topic,
      mode: 'in-person',
    });
    setTopic('');
  };

  const handleLeaveQueue = () => {
    if (myEntryId) {
      emit('student_leave_queue', {
        course_id: courseId,
        queue_entry_id: myEntryId,
      });
    }
  };

  return (
    <div className="min-h-screen bg-[#0e1c2c]/75 text-white p-6 flex flex-col items-center relative">
      <div className="absolute top-4 right-6">
        <SignOutButton />
      </div>

      <h1 className="text-4xl font-bold mb-6">Course Queue for {courseId}</h1>
      {error && <p className="mb-4 text-red-500">{error}</p>}

      {!queueActive ? (
        <div className="mb-6 text-yellow-400 text-center font-semibold">
          The queue is currently paused. Please wait for staff to open it.
        </div>
      ) : myEntryId ? (
        <div className="mb-6 flex flex-col items-center">
          <p className="mb-2">You are currently in the queue!</p>
          <button
            onClick={handleLeaveQueue}
            className="px-6 py-2 bg-red-500 hover:bg-red-600 rounded-xl font-semibold transition"
          >
            Leave Queue
          </button>
        </div>
      ) : (
        <div className="mb-6 flex flex-col items-center">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter your topic"
            className="px-4 py-2 rounded-lg text-black mb-2 w-64"
          />
          <button
            onClick={handleJoinQueue}
            className="px-6 py-2 bg-green-500 hover:bg-green-600 rounded-xl font-semibold transition"
          >
            Join Queue
          </button>
        </div>
      )}

      {queueEntries.length === 0 ? (
        <p>No friends in the queue yet.</p>
      ) : (
        <div className="overflow-x-auto w-full max-w-4xl">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr>
                <th className="border-b border-gray-600 p-3">Name</th>
                <th className="border-b border-gray-600 p-3">NetID</th>
                <th className="border-b border-gray-600 p-3">Topic</th>
                <th className="border-b border-gray-600 p-3">Status</th>
                <th className="border-b border-gray-600 p-3">Joined At</th>
              </tr>
            </thead>
            <tbody>
              {queueEntries.map((entry) => (
                <tr
                  key={entry.queue_entry_id}
                  className={`hover:bg-gray-700 ${
                    entry.net_id === myNetId ? 'bg-blue-900' : ''
                  }`}
                >
                  <td className="p-3">{entry.first_name} {entry.last_name}</td>
                  <td className="p-3">{entry.net_id}</td>
                  <td className="p-3">{entry.topic_name}</td>
                  <td className="p-3">{entry.status}</td>
                  <td className="p-3">
                    {entry.time_entered
                      ? new Date(entry.time_entered).toLocaleString()
                      : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="mt-6 flex gap-4">
        <button
          onClick={() => router.back()}
          className="px-6 py-3 bg-white text-[#0e1c2c] rounded-xl font-semibold hover:bg-gray-200 transition"
        >
          Back
        </button>
        <button
          onClick={toggleChat}
          className="px-6 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition"
        >
          {showChat ? 'Hide Chat' : 'Show Chat'}
        </button>
      </div>

      {showChat && (
        <div className="w-full max-w-4xl mt-4 bg-gray-800 p-4 rounded-lg">
          <ChatBox courseId={courseId} />
        </div>
      )}
    </div>
  );
};

export default StudentQueuePage;
