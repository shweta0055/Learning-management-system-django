import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { coursesAPI, enrollmentsAPI, streamingAPI } from '../services/api';
import { toast } from 'react-toastify';

export default function LearnPage() {
  const { slug } = useParams();
  const [activeLesson, setActiveLesson] = useState(null);
  const [enrollment, setEnrollment] = useState(null);

  const { data: course } = useQuery({
    queryKey: ['course-learn', slug],
    queryFn: () => coursesAPI.detail(slug),
    select: (r) => r.data,
    onSuccess: (c) => {
      // Set first lesson
      const firstLesson = c.sections?.[0]?.lessons?.[0];
      if (firstLesson && !activeLesson) setActiveLesson(firstLesson);
    },
  });

  const { data: myEnrollments } = useQuery({
    queryKey: ['my-enrollments'],
    queryFn: () => enrollmentsAPI.myEnrollments(),
    select: (r) => r.data.results,
    onSuccess: (data) => {
      const e = data.find((e) => e.course.id === course?.id);
      if (e) setEnrollment(e);
    },
  });

  const progressMutation = useMutation({
    mutationFn: ({ lessonId, data }) =>
      enrollmentsAPI.updateProgress(enrollment?.id, lessonId, data),
    onSuccess: () => toast.success('Progress saved!'),
  });

  const markComplete = () => {
    if (!enrollment || !activeLesson) return;
    progressMutation.mutate({
      lessonId: activeLesson.id,
      data: { is_completed: true },
    });
  };

  if (!course) return <div className="flex items-center justify-center h-64">
    <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full" />
  </div>;

  return (
    <div className="flex h-[calc(100vh-64px)] overflow-hidden bg-gray-900">
      {/* Sidebar */}
      <aside className="w-72 bg-gray-800 overflow-y-auto flex-shrink-0 hidden lg:block">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-white font-semibold text-sm truncate">{course.title}</h2>
          {enrollment && (
            <div className="mt-2">
              <div className="bg-gray-700 rounded-full h-1.5 mt-1">
                <div className="bg-primary-500 h-1.5 rounded-full transition-all" style={{ width: `${enrollment.progress}%` }} />
              </div>
              <p className="text-gray-400 text-xs mt-1">{Math.round(enrollment.progress)}% complete</p>
            </div>
          )}
        </div>
        <div className="divide-y divide-gray-700">
          {course.sections?.map((section) => (
            <div key={section.id}>
              <div className="px-4 py-3 bg-gray-750">
                <p className="text-gray-300 text-xs font-semibold uppercase tracking-wide">{section.title}</p>
              </div>
              {section.lessons?.map((lesson) => {
                const isCompleted = enrollment?.lesson_progress?.find(lp => lp.lesson === lesson.id)?.is_completed;
                const isActive = activeLesson?.id === lesson.id;
                return (
                  <button
                    key={lesson.id}
                    onClick={() => setActiveLesson(lesson)}
                    className={`w-full text-left px-4 py-3 flex items-center gap-3 text-sm transition-colors ${
                      isActive ? 'bg-primary-600 text-white' : 'text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    <span className="flex-shrink-0 w-5">
                      {isCompleted ? '✅' : lesson.content_type === 'video' ? '▶' : '📄'}
                    </span>
                    <span className="truncate flex-1">{lesson.title}</span>
                    {lesson.video_duration > 0 && (
                      <span className="text-xs opacity-60">{Math.floor(lesson.video_duration / 60)}m</span>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-gray-950">
        {activeLesson ? (
          <div>
            {activeLesson.video_url && (
              <div className="aspect-video bg-black">
                <video
                  key={activeLesson.id}
                  src={activeLesson.video_url}
                  controls
                  className="w-full h-full"
                />
              </div>
            )}
            <div className="p-6 max-w-4xl">
              <div className="flex items-start justify-between gap-4 mb-4">
                <h1 className="text-white text-2xl font-bold">{activeLesson.title}</h1>
                <button onClick={markComplete} disabled={progressMutation.isPending}
                  className="btn-primary text-sm flex-shrink-0 py-1.5">
                  {progressMutation.isPending ? '...' : 'Mark Complete ✓'}
                </button>
              </div>
              {activeLesson.description && (
                <p className="text-gray-400 leading-relaxed">{activeLesson.description}</p>
              )}
              {activeLesson.content && (
                <div className="mt-4 text-gray-300 leading-relaxed whitespace-pre-line bg-gray-900 p-4 rounded-lg">
                  {activeLesson.content}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <div className="text-5xl mb-4">🎓</div>
              <p>Select a lesson from the sidebar to begin</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
