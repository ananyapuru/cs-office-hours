'use client';

import { useParams, useRouter } from 'next/navigation';
import { formatCourseId } from '../../../utils/formatters';
import SignOutButton from '@/app/components/SignOutButton';

const QueuePage: React.FC = () => {
  const params = useParams();
  const router = useRouter();

  const courseId = params?.courseId as string; // Dynamic route param

  if (!courseId) {
    return <p className="text-white text-center mt-10">Course ID not found.</p>;
  }

  return (
    <div className="min-h-screen bg-[#0e1c2c] flex flex-col items-center justify-center text-white px-6">
    <div className="absolute top-4 right-6">
        <SignOutButton />
      </div>
      <h1 className="text-5xl font-bold mb-6">
        {formatCourseId(courseId)} Queue
      </h1>
      <p className="text-gray-400">Real-time queue system coming soon!</p>

      <div className="text-center mt-10">
        <button
          onClick={() => router.push('/welcome')}
          className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold hover:bg-gray-200 transition"
        >
          Back to Welcome Page
        </button>
      </div>
    </div>
    
  );
};

export default QueuePage;
