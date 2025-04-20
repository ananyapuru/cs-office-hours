'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import QueueManagement from '@/app/components/QueueManagement';
import ChatManagement from '@/app/components/ChatManagement';


const StaffQueuePage: React.FC = () => {
  const { courseId } = useParams() as { courseId: string };
  const [showChat, setShowChat] = useState(false);
  const toggleChat = () => setShowChat(prev => !prev);

  
  return (

    <div className="min-h-screen bg-[#0e1c2c]/70 text-white">
        <button
        onClick={toggleChat}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        {showChat ? 'Hide Chat' : 'Show Chat'}
      </button>

      {showChat && (
        <div className="mb-6">
          <ChatManagement courseId={courseId} />
        </div>
      )}
     <QueueManagement courseId={courseId} role="staff" />
    </div>
  );
};

export default StaffQueuePage;
