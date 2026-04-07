import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsAPI } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function AdminDashboardPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => analyticsAPI.adminDashboard(),
    select: (r) => r.data,
  });

  if (isLoading) return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        {[1,2,3,4].map(i => <div key={i} className="card h-28 animate-pulse" />)}
      </div>
    </div>
  );

  const stats = analytics ? [
    { label: 'Total Users', value: analytics.users?.total || 0, sub: `${analytics.users?.students || 0} students, ${analytics.users?.instructors || 0} instructors`, icon: '👥', color: 'bg-blue-50 text-blue-600' },
    { label: 'Total Courses', value: analytics.courses?.total || 0, sub: `${analytics.courses?.published || 0} published`, icon: '📚', color: 'bg-purple-50 text-purple-600' },
    { label: 'Total Enrollments', value: analytics.enrollments || 0, sub: 'All time', icon: '🎓', color: 'bg-green-50 text-green-600' },
    { label: 'Total Revenue', value: `$${(analytics.revenue || 0).toFixed(0)}`, sub: 'All payments', icon: '💰', color: 'bg-yellow-50 text-yellow-600' },
  ] : [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Platform-wide overview</p>
      </div>

      {/* Quick links */}
      <div className="flex gap-3 mb-8">
        <a href="/admin/" target="_blank" rel="noreferrer" className="btn-primary text-sm py-2">
          Django Admin Panel ↗
        </a>
        <a href="http://localhost:8001/docs" target="_blank" rel="noreferrer" className="btn-secondary text-sm py-2">
          FastAPI Docs ↗
        </a>
        <a href="/api/docs/" target="_blank" rel="noreferrer" className="btn-secondary text-sm py-2">
          Django API Docs ↗
        </a>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-10">
        {stats.map((s) => (
          <div key={s.label} className="card p-6">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-xl mb-3 ${s.color}`}>
              {s.icon}
            </div>
            <div className="text-2xl font-bold text-gray-900">{s.value}</div>
            <div className="text-sm text-gray-600 mt-0.5">{s.label}</div>
            <div className="text-xs text-gray-400 mt-1">{s.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User breakdown */}
        <div className="card p-6">
          <h3 className="font-bold text-gray-900 mb-4">User Breakdown</h3>
          {analytics?.users && (
            <div className="space-y-3">
              {[
                { label: 'Students', value: analytics.users.students, total: analytics.users.total, color: 'bg-blue-500' },
                { label: 'Instructors', value: analytics.users.instructors, total: analytics.users.total, color: 'bg-purple-500' },
              ].map((item) => (
                <div key={item.label}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{item.label}</span>
                    <span className="font-medium">{item.value}</span>
                  </div>
                  <div className="bg-gray-100 rounded-full h-2">
                    <div
                      className={`${item.color} h-2 rounded-full`}
                      style={{ width: `${item.total ? (item.value / item.total) * 100 : 0}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Course status */}
        <div className="card p-6">
          <h3 className="font-bold text-gray-900 mb-4">Course Status</h3>
          {analytics?.courses && (
            <div className="space-y-3">
              {[
                { label: 'Published', value: analytics.courses.published, total: analytics.courses.total, color: 'bg-green-500' },
                { label: 'Draft/Archived', value: (analytics.courses.total || 0) - (analytics.courses.published || 0), total: analytics.courses.total, color: 'bg-gray-400' },
              ].map((item) => (
                <div key={item.label}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{item.label}</span>
                    <span className="font-medium">{item.value}</span>
                  </div>
                  <div className="bg-gray-100 rounded-full h-2">
                    <div
                      className={`${item.color} h-2 rounded-full`}
                      style={{ width: `${item.total ? (item.value / item.total) * 100 : 0}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick actions */}
        <div className="card p-6">
          <h3 className="font-bold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            {[
              { label: '👤 Manage Users', href: '/admin/users/user/' },
              { label: '📚 Manage Courses', href: '/admin/courses/course/' },
              { label: '🏅 View Certificates', href: '/admin/certificates/certificate/' },
              { label: '💳 View Payments', href: '/admin/payments/payment/' },
              { label: '🎫 Manage Coupons', href: '/admin/payments/coupon/' },
            ].map((action) => (
              <a
                key={action.label}
                href={action.href}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-700 hover:bg-gray-50 border border-gray-100 transition-colors"
              >
                {action.label}
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
