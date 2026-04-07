// DashboardPage.jsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { enrollmentsAPI, recommendationsAPI } from '../services/api';
import { useAuthStore } from '../context/authStore';
import CourseCard from '../components/courses/CourseCard';

export default function DashboardPage() {
  const { user } = useAuthStore();

  const { data: enrollments, isLoading } = useQuery({
    queryKey: ['my-enrollments'],
    queryFn: () => enrollmentsAPI.myEnrollments(),
    select: (r) => r.data.results,
  });

  const { data: continueLearning } = useQuery({
    queryKey: ['continue-learning'],
    queryFn: () => recommendationsAPI.continueLearning(),
    select: (r) => r.data.courses,
  });

  const { data: recommendations } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => recommendationsAPI.forMe(),
    select: (r) => r.data.recommendations?.slice(0, 4),
  });

  const completed = enrollments?.filter((e) => e.status === 'completed').length || 0;
  const inProgress = enrollments?.filter((e) => e.status === 'active').length || 0;

  if (isLoading) return (
    <div className="max-w-7xl mx-auto px-4 py-10 animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-64 mb-8" />
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-10">
        {[1,2,3].map(i => <div key={i} className="card p-6 h-24" />)}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {[1,2,3].map(i => <div key={i} className="card h-48" />)}
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.first_name || user?.username}! 👋
        </h1>
        <p className="text-gray-500 mt-1 text-sm">Keep up the great work</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-10">
        {[
          { label: 'Enrolled Courses', value: enrollments?.length || 0, icon: '📚', color: 'bg-blue-50 text-blue-700' },
          { label: 'In Progress', value: inProgress, icon: '⏳', color: 'bg-yellow-50 text-yellow-700' },
          { label: 'Completed', value: completed, icon: '✅', color: 'bg-green-50 text-green-700' },
        ].map((stat) => (
          <div key={stat.label} className="card p-6 flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${stat.color}`}>
              {stat.icon}
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
              <div className="text-sm text-gray-500">{stat.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Continue Learning */}
      {continueLearning?.length > 0 && (
        <section className="mb-10">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Continue Learning</h2>
          <div className="space-y-3">
            {continueLearning.map((course) => (
              <div key={course.id} className="card p-4 flex items-center gap-4">
                <div className="w-16 h-12 rounded-lg bg-gray-200 overflow-hidden flex-shrink-0">
                  {course.thumbnail
                    ? <img src={course.thumbnail} alt={course.title} className="w-full h-full object-cover" />
                    : <div className="w-full h-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold">{course.title[0]}</div>
                  }
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 text-sm truncate">{course.title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                      <div className="bg-primary-600 h-1.5 rounded-full" style={{ width: `${course.progress}%` }} />
                    </div>
                    <span className="text-xs text-gray-500">{Math.round(course.progress)}%</span>
                  </div>
                </div>
                <Link to={`/learn/${course.slug}`} className="btn-primary text-xs py-1.5 px-3 flex-shrink-0">
                  Resume
                </Link>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* My enrollments */}
      <section className="mb-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">My Courses</h2>
          <Link to="/courses" className="text-primary-600 text-sm font-medium hover:underline">Browse more →</Link>
        </div>
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[1,2,3].map(i => <div key={i} className="card animate-pulse h-48" />)}
          </div>
        ) : enrollments?.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {enrollments.map((e) => <CourseCard key={e.id} course={e.course} />)}
          </div>
        ) : (
          <div className="card p-10 text-center text-gray-400">
            <div className="text-4xl mb-3">📚</div>
            <p>You haven't enrolled in any courses yet.</p>
            <Link to="/courses" className="btn-primary mt-4 inline-block">Explore Courses</Link>
          </div>
        )}
      </section>

      {/* Recommendations */}
      {recommendations?.length > 0 && (
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recommended for You</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {recommendations.map((course) => <CourseCard key={course.id} course={course} />)}
          </div>
        </section>
      )}
    </div>
  );
}
