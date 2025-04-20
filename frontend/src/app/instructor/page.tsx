'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from '../constants';
import SignOutButton from '../components/SignOutButton';
import { useRouter } from 'next/navigation';
import { formatCourseId } from '../utils/formatters';

interface User {
  netId: string;
  firstName?: string;
  lastName?: string;
}

interface AdminEntry {
  net_id: string;
  course_id: string;
}

interface Course {
  course_id: string;
  academic_year: string;
  academic_term: string;
  enrollment_size?: number;
  course_staff_size?: number;
  calendar_link?: string;
}

const InstructorPage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await axios.get<{ auth: boolean; user?: User }>(
          `${API_ENDPOINTS.BACKEND_URL}/check`,
          { withCredentials: true }
        );
        if (res.data.auth && res.data.user) {
          setUser(res.data.user);
        }
      } catch (error) {
        console.error('Error fetching user:', error);
      }
    };

    fetchUser();
  }, []);

  useEffect(() => {
    if (!user) return;

    const fetchCourses = async () => {
      try {
        const token = localStorage.getItem('jwtToken');
        const adminRes = await axios.get<AdminEntry[]>(
          `${API_ENDPOINTS.BACKEND_URL}/admins/person`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                withCredentials: true,
            });

        const courseDetails = await Promise.all(
          adminRes.data.map(async (entry) => {
            const courseRes = await axios.get<Course>(
              `${API_ENDPOINTS.BACKEND_URL}/course/${entry.course_id}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                withCredentials: true,
            });
            return courseRes.data;
          })
        );

        setCourses(courseDetails);
      } catch (error) {
        console.error('Error fetching instructor courses:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [user]);

  if (loading) return <p className="text-white text-center mt-10">Loading...</p>;
  if (!user) return <p className="text-white text-center mt-10">You are not logged in.</p>;

  return (
    <div className="min-h-screen bg-[#0e1c2c]/75 text-white px-6 py-8 relative">
      <div className="absolute top-4 right-6">
        <SignOutButton />
      </div>

      <h1 className="text-4xl sm:text-5xl font-bold text-center mb-10">
        Courses you're instructing
      </h1>

      {courses.length === 0 ? (
        <p className="text-center text-gray-300">No courses found for you.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white text-[#0e1c2c] rounded-xl overflow-hidden">
            <thead className="bg-gray-200 text-left text-lg">
              <tr>
                <th className="px-6 py-3">Course ID</th>
                <th className="px-6 py-3">Academic Year</th>
                <th className="px-6 py-3">Term</th>
                <th className="px-6 py-3">Enrollment</th>
                <th className="px-6 py-3">Staff Size</th>
                <th className="px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {courses.map((course, idx) => (
                <tr
                  key={course.course_id}
                  className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-100'}
                >
                  <td className="px-6 py-3">{formatCourseId(course.course_id)}</td>
                  <td className="px-6 py-3">{course.academic_year}</td>
                  <td className="px-6 py-3">{course.academic_term}</td>
                  <td className="px-6 py-3">{course.enrollment_size}</td>
                  <td className="px-6 py-3">{course.course_staff_size}</td>
                  <td className="px-6 py-3">
                    <div className="flex flex-col space-y-2">
                      <button
                        className="px-4 py-2 bg-[#0e1c2c]/75 text-white rounded-lg hover:bg-gray-800 transition"
                        onClick={() => router.push(`/instructor/${course.course_id}/students`)}
                      >
                        Manage Students
                      </button>
                      <button
                        className="px-4 py-2 bg-[#0e1c2c]/75 text-white rounded-lg hover:bg-gray-800 transition"
                        onClick={() => router.push(`/instructor/${course.course_id}/staff`)}
                      >
                        Manage Staff
                      </button>
                      <button
                        className="px-4 py-2 bg-[#0e1c2c]/75 text-white rounded-lg hover:bg-gray-800 transition"
                        onClick={() => router.push(`/instructor/${course.course_id}/queue`)}
                      >
                        View Queue
                      </button>

                      <button
                        className="px-4 py-2 bg-[#0e1c2c]/75 text-white rounded-lg hover:bg-green-800 transition"
                        onClick={() => router.push(`/instructor/metrics`)}
                      >
                        Compute Ed Metrics
                      </button>
                    </div>
                  </td>
                  <td className="px-6 py-3 space-y-2 flex flex-col">
                    {course.calendar_link?.trim() ? (
                      <>
                        <button
                          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                          onClick={() => router.push(`/instructor/${course.course_id}/calendar`)}
                        >
                          View Calendar
                        </button>
                        <button
                          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
                          onClick={() => {
                            const link = prompt('Enter PUBLIC Google Calendar Link:');
                            if (link) {
                              axios.put(`${API_ENDPOINTS.BACKEND_URL}/course/${course.course_id}`, {
                                calendar_link: link
                              }, { withCredentials: true })
                                .then(() => {
                                  alert('Calendar link updated!');
                                  window.location.reload();
                                })
                                .catch(err => {
                                  console.error('Failed to update:', err);
                                  alert('Update failed.');
                                });
                            }
                          }}
                        >
                          Edit Calendar
                        </button>
                      </>
                    ) : (
                      <button
                        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
                        onClick={() => {
                          const link = prompt('Enter PUBLIC Google Calendar Link:');
                          if (link) {
                            axios.put(`${API_ENDPOINTS.BACKEND_URL}/course/${course.course_id}`, {
                              calendar_link: link
                            }, { withCredentials: true })
                              .then(() => {
                                alert('Calendar link added!');
                                window.location.reload();
                              })
                              .catch(err => {
                                console.error('Failed to add:', err);
                                alert('Add failed.');
                              });
                          }
                        }}
                      >
                        Add Calendar
                      </button>
                    )}
                  </td>


                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

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

export default InstructorPage;
