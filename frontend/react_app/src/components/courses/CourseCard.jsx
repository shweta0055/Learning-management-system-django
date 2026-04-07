import React from 'react';
import { Link } from 'react-router-dom';

const StarRating = ({ rating }) => (
  <div className="flex items-center gap-1">
    {[1,2,3,4,5].map(i => (
      <svg key={i} className={`w-3.5 h-3.5 ${i <= Math.round(rating) ? 'text-yellow-400' : 'text-gray-300'}`}
        fill="currentColor" viewBox="0 0 20 20">
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
      </svg>
    ))}
    <span className="text-xs text-gray-600 ml-1">{rating.toFixed(1)}</span>
  </div>
);

const LevelBadge = ({ level }) => {
  const colors = {
    beginner: 'bg-green-100 text-green-700',
    intermediate: 'bg-yellow-100 text-yellow-700',
    advanced: 'bg-red-100 text-red-700',
  };
  return (
    <span className={`badge ${colors[level] || 'bg-gray-100 text-gray-700'}`}>
      {level.charAt(0).toUpperCase() + level.slice(1)}
    </span>
  );
};

export default function CourseCard({ course }) {
  const price = course.is_free ? 'Free' :
    course.discount_price
      ? `$${parseFloat(course.discount_price).toFixed(2)}`
      : `$${parseFloat(course.price).toFixed(2)}`;

  return (
    <Link to={`/courses/${course.slug}`} className="card group block hover:shadow-md transition-shadow">
      {/* Thumbnail */}
      <div className="aspect-video bg-gray-200 overflow-hidden">
        {course.thumbnail ? (
          <img
            src={course.thumbnail}
            alt={course.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700">
            <span className="text-white text-4xl font-bold opacity-30">
              {course.title?.[0]}
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="font-semibold text-gray-900 text-sm leading-snug line-clamp-2 flex-1">
            {course.title}
          </h3>
          <LevelBadge level={course.level} />
        </div>

        <p className="text-xs text-gray-500 mb-2">
          {course.instructor?.first_name
            ? `${course.instructor.first_name} ${course.instructor.last_name}`
            : course.instructor_name || 'Instructor'}
        </p>

        {course.rating > 0 && (
          <div className="mb-2">
            <StarRating rating={course.rating} />
            <span className="text-xs text-gray-500">({course.total_ratings?.toLocaleString() || course.total_students?.toLocaleString()} students)</span>
          </div>
        )}

        <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{course.total_lessons || 0} lessons</span>
            {course.duration_hours > 0 && (
              <><span>·</span><span>{course.duration_hours.toFixed(1)}h</span></>
            )}
          </div>
          <div className="flex items-center gap-1.5">
            {course.discount_price && !course.is_free && (
              <span className="text-xs text-gray-400 line-through">
                ${parseFloat(course.price).toFixed(2)}
              </span>
            )}
            <span className={`font-bold text-sm ${course.is_free ? 'text-green-600' : 'text-gray-900'}`}>
              {price}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}
