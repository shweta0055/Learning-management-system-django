import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { coursesAPI } from '../services/api';
import { recommendationsAPI } from '../services/api';
import CourseCard from '../components/courses/CourseCard';
import { useAuthStore } from '../context/authStore';

const StatCard = ({ value, label }) => (
  <div className="text-center">
    <div className="text-3xl font-bold text-primary-600">{value}</div>
    <div className="text-sm text-gray-600 mt-1">{label}</div>
  </div>
);

export default function HomePage() {
  const { isAuthenticated } = useAuthStore();

  const { data: featuredCourses } = useQuery({
    queryKey: ['featured-courses'],
    queryFn: () => coursesAPI.list({ ordering: '-rating', page_size: 8 }),
    select: (r) => r.data.results,
    staleTime: 5 * 60 * 1000,
  });

  const { data: trending } = useQuery({
    queryKey: ['trending'],
    queryFn: () => recommendationsAPI.trending(),
    select: (r) => r.data.trending?.slice(0, 4),
  });

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-700 via-primary-600 to-blue-500 text-white">
        <div className="max-w-7xl mx-auto px-4 py-20 sm:py-28 flex flex-col lg:flex-row items-center gap-12">
          <div className="flex-1 text-center lg:text-left">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6">
              Learn Without<br />
              <span className="text-yellow-300">Limits</span>
            </h1>
            <p className="text-lg sm:text-xl text-primary-100 mb-8 max-w-xl">
              Access thousands of expert-led courses. Build real skills. Earn certificates that matter.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link to="/courses" className="bg-white text-primary-700 px-8 py-3 rounded-xl font-bold hover:bg-primary-50 transition-colors text-center">
                Explore Courses
              </Link>
              {!isAuthenticated() && (
                <Link to="/register" className="border-2 border-white text-white px-8 py-3 rounded-xl font-bold hover:bg-white hover:text-primary-700 transition-colors text-center">
                  Start for Free
                </Link>
              )}
            </div>
          </div>
          <div className="hidden lg:block flex-1">
            <div className="grid grid-cols-2 gap-4">
              {['Python & ML', 'Web Dev', 'Data Science', 'Design'].map((cat) => (
                <div key={cat} className="bg-white/10 backdrop-blur rounded-xl p-6 text-center border border-white/20">
                  <div className="text-3xl mb-2">
                    {cat === 'Python & ML' ? '🐍' : cat === 'Web Dev' ? '💻' : cat === 'Data Science' ? '📊' : '🎨'}
                  </div>
                  <div className="font-semibold text-sm">{cat}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 py-10 grid grid-cols-2 md:grid-cols-4 gap-8">
          <StatCard value="10K+" label="Courses" />
          <StatCard value="500K+" label="Students" />
          <StatCard value="2K+" label="Instructors" />
          <StatCard value="150+" label="Countries" />
        </div>
      </section>

      {/* Trending courses */}
      {trending?.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 py-16">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">🔥 Trending Now</h2>
              <p className="text-gray-500 mt-1 text-sm">Most popular this week</p>
            </div>
            <Link to="/courses" className="text-primary-600 font-medium text-sm hover:underline">View all →</Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {trending.map((course) => <CourseCard key={course.id} course={course} />)}
          </div>
        </section>
      )}

      {/* Featured courses */}
      <section className="bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-16">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">⭐ Top-Rated Courses</h2>
              <p className="text-gray-500 mt-1 text-sm">Chosen by our community</p>
            </div>
            <Link to="/courses" className="text-primary-600 font-medium text-sm hover:underline">View all →</Link>
          </div>
          {featuredCourses?.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {featuredCourses.map((course) => <CourseCard key={course.id} course={course} />)}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {Array.from({length: 8}).map((_, i) => (
                <div key={i} className="card animate-pulse">
                  <div className="aspect-video bg-gray-200" />
                  <div className="p-4 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-primary-700 text-white py-16">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to start learning?</h2>
          <p className="text-primary-200 mb-8">Join over 500,000 students worldwide and take your career to the next level.</p>
          <Link to="/register" className="bg-yellow-400 text-gray-900 px-10 py-3 rounded-xl font-bold hover:bg-yellow-300 transition-colors inline-block">
            Join for Free Today
          </Link>
        </div>
      </section>
    </div>
  );
}
