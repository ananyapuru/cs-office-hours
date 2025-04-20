'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import axios from 'axios';
import { API_ENDPOINTS } from '../../../constants';
import SignOutButton from '../../../components/SignOutButton';

interface Course {
  calendar_link?: string;
}

const StudentCalendarPage: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const { courseId } = params;
  const [calendarLink, setCalendarLink] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCalendar = async () => {
      try {
        const token = localStorage.getItem('jwtToken');
        const res = await axios.get<Course>(
          `${API_ENDPOINTS.BACKEND_URL}/course/${courseId}`, {
              headers: {
                  'Authorization': `Bearer ${token}`
              },
              withCredentials: true,
            });
        setCalendarLink(res.data.calendar_link || null);
      } catch (err) {
        console.error('Error fetching calendar link:', err);
      } finally {
        setLoading(false);
      }
    };

    if (courseId) fetchCalendar();
  }, [courseId]);

  if (loading) return <p className="text-center text-white mt-10">Loading calendar...</p>;

  if (!calendarLink) {
    return (
      <div className="min-h-screen bg-[#0e1c2c]/75 text-white flex flex-col items-center justify-center">
        <p className="text-2xl mb-6">No Calendar Available for this Course.</p>
        <button
          onClick={() => router.back()}
          className="px-6 py-3 bg-white text-[#0e1c2c] rounded-xl font-semibold hover:bg-gray-200 transition"
        >
          Back
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0e1c2c]/75 text-white px-6 py-8 flex flex-col items-center relative">
      <div className="absolute top-4 right-6">
        <SignOutButton />
      </div>

      <h1 className="text-4xl font-bold mb-8 text-center">Course Calendar</h1>

      <iframe
        src={calendarLink}
        style={{ border: 0 }}
        width="800"
        height="600"
        frameBorder="0"
        scrolling="no"
      ></iframe>

      <button
        onClick={() => router.back()}
        className="mt-8 px-6 py-3 bg-white text-[#0e1c2c] rounded-xl font-semibold hover:bg-gray-200 transition"
      >
        Back
      </button>
    </div>
  );
};

export default StudentCalendarPage;
