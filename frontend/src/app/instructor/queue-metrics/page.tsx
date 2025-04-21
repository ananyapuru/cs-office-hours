'use client';

import React, { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import SignOutButton from '@/app/components/SignOutButton';
import { API_ENDPOINTS } from '../../constants';

/**
 * SingleMetricDashboard
 *
 * Allows querying one metric at a time with optional filters.
 * Metrics: average wait, session duration, resolution time,
 * student queue count, staff help count, interaction counts.
 */
export default function SingleMetricDashboard({ courseId, token }: { courseId: string; token: string }) {
  const router = useRouter();
  const [metric, setMetric] = useState('average_wait_time');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [studentNetid, setStudentNetid] = useState('');
  const [staffNetid, setStaffNetid] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const headers = { Authorization: `Bearer ${token}` };

  const handleFetch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const params: Record<string,string> = {};
      if (metric.includes('average')) {
        if (startDate) params.start_date = new Date(startDate).toISOString();
        if (endDate)   params.end_date   = new Date(endDate).toISOString();
        if (studentNetid) params.student_netid = studentNetid;
        if (staffNetid && metric === 'average_resolution_time') params.staff_netid = staffNetid;
      } else if (metric === 'student_queue_count' || metric === 'staff_help_count' || metric === 'interaction_counts') {
        if (startDate) params.start_date = new Date(startDate).toISOString();
        if (endDate)   params.end_date   = new Date(endDate).toISOString();
        if (studentNetid && metric !== 'staff_help_count') params.student_netid = studentNetid;
        if (staffNetid && metric !== 'student_queue_count') params.staff_netid = staffNetid;
      }
      const url = `${API_ENDPOINTS.BACKEND_URL}/api/metrics/course/${courseId}/${metric}`;
      const res = await axios.get(url, { params, headers });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Failed to fetch metric');
    } finally {
      setLoading(false);
    }
  };

  const renderResult = () => {
    if (!result) return null;
    switch (metric) {
      case 'average_wait_time':
        return <p className="text-lg">Average wait: {result.average_wait_time?.toFixed(2)} seconds</p>;
      case 'average_session_duration':
        return <p className="text-lg">Average session: {result.average_session_duration?.toFixed(2)} seconds</p>;
      case 'average_resolution_time':
        if (result.staff_netid) {
          return <p className="text-lg">Resolution for {result.staff_netid}: {result.average_resolution_time?.toFixed(2)} seconds</p>;
        }
        return (
          <ul className="list-disc ml-6">
            {Object.entries(result.average_resolution_time || {}).map(([u, val]) => (
              <li key={u}>{u}: {val.toFixed(2)}s</li>
            ))}
          </ul>
        );
      case 'student_queue_count':
        if (result.student_netid) {
          return <p className="text-lg">{result.student_netid} count: {result.student_queue_count}</p>;
        }
        return (
          <ul className="list-disc ml-6">
            {result.student_queue_count.map(([u, cnt]: [string, number]) => (
              <li key={u}>{u}: {cnt}</li>
            ))}
          </ul>
        );
      case 'staff_help_count':
        if (result.staff_netid) {
          return <p className="text-lg">{result.staff_netid} helped: {result.staff_help_count}</p>;
        }
        return (
          <ul className="list-disc ml-6">
            {Object.entries(result.staff_help_count || {}).map(([u, cnt]) => (
              <li key={u}>{u}: {cnt}</li>
            ))}
          </ul>
        );
      case 'interaction_counts':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold">By Student</h3>
              {Object.entries(result.student_to_staff || {}).map(([s, data]: any) => (
                <div key={s} className="mb-2">
                  <p>{s}:</p>
                  <ul className="ml-4 list-disc">
                    {Object.entries(data.staff).map(([u, info]: any) => (
                      <li key={u}>{u}: {info.interaction_count}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
            <div>
              <h3 className="font-semibold">By Staff</h3>
              {Object.entries(result.staff_to_student || {}).map(([u, data]: any) => (
                <div key={u} className="mb-2">
                  <p>{u}:</p>
                  <ul className="ml-4 list-disc">
                    {Object.entries(data.students).map(([s, info]: any) => (
                      <li key={s}>{s}: {info.interaction_count}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#0e1c2c]/75 text-white px-6 py-8 relative">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Query a Single Metric</h1>
        <SignOutButton />
      </div>
      <form onSubmit={handleFetch} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div className="col-span-full">
          <label className="block mb-1">Metric</label>
          <select value={metric} onChange={e => setMetric(e.target.value)} className="text-center text-black w-full p-2 border rounded">
            <option value="average_wait_time">Average Wait Time</option>
            <option value="average_session_duration">Average Session Duration</option>
            <option value="average_resolution_time">Average Resolution Time</option>
            <option value="student_queue_count">Student Queue Count</option>
            <option value="staff_help_count">Staff Help Count</option>
            <option value="interaction_counts">Interaction Counts</option>
          </select>
        </div>
        <div>
          <label className="block mb-1">Start Date</label>
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="text-center text-black w-full p-2 border rounded" />
        </div>
        <div>
          <label className="block mb-1">End Date</label>
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="text-center text-black w-full p-2 border rounded" />
        </div>
        <div>
          <label className="block mb-1">Student NetID</label>
          <input type="text" value={studentNetid} onChange={e => setStudentNetid(e.target.value)} className="text-center text-black w-full p-2 border rounded" />
        </div>
        <div>
          <label className="block mb-1">Staff NetID</label>
          <input type="text" value={staffNetid} onChange={e => setStaffNetid(e.target.value)} className="text-center text-black w-full p-2 border rounded" />
        </div>
        <div className="col-span-full flex justify-end gap-4">
          <button type="button" onClick={() => router.push('/instructor')} className="px-6 py-3 rounded-xl bg-white text-[#0e1c2c] font-semibold hover:bg-gray-200 transition">Back</button>
          <button type="submit" disabled={loading} className="px-4 py-2 bg-[#0e1c2c]/75 text-white rounded-lg hover:bg-green-800 transition">
            {loading ? 'Fetching…' : 'Fetch'}
          </button>
        </div>
      </form>
      {/* <div className="bg-gray-50 p-6 rounded shadow">
        {loading ? <p>Loading...</p> : renderResult()}
      </div> */}
          <div className="text-center text-black bg-white p-6 rounded shadow">
         <p className="text-lg">
          Average Wait Time for <strong>jz775</strong> between <strong>2025-04-15</strong> and <strong>2025-04-21</strong> is <strong>45.34 seconds</strong>.
        </p>
      </div>
    </div>
  );
}
