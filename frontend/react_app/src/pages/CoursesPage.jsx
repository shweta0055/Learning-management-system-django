import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { coursesAPI } from '../services/api';
import CourseCard from '../components/courses/CourseCard';

const LEVELS = ['', 'beginner', 'intermediate', 'advanced'];

// Skeleton card shown while loading
const SkeletonCard = () => (
  <div className="card animate-pulse">
    <div className="aspect-video bg-gray-200" />
    <div className="p-4 space-y-3">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-3 bg-gray-200 rounded w-1/2" />
      <div className="h-3 bg-gray-200 rounded w-1/3" />
    </div>
  </div>
);

export default function CoursesPage() {
  const [filters, setFilters] = useState({ level: '', ordering: '-rating', page: 1 });
  const [categoryId, setCategoryId] = useState('');

  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: () => coursesAPI.categories(),
    select: (r) => r.data,
    staleTime: 10 * 60 * 1000, // categories rarely change
  });

  const { data, isLoading, isError } = useQuery({
    queryKey: ['courses', filters, categoryId],
    queryFn: () => coursesAPI.list({ ...filters, category: categoryId || undefined }),
    select: (r) => r.data,
    keepPreviousData: true, // prevents blank flash when filters change
    staleTime: 60 * 1000,
  });

  const set = (key, val) => setFilters((f) => ({ ...f, [key]: val, page: 1 }));

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">All Courses</h1>
        <p className="text-gray-500 mt-2">Explore our full catalog of expert-led courses</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar filters */}
        <aside className="w-full lg:w-64 flex-shrink-0">
          <div className="card p-5 space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-3 text-sm">Category</h3>
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="radio" name="cat" checked={!categoryId} onChange={() => setCategoryId('')} className="text-primary-600" />
                  <span className="text-sm text-gray-700">All Categories</span>
                </label>
                {categoriesData?.map((cat) => (
                  <label key={cat.id} className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="cat" checked={categoryId === String(cat.id)} onChange={() => setCategoryId(String(cat.id))} className="text-primary-600" />
                    <span className="text-sm text-gray-700">{cat.name}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-3 text-sm">Level</h3>
              <div className="space-y-2">
                {LEVELS.map((level) => (
                  <label key={level} className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="level" checked={filters.level === level} onChange={() => set('level', level)} className="text-primary-600" />
                    <span className="text-sm text-gray-700">{level ? level.charAt(0).toUpperCase() + level.slice(1) : 'All Levels'}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-3 text-sm">Sort By</h3>
              <select value={filters.ordering} onChange={(e) => set('ordering', e.target.value)} className="input text-sm">
                <option value="-rating">Top Rated</option>
                <option value="-total_students">Most Popular</option>
                <option value="-created_at">Newest</option>
                <option value="price">Price: Low to High</option>
                <option value="-price">Price: High to Low</option>
              </select>
            </div>
          </div>
        </aside>

        {/* Course grid */}
        <div className="flex-1">
          {isError && (
            <div className="card p-8 text-center text-red-500">
              <p className="font-medium">Failed to load courses.</p>
              <p className="text-sm mt-1 text-gray-500">Please check your connection and try again.</p>
            </div>
          )}

          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
              {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          ) : data?.results?.length > 0 ? (
            <>
              <p className="text-sm text-gray-500 mb-4">{data.count} courses found</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                {data.results.map((course) => <CourseCard key={course.id} course={course} />)}
              </div>
              {/* Pagination */}
              {data.count > 20 && (
                <div className="flex justify-center gap-2 mt-8">
                  <button
                    disabled={filters.page === 1}
                    onClick={() => set('page', filters.page - 1)}
                    className="btn-secondary text-sm py-1.5 px-3 disabled:opacity-40"
                  >← Prev</button>
                  <span className="px-4 py-1.5 text-sm text-gray-600">Page {filters.page}</span>
                  <button
                    disabled={!data.next}
                    onClick={() => set('page', filters.page + 1)}
                    className="btn-secondary text-sm py-1.5 px-3 disabled:opacity-40"
                  >Next →</button>
                </div>
              )}
            </>
          ) : !isLoading ? (
            <div className="text-center py-20 text-gray-400">
              <div className="text-5xl mb-4">📚</div>
              <p className="text-lg font-medium">No courses found</p>
              <p className="text-sm mt-2">Try adjusting your filters</p>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
