'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useRouter } from 'next/navigation';
import SignOutButton from '@/app/components/SignOutButton';
import { API_ENDPOINTS } from '@/app/constants';

interface StaffEntry {
  net_id: string;
  first_name: string;
  last_name: string;
  yale_email: string;
}

const ManageStaffPage: React.FC = () => {
  const { courseId } = useParams();
  const router = useRouter();
  const [staff, setStaff] = useState<StaffEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [netId, setNetId] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStaff = async () => {
      try {
        const ulaRes = await axios.get<{ net_id: string }[]>(
          `${API_ENDPOINTS.BACKEND_URL}/ulas/course/${courseId}`,
          { withCredentials: true }
        );

        const detailedStaff = await Promise.all(
          ulaRes.data.map(async (entry) => {
            const personRes = await axios.get<{ first_name: string; last_name: string; yale_email: string }>(
              `${API_ENDPOINTS.BACKEND_URL}/person/${entry.net_id}`,
              { withCredentials: true }
            );
            return {
              net_id: entry.net_id,
              first_name: personRes.data.first_name,
              last_name: personRes.data.last_name,
              yale_email: personRes.data.yale_email,
            };
          })
        );

        setStaff(detailedStaff);
      } catch (err) {
        console.error('Error fetching staff:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStaff();
  }, [courseId]);

  const handleDelete = async (net_id: string) => {
    try {
      await axios.delete(`${API_ENDPOINTS.BACKEND_URL}/ula/${net_id}/${courseId}`, {
        withCredentials: true,
      });
      setStaff((prev) => prev.filter((s) => s.net_id !== net_id));
    } catch (err) {
      console.error('Error deleting staff:', err);
    }
  };

  const handleAddStaff = async () => {
    setError('');
    if (!netId.trim()) {
      setError('Net ID is required.');
      return;
    }

    try {
      await axios.post(`${API_ENDPOINTS.BACKEND_URL}/ula`, {
        net_id: netId.trim(),
        course_id: courseId,
      }, { withCredentials: true });

      setNetId('');
      // Refresh staff list
      const ulaRes = await axios.get<{ net_id: string }[]>(
        `${API_ENDPOINTS.BACKEND_URL}/ulas/course/${courseId}`,
        { withCredentials: true }
      );

      const detailedStaff = await Promise.all(
        ulaRes.data.map(async (entry) => {
          const personRes = await axios.get<{ first_name: string; last_name: string; yale_email: string }>(
            `${API_ENDPOINTS.BACKEND_URL}/person/${entry.net_id}`,
            { withCredentials: true }
          );
          return {
            net_id: entry.net_id,
            first_name: personRes.data.first_name,
            last_name: personRes.data.last_name,
            yale_email: personRes.data.yale_email,
          };
        })
      );

      setStaff(detailedStaff);
    } catch (err: any) {
      console.error('Error adding staff:', err);
      setError(err.response?.data?.error || 'Something went wrong.');
    }
  };

  if (loading) return <p className="text-white text-center mt-10">Loading...</p>;

  return (
    <div className="min-h-screen bg-[#0e1c2c] text-white px-6 py-8 relative">
      <div className="absolute top-4 right-6">
        <SignOutButton />
      </div>

      <h1 className="text-4xl font-bold text-center mb-8">
        Manage Teaching Staff for {courseId}
      </h1>

      {staff.length === 0 ? (
        <p className="text-center">No teaching staff assigned yet.</p>
      ) : (
        <div className="overflow-x-auto mb-10">
          <table className="min-w-full bg-white text-[#0e1c2c] rounded-xl overflow-hidden text-sm">
            <thead className="bg-gray-200 text-left">
              <tr>
                <th className="px-4 py-2">Net ID</th>
                <th className="px-4 py-2">First Name</th>
                <th className="px-4 py-2">Last Name</th>
                <th className="px-4 py-2">Email</th>
                <th className="px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {staff.map((s, i) => (
                <tr key={s.net_id} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-100'}>
                  <td className="px-4 py-2">{s.net_id}</td>
                  <td className="px-4 py-2">{s.first_name}</td>
                  <td className="px-4 py-2">{s.last_name}</td>
                  <td className="px-4 py-2">{s.yale_email}</td>
                  <td className="px-4 py-2">
                    <button
                      onClick={() => handleDelete(s.net_id)}
                      className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Teaching Staff Form */}
      <div className="bg-white text-[#0e1c2c] p-6 rounded-xl max-w-xl mx-auto mb-10 space-y-4">
        <h2 className="text-lg font-bold">Add Teaching Staff by NetID</h2>
        {error && <p className="text-red-600">{error}</p>}
        <input
          placeholder="NetID"
          value={netId}
          onChange={(e) => setNetId(e.target.value)}
          className="border p-2 rounded w-full"
        />
        <button
          onClick={handleAddStaff}
          className="mt-2 px-6 py-2 rounded bg-[#0e1c2c] text-white hover:bg-gray-800 transition"
        >
          Add Staff
        </button>
      </div>

      {/* Back Button */}
      <div className="text-center mt-10">
        <button
          onClick={() => router.push('/instructor')}
          className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold hover:bg-gray-200 transition"
        >
          Back to Instructor Page
        </button>
      </div>
    </div>
  );
};

export default ManageStaffPage;
