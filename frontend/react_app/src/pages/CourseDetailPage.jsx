import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { coursesAPI, enrollmentsAPI } from '../services/api';
import { useAuthStore } from '../context/authStore';
import { toast } from 'react-toastify';

export default function CourseDetailPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuthStore();
  const [activeTab, setActiveTab] = useState('overview');

  const { data: course, isLoading } = useQuery({
    queryKey: ['course', slug],
    queryFn: () => coursesAPI.detail(slug),
    select: (r) => r.data,
    staleTime: 2 * 60 * 1000,
  });

  const { data: myEnrollments } = useQuery({
    queryKey: ['my-enrollments'],
    queryFn: () => enrollmentsAPI.myEnrollments(),
    enabled: isAuthenticated(),
    select: (r) => r.data.results,
  });

  const isEnrolled = myEnrollments?.some((e) => e.course.id === course?.id);

  const enrollMutation = useMutation({
    mutationFn: () => enrollmentsAPI.enroll(course.id),
    onSuccess: () => {
      toast.success('Enrolled successfully!');
      navigate(`/learn/${slug}`);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Enrollment failed'),
  });

  const handleEnroll = () => {
    if (!isAuthenticated()) return navigate('/login');
    if (course.is_free || course.effective_price === 0) {
      enrollMutation.mutate();
    } else {
      navigate(`/checkout/${course.id}`);
    }
  };

  if (isLoading) return (
    <div className="bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-12 animate-pulse">
        <div className="h-8 bg-gray-700 rounded w-2/3 mb-4" />
        <div className="h-4 bg-gray-700 rounded w-1/2 mb-6" />
        <div className="flex gap-4">
          {[1,2,3,4].map(i => <div key={i} className="h-4 bg-gray-700 rounded w-24" />)}
        </div>
      </div>
    </div>
  );

  if (!course) return <div className="text-center py-20">Course not found.</div>;

  const tabs = ['overview', 'curriculum', 'reviews'];

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-12 flex flex-col lg:flex-row gap-8">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-4">
              {course.category && (
                <span className="badge bg-primary-500/20 text-primary-300 text-xs">{course.category.name}</span>
              )}
              <span className="badge bg-yellow-500/20 text-yellow-300 text-xs capitalize">{course.level}</span>
            </div>
            <h1 className="text-3xl lg:text-4xl font-bold mb-4">{course.title}</h1>
            <p className="text-gray-300 text-lg mb-6">{course.short_description}</p>
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400">
              <span>👤 {course.instructor?.first_name} {course.instructor?.last_name}</span>
              {course.rating > 0 && <span>⭐ {course.rating.toFixed(1)} ({course.total_ratings} reviews)</span>}
              <span>👥 {course.total_students?.toLocaleString()} students</span>
              <span>🕐 {course.duration_hours?.toFixed(1)}h total</span>
              <span>📖 {course.total_lessons} lessons</span>
              <span>🌐 {course.language}</span>
            </div>
          </div>

          {/* Purchase card */}
          <div className="w-full lg:w-80 flex-shrink-0">
            <div className="bg-white text-gray-900 rounded-xl overflow-hidden shadow-xl">
              {course.thumbnail && (
                <img src={course.thumbnail} alt={course.title} className="w-full aspect-video object-cover" />
              )}
              <div className="p-6">
                <div className="flex items-baseline gap-3 mb-4">
                  <span className="text-3xl font-bold text-gray-900">
                    {course.is_free ? 'Free' : `$${parseFloat(course.effective_price).toFixed(2)}`}
                  </span>
                  {course.discount_price && !course.is_free && (
                    <span className="text-gray-400 line-through text-lg">${parseFloat(course.price).toFixed(2)}</span>
                  )}
                </div>

                {isEnrolled ? (
                  <Link to={`/learn/${slug}`} className="btn-primary w-full py-3 text-center block text-base">
                    Continue Learning →
                  </Link>
                ) : (
                  <button
                    onClick={handleEnroll}
                    disabled={enrollMutation.isPending}
                    className="btn-primary w-full py-3 text-base"
                  >
                    {enrollMutation.isPending ? 'Enrolling...' : course.is_free ? 'Enroll for Free' : 'Buy Now'}
                  </button>
                )}

                <ul className="mt-5 space-y-2 text-sm text-gray-600">
                  <li>✅ Full lifetime access</li>
                  {course.certificate_available && <li>🏅 Certificate of completion</li>}
                  <li>📱 Access on mobile & desktop</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex gap-1 border-b border-gray-200 mb-8">
          {tabs.map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`px-5 py-2.5 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
                activeTab === tab ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}>
              {tab}
            </button>
          ))}
        </div>

        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              {course.objectives?.length > 0 && (
                <div className="card p-6">
                  <h3 className="font-bold text-lg mb-4">What you'll learn</h3>
                  <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {course.objectives.map((obj, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className="text-green-500 mt-0.5 flex-shrink-0">✓</span>{obj}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="card p-6">
                <h3 className="font-bold text-lg mb-4">Course Description</h3>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">{course.description}</p>
              </div>
              {course.requirements?.length > 0 && (
                <div className="card p-6">
                  <h3 className="font-bold text-lg mb-4">Requirements</h3>
                  <ul className="space-y-2">
                    {course.requirements.map((req, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className="text-primary-500 mt-0.5">•</span>{req}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <div>
              <div className="card p-6">
                <h3 className="font-bold mb-4">Instructor</h3>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold">
                    {course.instructor?.first_name?.[0]}
                  </div>
                  <div>
                    <p className="font-semibold text-sm">{course.instructor?.first_name} {course.instructor?.last_name}</p>
                    <p className="text-xs text-gray-500">{course.instructor?.email}</p>
                  </div>
                </div>
                {course.instructor?.bio && (
                  <p className="text-sm text-gray-600 mt-4 leading-relaxed">{course.instructor.bio}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'curriculum' && (
          <div className="max-w-3xl space-y-3">
            {course.sections?.map((section) => (
              <div key={section.id} className="card">
                <div className="p-4 bg-gray-50 border-b border-gray-100">
                  <h4 className="font-semibold text-gray-900">{section.title}</h4>
                  <p className="text-xs text-gray-500 mt-0.5">{section.lessons?.length} lessons</p>
                </div>
                <ul className="divide-y divide-gray-100">
                  {section.lessons?.map((lesson) => (
                    <li key={lesson.id} className="flex items-center gap-3 px-4 py-3">
                      <span className="text-gray-400 flex-shrink-0">
                        {lesson.content_type === 'video' ? '▶' : lesson.content_type === 'quiz' ? '❓' : '📄'}
                      </span>
                      <span className="text-sm text-gray-700 flex-1">{lesson.title}</span>
                      {lesson.is_free_preview && <span className="badge bg-green-100 text-green-700">Preview</span>}
                      {lesson.video_duration > 0 && (
                        <span className="text-xs text-gray-400">{Math.floor(lesson.video_duration / 60)}min</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'reviews' && (
          <div className="max-w-2xl space-y-4">
            {course.reviews?.length > 0 ? course.reviews.map((review) => (
              <div key={review.id} className="card p-5">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-9 h-9 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-semibold text-sm">
                    {review.user.first_name?.[0] || review.user.email[0].toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{review.user.first_name} {review.user.last_name}</p>
                    <div className="flex text-yellow-400">{'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}</div>
                  </div>
                </div>
                <p className="text-sm text-gray-700">{review.comment}</p>
              </div>
            )) : (
              <p className="text-gray-500 text-center py-10">No reviews yet. Be the first to review!</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
