import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { enrollmentsAPI, coursesAPI, certificatesAPI, recommendationsAPI } from '../services/api';
import { useAuthStore } from '../context/authStore';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

// ─── useEnrollment ────────────────────────────────────────────────────────────
export function useEnrollment(courseId) {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: enrollments } = useQuery({
    queryKey: ['my-enrollments'],
    queryFn: () => enrollmentsAPI.myEnrollments(),
    enabled: isAuthenticated(),
    select: (r) => r.data.results,
  });

  const isEnrolled = enrollments?.some((e) => e.course.id === courseId || e.course === courseId);
  const enrollment = enrollments?.find((e) => e.course.id === courseId || e.course === courseId);

  const enrollMutation = useMutation({
    mutationFn: () => enrollmentsAPI.enroll(courseId),
    onSuccess: () => {
      toast.success('Enrolled successfully!');
      qc.invalidateQueries(['my-enrollments']);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Enrollment failed'),
  });

  return { isEnrolled, enrollment, enroll: enrollMutation.mutate, enrolling: enrollMutation.isPending };
}

// ─── useWishlist ──────────────────────────────────────────────────────────────
export function useWishlist() {
  const { isAuthenticated } = useAuthStore();
  const qc = useQueryClient();

  const { data: wishlist } = useQuery({
    queryKey: ['wishlist'],
    queryFn: () => enrollmentsAPI.wishlist(),
    enabled: isAuthenticated(),
    select: (r) => r.data.results || r.data,
  });

  const toggleMutation = useMutation({
    mutationFn: (courseId) => enrollmentsAPI.toggleWishlist(courseId),
    onSuccess: () => qc.invalidateQueries(['wishlist']),
    onError: () => toast.error('Failed to update wishlist'),
  });

  const isWishlisted = (courseId) => wishlist?.some((w) => w.course?.id === courseId);

  return {
    wishlist,
    isWishlisted,
    toggleWishlist: toggleMutation.mutate,
    toggling: toggleMutation.isPending,
  };
}

// ─── useCourseProgress ────────────────────────────────────────────────────────
export function useCourseProgress(enrollmentId) {
  const qc = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: ({ lessonId, data }) =>
      enrollmentsAPI.updateProgress(enrollmentId, lessonId, data),
    onSuccess: () => {
      qc.invalidateQueries(['my-enrollments']);
    },
  });

  return {
    markComplete: (lessonId) =>
      updateMutation.mutate({ lessonId, data: { is_completed: true } }),
    updatePosition: (lessonId, position) =>
      updateMutation.mutate({ lessonId, data: { last_position: position } }),
    saving: updateMutation.isPending,
  };
}

// ─── useCertificate ───────────────────────────────────────────────────────────
export function useCertificate(courseId) {
  const qc = useQueryClient();

  const generateMutation = useMutation({
    mutationFn: () => certificatesAPI.generate(courseId),
    onSuccess: () => {
      toast.success('Certificate generated!');
      qc.invalidateQueries(['my-certificates']);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Generation failed'),
  });

  return { generateCertificate: generateMutation.mutate, generating: generateMutation.isPending };
}

// ─── useRecommendations ───────────────────────────────────────────────────────
export function useRecommendations() {
  const { isAuthenticated } = useAuthStore();

  const { data: forMe } = useQuery({
    queryKey: ['recommendations-for-me'],
    queryFn: () => recommendationsAPI.forMe(),
    enabled: isAuthenticated(),
    select: (r) => r.data.recommendations,
    staleTime: 10 * 60 * 1000,
  });

  const { data: trending } = useQuery({
    queryKey: ['trending'],
    queryFn: () => recommendationsAPI.trending(),
    select: (r) => r.data.trending,
    staleTime: 5 * 60 * 1000,
  });

  const { data: continueLearning } = useQuery({
    queryKey: ['continue-learning'],
    queryFn: () => recommendationsAPI.continueLearning(),
    enabled: isAuthenticated(),
    select: (r) => r.data.courses,
    staleTime: 2 * 60 * 1000,
  });

  return { forMe, trending, continueLearning };
}

// ─── useDebounce ──────────────────────────────────────────────────────────────
import { useState, useEffect } from 'react';

export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// ─── useLocalStorage ──────────────────────────────────────────────────────────
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
}
