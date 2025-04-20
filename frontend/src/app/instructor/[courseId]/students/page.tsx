'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useRouter } from 'next/navigation';
import SignOutButton from '../../../components/SignOutButton';
import { API_ENDPOINTS } from '../../../constants';

interface Student {
  net_id: string;
  first_name: string;
  last_name: string;
  yale_email: string;
  college: string;
  class_year: number;
  role: string;
}

const ManageStudentsPage: React.FC = () => {
  const { courseId } = useParams();
  const router = useRouter();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [netId, setNetId] = useState('');
  const [error, setError] = useState('');
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const token = localStorage.getItem('jwtToken');
        const res = await axios.get(`${API_ENDPOINTS.BACKEND_URL}/course/${courseId}/students`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        withCredentials: true,
      });
        setStudents(res.data);
      } catch (err) {
        console.error('Error fetching students:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, [courseId]);

  const handleDelete = async (net_id: string) => {
    try {
      const token = localStorage.getItem('jwtToken');
      await axios.delete(`${API_ENDPOINTS.BACKEND_URL}/student/${net_id}/${courseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        withCredentials: true,
      });
      setStudents((prev) => prev.filter((s) => s.net_id !== net_id));
    } catch (err) {
      console.error('Error deleting student:', err);
    }
  };

  const handleAddStudent = async () => {
    setError('');
    if (!netId.trim()) {
      setError('Net ID is required.');
      return;
    }

    try {
      const token = localStorage.getItem('jwtToken');
      await axios.post(`${API_ENDPOINTS.BACKEND_URL}/enroll-via-yalies`, {
        net_id: netId.trim(),
        course_id: courseId,
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        withCredentials: true,
      });

      setNetId('');
      const res = await axios.get(`${API_ENDPOINTS.BACKEND_URL}/course/${courseId}/students`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        withCredentials: true,
      });
      setStudents(res.data);
    } catch (err: any) {
      console.error('Error adding student:', err);
      setError(err.response?.data?.error || 'Something went wrong.');
    }
  };

  const handleCSVUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('jwtToken');
      await axios.post(`${API_ENDPOINTS.BACKEND_URL}/upload-roster/${courseId}`, formData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`,
        },
      });

      const res = await axios.get(`${API_ENDPOINTS.BACKEND_URL}/course/${courseId}/students`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        withCredentials: true,
      });
      setStudents(res.data);
      setFile(null);
    } catch (err) {
      console.error('Error uploading CSV:', err);
    }
  };

  return (
    <div className="min-h-screen bg-[#0e1c2c]/70 text-white px-6 py-8 relative">
      <div className="absolute top-4 right-6">
        <SignOutButton />
      </div>

      <h1 className="text-4xl font-bold text-center mb-8">
        Manage Students for {courseId}
      </h1>

      {loading ? (
        <p className="text-center">Loading students...</p>
      ) : (
        <div className="overflow-x-auto mb-10">
          <table className="min-w-full bg-white text-[#0e1c2c] rounded-xl overflow-hidden text-sm">
            <thead className="bg-gray-200 text-left">
              <tr>
                <th className="px-4 py-2">Net ID</th>
                <th className="px-4 py-2">Name</th>
                <th className="px-4 py-2">Email</th>
                <th className="px-4 py-2">College</th>
                <th className="px-4 py-2">Year</th>
                <th className="px-4 py-2">Role</th>
                <th className="px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s, i) => (
                <tr key={s.net_id} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-100'}>
                  <td className="px-4 py-2">{s.net_id}</td>
                  <td className="px-4 py-2">{s.first_name} {s.last_name}</td>
                  <td className="px-4 py-2">{s.yale_email}</td>
                  <td className="px-4 py-2">{s.college}</td>
                  <td className="px-4 py-2">{s.class_year}</td>
                  <td className="px-4 py-2">{s.role}</td>
                  <td className="px-4 py-2">
                    <button
                      onClick={() => handleDelete(s.net_id)}
                      className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Student Form */}
      <div className="bg-white text-[#0e1c2c] p-6 rounded-xl max-w-xl mx-auto mb-10 space-y-4">
        <h2 className="text-lg font-bold">Add Student</h2>
        {error && <p className="text-red-600">{error}</p>}
        <input
          placeholder="NetID"
          value={netId}
          onChange={(e) => setNetId(e.target.value)}
          className="border p-2 rounded w-full"
        />
        <button
          onClick={handleAddStudent}
          className="mt-2 px-6 py-2 rounded bg-[#0e1c2c]/70 text-white hover:bg-gray-800 transition"
        >
          Add Student
        </button>
      </div>

      {/* Upload CSV */}
      <div className="text-center space-y-4">
        <h2 className="text-xl font-semibold">Upload Canvas Roster CSV</h2>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="text-sm text-white"
        />
        <button
          onClick={handleCSVUpload}
          disabled={!file}
          className="ml-4 px-6 py-2 rounded bg-white text-[#0e1c2c] font-semibold hover:bg-gray-200 transition"
        >
          Upload Roster
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

export default ManageStudentsPage;
