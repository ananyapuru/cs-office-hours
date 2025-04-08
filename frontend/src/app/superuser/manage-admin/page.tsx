'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { API_ENDPOINTS } from '../../constants';
import SignOutButton from '../../components/SignOutButton';

interface AdminEntry {
  net_id: string;
  course_id: string;
}

const YALE_DEPARTMENTS = ['AMTH', 'CPSC', 'MATH', 'ECON'] // TODO: Add the rest
const YALE_SEMESTERS = ['Spring', 'Summer', 'Fall']

const ManageAdminPage: React.FC = () => {
  const [admins, setAdmins] = useState<AdminEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [netId, setNetId] = useState('');
  const [department, setDepartment] = useState('CPSC');
  const [courseCode, setCourseCode] = useState('');
  const [academicYear, setAcademicYear] = useState('2024-2025');
  const [semester, setSemester] = useState('Spring');
  const [calendarLink, setCalendarLink] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const academicYears = Array.from({ length: 30 }, (_, i) => {
    const start = 2023 + i;
    return `${start}-${start + 1}`;
  });

  const fetchAdmins = async () => {
    try {
      const token = localStorage.getItem('jwtToken');
      const res = await axios.get<AdminEntry[]>(
        `${API_ENDPOINTS.BACKEND_URL}/admins`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                withCredentials: true,
            });
      setAdmins(res.data);
    } catch (err) {
      console.error('Error fetching admins:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdmins();
  }, []);

  const formatCourseId = () => {
    const [startYear, endYear] = academicYear.split('-');
    const yearSegment = `AY${startYear.slice(-2)}-${endYear.slice(-2)}`;
    const termMap: Record<string, string> = {
      Spring: `S${endYear.slice(-2)}`,
      Fall: `F${startYear.slice(-2)}`,
      Summer: `U${endYear.slice(-2)}`
    };
    const termSegment = termMap[semester];
    return `${department}_${courseCode.padStart(4, '0')}_${yearSegment}_${termSegment}`;
  };

  const handleAddAdmin = async () => {
    setError('');
    if (!netId || !courseCode) {
      setError('Please fill out all fields.');
      return;
    }

    const course_id = formatCourseId();

    try {
      const token = localStorage.getItem('jwtToken');
      // First ensure course exists
      await axios.post(
        `${API_ENDPOINTS.BACKEND_URL}/course`,
        {
          course_id,
          academic_year: academicYear,
          academic_term: semester,
          enrollment_size: 0,
          course_staff_size: 0,
          calendar_link: calendarLink || null
        }, {
              headers: {
                  'Authorization': `Bearer ${token}`
              },
              withCredentials: true,
      }).catch(err => {
        if (err.response?.status !== 409) throw err;
      });

      // Then assign admin
      await axios.post(
        `${API_ENDPOINTS.BACKEND_URL}/admin`,
        {
          net_id: netId.trim(),
          course_id
        }, {
              headers: {
                  'Authorization': `Bearer ${token}`
              },
              withCredentials: true,
        });

      setNetId('');
      setCourseCode('');
      fetchAdmins();
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.error || 'Something went wrong');
    }
  };

  return (
    <div className="min-h-screen bg-[#0e1c2c] text-white px-6 py-8 relative">
      <div className="absolute top-4 right-6">
        <SignOutButton />
      </div>

      <h1 className="text-4xl sm:text-5xl font-bold text-center mb-8">
        Manage Admin
      </h1>

      {loading ? (
        <p className="text-center">Loading admins...</p>
      ) : (
        <div className="overflow-x-auto mb-10">
          <table className="min-w-full bg-white text-[#0e1c2c] rounded-xl overflow-hidden">
            <thead className="bg-gray-200 text-left text-lg">
              <tr>
                <th className="px-6 py-3">Net ID</th>
                <th className="px-6 py-3">Course ID</th>
                <th className="px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {admins.map((admin, index) => (
                <tr
                  key={`${admin.net_id}-${admin.course_id}`}
                  className={index % 2 === 0 ? 'bg-white' : 'bg-gray-100'}
                >
                  <td className="px-6 py-3">{admin.net_id}</td>
                  <td className="px-6 py-3">{admin.course_id}</td>
                  <td className="px-6 py-3">
                    <button
                      onClick={async () => {
                        try {
                          const token = localStorage.getItem('jwtToken');
                          await axios.delete(
                            `${API_ENDPOINTS.BACKEND_URL}/admin/${admin.net_id}/${admin.course_id}`, {
                              headers: {
                                  'Authorization': `Bearer ${token}`
                              },
                              withCredentials: true,
                        });
                          fetchAdmins();
                        } catch (err: any) {
                          console.error('Delete failed:', err);
                          alert(err.response?.data?.error || 'Failed to delete admin.');
                        }
                      }}
                      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
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

      {/* Add Admin Form */}
      <div className="bg-white text-[#0e1c2c] p-6 rounded-xl max-w-3xl mx-auto mb-10 space-y-4">
        <h2 className="text-xl font-bold">Add Admin</h2>
        {error && <p className="text-red-500">{error}</p>}
        <div className="flex flex-wrap gap-4">
          <input
            placeholder="NetID"
            value={netId}
            onChange={(e) => setNetId(e.target.value)}
            className="border p-2 rounded w-full sm:w-[48%]"
          />
          <input
            placeholder="Course Code (e.g., 3230)"
            type="number"
            min="1"
            max="9999"
            value={courseCode}
            onChange={(e) => setCourseCode(e.target.value)}
            className="border p-2 rounded w-full sm:w-[48%]"
          />
          <select
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="border p-2 rounded w-full sm:w-[48%]"
          >
            {/* TODO: ADD DEPARTMENTS */}
            {YALE_DEPARTMENTS.map(dep => (
              <option key={dep} value={dep}>{dep}</option>
            ))}
          </select>
          <select
            value={academicYear}
            onChange={(e) => setAcademicYear(e.target.value)}
            className="border p-2 rounded w-full sm:w-[48%]"
          >
            {academicYears.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
          <select
            value={semester}
            onChange={(e) => setSemester(e.target.value)}
            className="border p-2 rounded w-full sm:w-[48%]"
          >
            {YALE_SEMESTERS.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <input
            placeholder="Calendar Link (optional)"
            value={calendarLink}
            onChange={(e) => setCalendarLink(e.target.value)}
            className="border p-2 rounded w-full"
          />

        </div>
        <button
          onClick={handleAddAdmin}
          className="mt-4 px-6 py-3 rounded-xl bg-[#0e1c2c] text-white hover:bg-gray-800 transition font-semibold"
        >
          Add Admin
        </button>
      </div>

      {/* Back Button */}
      <div className="text-center">
        <button
          onClick={() => router.push('/superuser')}
          className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold hover:bg-gray-200 transition"
        >
          Back to Superuser Page
        </button>
      </div>
    </div>
  );
};

export default ManageAdminPage;
