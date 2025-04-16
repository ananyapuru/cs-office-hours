'use client';

import React, { useEffect, useState, useRef } from 'react';
import io, { Socket } from 'socket.io-client';
import axios from 'axios';
import { API_ENDPOINTS } from '@/app/constants';

interface ChatMessage {
  chat_message_id: number;
  net_id: string;
  first_name: string;
  last_name: string;
  message: string;
  time_sent: string;
}

interface ChatManagementProps {
  courseId: string;
}

const ChatManagement: React.FC<ChatManagementProps> = ({ courseId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [error, setError] = useState('');
  const socketRef = useRef<Socket | null>(null);
    
  const fetchChatMessages = async () => {
  try {
    const token = localStorage.getItem('jwtToken');
    const res = await axios.get<ChatMessage[]>(
      `${API_ENDPOINTS.BACKEND_URL}/chat/course/${courseId}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        withCredentials: true,
      }
    );
    setMessages(res.data);
  } catch (err) {
    console.error('Failed to fetch chat messages', err);
    setError('Unable to load chat');
  }
};


  useEffect(() => {
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
      socket.emit('get_chat_history', { course_id: courseId });
    });

    socket.on('chat_updated', (data: { messages: ChatMessage[] }) => {
      setMessages(data.messages);
    });

    socket.on('error', (err: { message: string }) => {
      setError(err.message);
    });

    socket.on('disconnect', (reason) => {
      if (reason === 'io server disconnect') {
        setError('Disconnected: authentication failed');
      }
    });

      fetchChatMessages();
    return () => {
      socket.off('connect');
      socket.off('chat_updated');
      socket.off('error');
      socket.disconnect();
    };
  }, [courseId]);

  const sendMessage = () => {
    if (!newMessage.trim() || !socketRef.current) return;
    socketRef.current.emit('send_chat_message', {
      course_id: courseId,
      message: newMessage.trim(),
    });
    setNewMessage('');
  };
    
    const handleDeleteMessage = (chatMessageId: number) => {
    if (!socketRef.current) return;

    socketRef.current.emit('staff_delete_message', {
        course_id: courseId,
        chat_message_id: chatMessageId,
    });
};

  return (
    <div className="w-full bg-gray-900 p-4 rounded-lg text-white">
      <h2 className="text-2xl font-bold mb-4">Course Chat (Staff View)</h2>
      {error && <p className="text-red-500">{error}</p>}

      <div className="h-60 overflow-y-auto bg-gray-800 p-3 rounded mb-3 space-y-2">
        {messages.map((msg) => (
        <div key={msg.chat_message_id} className="flex justify-between items-start gap-4">
            <div>
            <span className="font-semibold">{msg.first_name} {msg.last_name}</span>: {msg.message}
            <div className="text-xs text-gray-400">{new Date(msg.time_sent).toLocaleString()}</div>
            </div>

            {/* DELETE BUTTON */}
            <button
            onClick={() => handleDeleteMessage(msg.chat_message_id)}
            className="text-red-400 hover:text-red-600 text-sm"
            >
            Delete
            </button>
        </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          className="flex-grow p-2 bg-gray-700 rounded"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type your message"
        />
        <button
          onClick={sendMessage}
          className="bg-blue-500 px-4 py-2 rounded hover:bg-blue-600"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatManagement;
