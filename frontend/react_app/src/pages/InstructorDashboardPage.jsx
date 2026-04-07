import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { coursesAPI, analyticsAPI } from '../services/api';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';

export default function InstructorDashboardPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const qc = useQueryClient();
  const { register, handleSubmit, reset } = useForm();

  const { data: courses, isLoading } = useQuery({
    queryKey: ['instructor-courses'],
    queryFn: () => coursesAPI.myCourses(),
    select: (r) => r.data.results || r.data,
  });

  const { data: analytics } = useQuery({
    queryKey: ['instructor-analytics'],
    queryFn: () => analyticsAPI.instructorDashboard(),
    select: (r) => r.data,
  });

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => coursesAPI.categories(),
    select: (r) => r.data,
  });

  const createMutation = useMutation({
    mutationFn: (data) => coursesAPI.create(data),
    onSuccess: () => {
      toast.success('Course created!');
      qc.invalidateQueries(['instructor-courses']);
      setShowCreateForm(false);
      reset();
    },
    onError: (err) => {
      const msgs = err.response?.data;
      if (msgs) Object.values(msgs).flat().forEach((m) => toast.error(m));
      else toast.error('Creation failed');
    },
  });

  const statusColor = { draft: 'bg-gray-100 text-gray-600', published: 'bg-green-100 text-green-700', archived: 'bg-red-100 text-red-600' };

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Instructor Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">Manage your courses and track performance</p>
        </div>
        <button onClick={() => setShowCreateForm(true)} className="btn-primary">+ New Course</button>
      </div>

      {/* Analytics cards */}
      {analytics && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-10">
          {[
            { label: 'Total Courses', value: analytics.courses?.total || 0, icon: '📚' },
            { label: 'Total Students', value: analytics.courses?.total_students || 0, icon: '👥' },
            { label: 'Avg Rating', value: (analytics.courses?.avg_rating || 0).toFixed(1) + ' ⭐', icon: '⭐' },
            { label: 'Total Revenue', value: `$${(analytics.revenue?.total || 0).toFixed(0)}`, icon: '💰' },
          ].map((s) => (
            <div key={s.label} className="card p-5">
              <div className="text-2xl mb-2">{s.icon}</div>
              <div className="text-2xl font-bold text-gray-900">{s.value}</div>
              <div className="text-sm text-gray-500">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Create Course Form */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <h2 className="text-xl font-bold">Create New Course</h2>
              <button onClick={() => { setShowCreateForm(false); reset(); }} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
            </div>
            <form onSubmit={handleSubmit((d) => createMutation.mutate(d))} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Course Title *</label>
                <input {...register('title', { required: true })} className="input" placeholder="e.g. Complete Python Bootcamp" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Short Description</label>
                <input {...register('short_description')} className="input" placeholder="One-line summary" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
                <textarea {...register('description', { required: true })} rows={4} className="input" placeholder="Full course description..." />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select {...register('category')} className="input">
                    <option value="">Select category</option>
                    {categories?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Level</label>
                  <select {...register('level')} className="input">
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price ($)</label>
                  <input type="number" step="0.01" min="0" {...register('price')} className="input" placeholder="0.00" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
                  <input {...register('language')} className="input" defaultValue="English" />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="is_free" {...register('is_free')} className="rounded text-primary-600" />
                <label htmlFor="is_free" className="text-sm text-gray-700">This course is free</label>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="submit" disabled={createMutation.isPending} className="btn-primary flex-1 py-2.5">
                  {createMutation.isPending ? 'Creating...' : 'Create Course'}
                </button>
                <button type="button" onClick={() => { setShowCreateForm(false); reset(); }} className="btn-secondary px-6">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Course list */}
      <h2 className="text-xl font-bold text-gray-900 mb-4">My Courses</h2>
      {isLoading ? (
        <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="card h-20 animate-pulse" />)}</div>
      ) : courses?.length > 0 ? (
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Course</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Students</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Rating</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Price</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {courses.map((course) => (
                <tr key={course.id} className="hover:bg-gray-50">
                  <td className="px-5 py-4">
                    <p className="font-medium text-gray-900 text-sm">{course.title}</p>
                    <p className="text-xs text-gray-400 capitalize">{course.level}</p>
                  </td>
                  <td className="px-5 py-4">
                    <span className={`badge capitalize ${statusColor[course.status]}`}>{course.status}</span>
                  </td>
                  <td className="px-5 py-4 text-sm text-gray-600">{course.total_students || 0}</td>
                  <td className="px-5 py-4 text-sm text-gray-600">
                    {course.rating > 0 ? `${course.rating.toFixed(1)} ⭐` : '—'}
                  </td>
                  <td className="px-5 py-4 text-sm text-gray-600">
                    {course.is_free ? 'Free' : `$${parseFloat(course.price).toFixed(2)}`}
                  </td>
                  <td className="px-5 py-4">
                    <Link to={`/courses/${course.slug}`} className="text-primary-600 text-xs font-medium hover:underline">
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card p-12 text-center text-gray-400">
          <div className="text-4xl mb-3">📚</div>
          <p>You haven't created any courses yet.</p>
          <button onClick={() => setShowCreateForm(true)} className="btn-primary mt-4">Create Your First Course</button>
        </div>
      )}
    </div>
  );
}
