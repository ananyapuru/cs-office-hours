'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import QueueManagement from '@/app/components/QueueManagement';

const InstructorQueuePage: React.FC = () => {
  const { courseId } = useParams() as { courseId: string };

  return (
    <div className="min-h-screen bg-[#0e1c2c] text-white">
      <QueueManagement courseId={courseId} role="instructor" />
    </div>
  );
};

export default InstructorQueuePage;
