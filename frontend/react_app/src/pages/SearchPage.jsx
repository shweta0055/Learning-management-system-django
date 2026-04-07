import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { searchAPI } from '../services/api';
import CourseCard from '../components/courses/CourseCard';

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState({
    q: searchParams.get('q') || '',
    level: '',
    sort_by: 'relevance',
    page: 1,
  });

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) setFilters((f) => ({ ...f, q }));
  }, [searchParams]);

  const { data, isLoading } = useQuery({
    queryKey: ['search', filters],
    queryFn: () => searchAPI.courses(filters),
    select: (r) => r.data,
    enabled: filters.q.length >= 2,
    staleTime: 30 * 1000,
    keepPreviousData: true,
  });

  const set = (k, v) => setFilters((f) => ({ ...f, [k]: v, page: 1 }));

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          {filters.q ? `Results for "${filters.q}"` : 'Search Courses'}
        </h1>
        {data && <p className="text-gray-500 text-sm mt-1">{data.total} courses found</p>}
      </div>

      {/* Filter bar */}
      <div className="flex flex-wrap gap-3 mb-8">
        <select value={filters.level} onChange={(e) => set('level', e.target.value)} className="input w-auto text-sm">
          <option value="">All Levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
        <select value={filters.sort_by} onChange={(e) => set('sort_by', e.target.value)} className="input w-auto text-sm">
          <option value="relevance">Relevance</option>
          <option value="rating">Top Rated</option>
          <option value="newest">Newest</option>
          <option value="price_asc">Price: Low</option>
          <option value="price_desc">Price: High</option>
        </select>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="aspect-video bg-gray-200" />
              <div className="p-4 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4" />
                <div className="h-3 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : data?.results?.length > 0 ? (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {data.results.map((course) => <CourseCard key={course.id} course={course} />)}
          </div>
          {data.total_pages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              <button disabled={filters.page === 1} onClick={() => set('page', filters.page - 1)} className="btn-secondary text-sm py-1.5 px-3 disabled:opacity-40">← Prev</button>
              <span className="px-4 py-1.5 text-sm text-gray-600">Page {filters.page} of {data.total_pages}</span>
              <button disabled={filters.page >= data.total_pages} onClick={() => set('page', filters.page + 1)} className="btn-secondary text-sm py-1.5 px-3 disabled:opacity-40">Next →</button>
            </div>
          )}
        </>
      ) : filters.q ? (
        <div className="text-center py-20 text-gray-400">
          <div className="text-5xl mb-4">🔍</div>
          <p className="text-lg">No courses found for "{filters.q}"</p>
          <p className="text-sm mt-2">Try different keywords or remove filters</p>
        </div>
      ) : (
        <div className="text-center py-20 text-gray-400">
          <div className="text-5xl mb-4">🔍</div>
          <p>Enter a search term to find courses</p>
        </div>
      )}
    </div>
  );
}
