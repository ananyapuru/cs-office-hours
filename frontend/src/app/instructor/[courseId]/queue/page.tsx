'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import QueueManagement from '@/app/components/QueueManagement';
import ChatManagement from '@/app/components/ChatManagement';

const InstructorQueuePage: React.FC = () => {
  const { courseId } = useParams() as { courseId: string };
  const [showChat, setShowChat] = useState(false);
  const toggleChat = () => setShowChat(prev => !prev);
  
  return (
    <div className="min-h-screen text-white">
      {showChat && (
        <div className="mb-6">
          <ChatManagement courseId={courseId} />
        </div>
      )}
      <QueueManagement courseId={courseId} role="instructor" />
    </div>
  );
};

export default InstructorQueuePage;
