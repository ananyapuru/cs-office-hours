// src/app/teachingstaff/[courseId]/page.tsx
'use client';

import React, { useEffect, useState, useRef } from 'react';
import io, { Socket } from 'socket.io-client';
import axios from 'axios';
import { useParams, useRouter } from 'next/navigation';
import SignOutButton from '@/app/components/SignOutButton';
import ChatBox from '@/app/components/Chat';
import { API_ENDPOINTS } from '@/app/constants';
import { formatCourseId } from '@/app/utils/formatters';

interface User {
  netId: string;
  firstName?: string;
  lastName?: string;
}

interface QueueEntry {
  queue_entry_id: number;
  net_id: string;
  first_name: string;
  last_name: string;
  topic_name: string;
  status: string;
  time_entered: string | null;
}

export default function QueueManagement() {
  const { courseId } = useParams() as { courseId: string };
  const router = useRouter();
  const role = 'staff';

  const [entries, setEntries] = useState<QueueEntry[]>([]);
  const [active, setActive] = useState(false);
  const [error, setError] = useState('');
  const [user, setUser] = useState<User | null>(null);
  const [showChat, setShowChat] = useState(false);
  const socketRef = useRef<Socket | null>(null);

  const toggleChat = () => setShowChat(v => !v);

  // REST: fetch entries
  const fetchEntries = async () => {
    try {
      const token = localStorage.getItem('jwtToken');
      const res = await axios.get<QueueEntry[]>(
        `${API_ENDPOINTS.BACKEND_URL}/queue/course/${courseId}/active-entries`,
        { headers: { Authorization: `Bearer ${token}` }, withCredentials: true }
      );
      setEntries(res.data);
    } catch {
      setError('Could not load queue entries.');
    }
  };

  // REST: fetch status
  const fetchStatus = async () => {
    try {
      const token = localStorage.getItem('jwtToken');
      const res = await axios.get<{ is_active: boolean }>(
        `${API_ENDPOINTS.BACKEND_URL}/queue/course/${courseId}/status`,
        { headers: { Authorization: `Bearer ${token}` }, withCredentials: true }
      );
      setActive(res.data.is_active);
    } catch {
      /* silent */
    }
  };

  // socket emitter
  const emit = (evt: string, data: any) => {
    if (!socketRef.current) return setError('Socket not connected');
    socketRef.current.emit(evt, data);
  };

  useEffect(() => {
    const token = localStorage.getItem('jwtToken');
    if (!token) {
      setError('Not authenticated');
      return;
    }

    // fetch user
    axios
      .get<{ auth: boolean; user?: User }>(
        `${API_ENDPOINTS.BACKEND_URL}/check`,
        { withCredentials: true }
      )
      .then(r => {
        if (r.data.auth && r.data.user) setUser(r.data.user);
      })
      .catch(() => setError('Failed to fetch user'));

    // connect socket
    const socket = io(API_ENDPOINTS.BACKEND_URL, {
      query: { token },
      transports: ['websocket'],
    });
    socketRef.current = socket;

    socket.on('connect', () => socket.emit('join_room', { course_id: courseId }));
    socket.on('queue_updated', (d: any) => setEntries(d.entries));
    socket.on('queue_status_updated', (d: any) => setActive(d.is_active));
    socket.on('error', (e: { message: string }) => setError(e.message));
    socket.on('disconnect', reason => {
      if (reason === 'io server disconnect') setError('Disconnected: auth failed');
    });

    fetchStatus();
    fetchEntries();

    return () => {
      socket.off('connect');
      socket.off('queue_updated');
      socket.off('queue_status_updated');
      socket.off('error');
      socket.disconnect();
    };
  }, [courseId]);

  // staff actions
  const toggleQueue = (on: boolean) => {
    setActive(on);
    emit('staff_toggle_queue', { course_id: courseId, is_active: on });
  };
  const clearQueue = () => emit('staff_clear_queue', { course_id: courseId });
  const updateStatus = (id: number, status: string) => {
    if (!user) return setError('User not loaded');
    emit('staff_update_entry', {
      course_id: courseId,
      queue_entry_id: id,
      new_status: status,
      staff_net_id: user.netId,
    });
  };
  const removeEntry = (id: number) =>
    emit('staff_remove_entry', { course_id: courseId, queue_entry_id: id });

  return (
    <div className="
        min-h-screen w-full
        bg-[#0e1c2c]/75 text-white
        p-6 flex flex-col items-center relative
        overflow-y-auto overflow-x-hidden
      ">
      {/* Sign out */}
      <div className="absolute top-4 right-6">
        <SignOutButton />
      </div>

      <h1 className="text-4xl font-bold mb-6">
        {formatCourseId(courseId)} Queue ({role})
      </h1>

      {error && <p className="mb-4 text-red-500">{error}</p>}

      {/* Controls */}
      <div className="flex gap-4 mb-6">
        {active ? (
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

      {/* Entries */}
      {entries.length === 0 ? (
        <p>No students in the queue yet.</p>
      ) : (
        <ul className="w-full max-w-2xl">
          {entries.map(e => (
            <li
              key={e.queue_entry_id}
              className="p-4 border-b border-gray-600 flex justify-between items-center"
            >
              <div>
                <strong>{e.net_id}</strong> – {e.topic_name} – <em>{e.status}</em>
                <br />
                <small>Joined at: {e.time_entered || 'N/A'}</small>
              </div>
              <div className="flex gap-2 items-center">
                <select
                  value={e.status}
                  onChange={evt => updateStatus(e.queue_entry_id, evt.target.value)}
                  className="p-2 rounded bg-gray-800 border border-gray-600"
                >
                  <option>In Queue</option>
                  <option>In Progress</option>
                  <option>Completed</option>
                </select>
                <button
                  onClick={() => removeEntry(e.queue_entry_id)}
                  className="px-4 py-2 bg-red-600 rounded hover:bg-red-700"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* Bottom bar: Back + Chat toggle */}
      <div className="mt-8 flex gap-4">
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

      {/* Chat window */}
      {showChat && (
        <div className="w-full max-w-4xl mt-4 bg-gray-800 p-4 rounded-lg">
          <ChatBox courseId={courseId} />
        </div>
      )}
    </div>
  );
}
