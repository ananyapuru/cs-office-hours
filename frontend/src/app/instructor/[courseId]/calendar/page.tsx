'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import axios from 'axios';
import { API_ENDPOINTS } from '../../../constants';
import SignOutButton from '../../../components/SignOutButton';

interface Course {
  course_id: string;
  calendar_link?: string;
}

const CalendarPage: React.FC = () => {
  const { courseId } = useParams();
  const router = useRouter();
  const [calendarLink, setCalendarLink] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCalendarLink = async () => {
      try {
        const token = localStorage.getItem('jwtToken');
        const res = await axios.get<Course>(
          `${API_ENDPOINTS.BACKEND_URL}/course/${courseId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                withCredentials: true,
            });
        if (res.data.calendar_link) {
          setCalendarLink(res.data.calendar_link);
        } else {
          alert('No calendar link found for this course.');
          router.push('/instructor');
        }
      } catch (error) {
        console.error('Error fetching calendar link:', error);
        alert('Failed to load calendar.');
        router.push('/instructor');
      } finally {
        setLoading(false);
      }
    };

    fetchCalendarLink();
  }, [courseId, router]);

  if (loading) return <p className="text-white text-center mt-10">Loading...</p>;

  return (
    <div className="min-h-screen bg-[#0e1c2c]/75 text-white px-6 py-8 relative flex flex-col items-center">
      <div className="absolute top-4 right-6">
        <SignOutButton />
      </div>

      <h1 className="text-3xl sm:text-4xl font-bold mb-6 text-center">Course Calendar</h1>

      {calendarLink ? (
        <iframe
          src={calendarLink}
          style={{ border: 0 }}
          width="100%"
          height="600"
          frameBorder="0"
          scrolling="no"
          className="rounded-xl max-w-6xl"
        ></iframe>
      ) : (
        <p className="text-center">No calendar link available for this course.</p>
      )}

      <button
        onClick={() => router.push('/instructor')}
        className="mt-6 px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold hover:bg-gray-200 transition"
      >
        Back to Instructor Page
      </button>
    </div>
  );
};

export default CalendarPage;
