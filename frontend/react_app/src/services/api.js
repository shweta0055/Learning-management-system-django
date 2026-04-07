import axios from 'axios';

const DJANGO_BASE = process.env.REACT_APP_DJANGO_API_URL || 'http://localhost:8000';
const FASTAPI_BASE = process.env.REACT_APP_FASTAPI_URL || 'http://localhost:8001';

// Django API client
export const djangoApi = axios.create({ baseURL: `${DJANGO_BASE}/api` });

// FastAPI client
export const fastapiClient = axios.create({ baseURL: FASTAPI_BASE });

// Attach token to every request
const authInterceptor = (config) => {
  const stored = localStorage.getItem('lms-auth');
  if (stored) {
    const { state } = JSON.parse(stored);
    if (state?.accessToken) {
      config.headers.Authorization = `Bearer ${state.accessToken}`;
    }
  }
  return config;
};

djangoApi.interceptors.request.use(authInterceptor);
fastapiClient.interceptors.request.use(authInterceptor);

// Auto-refresh on 401
djangoApi.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const stored = localStorage.getItem('lms-auth');
        const { state } = JSON.parse(stored);
        const { data } = await axios.post(`${DJANGO_BASE}/api/auth/token/refresh/`, {
          refresh: state.refreshToken,
        });
        // Update token in store
        const parsed = JSON.parse(stored);
        parsed.state.accessToken = data.access;
        localStorage.setItem('lms-auth', JSON.stringify(parsed));
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return djangoApi(originalRequest);
      } catch {
        localStorage.removeItem('lms-auth');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth ────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => djangoApi.post('/auth/register/', data),
  login: (data) => djangoApi.post('/auth/login/', data),
  logout: (refresh) => djangoApi.post('/auth/logout/', { refresh }),
  getProfile: () => djangoApi.get('/auth/profile/'),
  updateProfile: (data) => djangoApi.patch('/auth/profile/', data),
  changePassword: (data) => djangoApi.post('/auth/change-password/', data),
};

// ─── Courses ─────────────────────────────────────────────────────────────────
export const coursesAPI = {
  list: (params) => djangoApi.get('/courses/', { params }),
  detail: (slug) => djangoApi.get(`/courses/${slug}/`),
  create: (data) => djangoApi.post('/courses/create/', data),
  update: (id, data) => djangoApi.patch(`/courses/${id}/update/`, data),
  myCourses: () => djangoApi.get('/courses/my-courses/'),
  categories: () => djangoApi.get('/courses/categories/'),
  // Sections
  getSections: (courseId) => djangoApi.get(`/courses/${courseId}/sections/`),
  createSection: (courseId, data) => djangoApi.post(`/courses/${courseId}/sections/`, data),
  updateSection: (courseId, id, data) => djangoApi.patch(`/courses/${courseId}/sections/${id}/`, data),
  deleteSection: (courseId, id) => djangoApi.delete(`/courses/${courseId}/sections/${id}/`),
  // Lessons
  getLessons: (courseId) => djangoApi.get(`/courses/${courseId}/lessons/`),
  createLesson: (courseId, data) => djangoApi.post(`/courses/${courseId}/lessons/`, data),
  updateLesson: (courseId, id, data) => djangoApi.patch(`/courses/${courseId}/lessons/${id}/`, data),
  deleteLesson: (courseId, id) => djangoApi.delete(`/courses/${courseId}/lessons/${id}/`),
  // Reviews
  getReviews: (courseId) => djangoApi.get(`/courses/${courseId}/reviews/`),
  addReview: (courseId, data) => djangoApi.post(`/courses/${courseId}/reviews/`, data),
  // Announcements
  getAnnouncements: (courseId) => djangoApi.get(`/courses/${courseId}/announcements/`),
};

// ─── Enrollments ─────────────────────────────────────────────────────────────
export const enrollmentsAPI = {
  enroll: (courseId) => djangoApi.post('/enrollments/enroll/', { course: courseId }),
  myEnrollments: () => djangoApi.get('/enrollments/my/'),
  detail: (id) => djangoApi.get(`/enrollments/${id}/`),
  updateProgress: (enrollId, lessonId, data) =>
    djangoApi.post(`/enrollments/${enrollId}/progress/${lessonId}/`, data),
  wishlist: () => djangoApi.get('/enrollments/wishlist/'),
  toggleWishlist: (courseId) => djangoApi.post('/enrollments/wishlist/', { course_id: courseId }),
};

// ─── Quizzes ─────────────────────────────────────────────────────────────────
export const quizzesAPI = {
  getCourseQuizzes: (courseId) => djangoApi.get(`/quizzes/course/${courseId}/`),
  getQuiz: (id) => djangoApi.get(`/quizzes/${id}/`),
  submitQuiz: (quizId, data) => djangoApi.post(`/quizzes/${quizId}/submit/`, data),
  myAttempts: (quizId) => djangoApi.get(`/quizzes/${quizId}/my-attempts/`),
  // Assignments
  getCourseAssignments: (courseId) => djangoApi.get(`/quizzes/assignments/course/${courseId}/`),
  submitAssignment: (assignmentId, data) =>
    djangoApi.post(`/quizzes/assignments/${assignmentId}/submit/`, data),
};

// ─── Certificates ────────────────────────────────────────────────────────────
export const certificatesAPI = {
  myCertificates: () => djangoApi.get('/certificates/my/'),
  generate: (courseId) => djangoApi.post(`/certificates/generate/${courseId}/`),
  verify: (certId) => djangoApi.get(`/certificates/verify/${certId}/`),
};

// ─── Payments ────────────────────────────────────────────────────────────────
export const paymentsAPI = {
  checkout: (courseId, couponCode) =>
    djangoApi.post('/payments/checkout/', { course_id: courseId, coupon_code: couponCode }),
  validateCoupon: (code, courseId) =>
    djangoApi.post('/payments/coupon/validate/', { code, course_id: courseId }),
  myPayments: () => djangoApi.get('/payments/my/'),
};

// ─── FastAPI (analytics, recommendations, search) ────────────────────────────
export const analyticsAPI = {
  studentDashboard: () => fastapiClient.get('/api/analytics/dashboard/student'),
  instructorDashboard: () => fastapiClient.get('/api/analytics/dashboard/instructor'),
  adminDashboard: () => fastapiClient.get('/api/analytics/dashboard/admin'),
  courseAnalytics: (courseId) => fastapiClient.get(`/api/analytics/course/${courseId}`),
};

export const recommendationsAPI = {
  forMe: () => fastapiClient.get('/api/recommendations/courses'),
  continueLearning: () => fastapiClient.get('/api/recommendations/continue-learning'),
  trending: () => fastapiClient.get('/api/recommendations/trending'),
};

export const searchAPI = {
  courses: (params) => fastapiClient.get('/api/search/courses', { params }),
  suggestions: (q) => fastapiClient.get('/api/search/suggestions', { params: { q } }),
};

export const streamingAPI = {
  getPresignedUrl: (lessonId) => fastapiClient.get(`/api/streaming/presigned-url/${lessonId}`),
};
