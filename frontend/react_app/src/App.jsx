import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './context/authStore';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import CoursesPage from './pages/CoursesPage';
import CourseDetailPage from './pages/CourseDetailPage';
import LearnPage from './pages/LearnPage';
import DashboardPage from './pages/DashboardPage';
import InstructorDashboardPage from './pages/InstructorDashboardPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import ProfilePage from './pages/ProfilePage';
import QuizPage from './pages/QuizPage';
import CheckoutPage from './pages/CheckoutPage';
import CertificatesPage from './pages/CertificatesPage';
import SearchPage from './pages/SearchPage';
import NotFoundPage from './pages/NotFoundPage';

// Layout
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// ─── Hydration gate ────────────────────────────────────────────────────────
// Prevents blank flash: waits for Zustand to rehydrate from localStorage
// before rendering protected routes. Shows nothing for one frame (~16ms).
function useHasHydrated() {
  const [hasHydrated, setHasHydrated] = useState(false);
  useEffect(() => {
    // Zustand persist rehydrates synchronously from localStorage on mount
    setHasHydrated(true);
  }, []);
  return hasHydrated;
}

// ─── Route guards ──────────────────────────────────────────────────────────
const PrivateRoute = ({ children }) => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const hydrated = useHasHydrated();
  // While not yet hydrated, render nothing (avoids redirect flash)
  if (!hydrated) return null;
  return isAuthenticated() ? children : <Navigate to="/login" replace />;
};

const RoleRoute = ({ children, roles }) => {
  const { user, isAuthenticated } = useAuthStore();
  const hydrated = useHasHydrated();
  if (!hydrated) return null;
  if (!isAuthenticated()) return <Navigate to="/login" replace />;
  if (!roles.includes(user?.role)) return <Navigate to="/dashboard" replace />;
  return children;
};

const GuestRoute = ({ children }) => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const hydrated = useHasHydrated();
  if (!hydrated) return null;
  return !isAuthenticated() ? children : <Navigate to="/dashboard" replace />;
};

// ─── App ────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-gray-50">
        <Navbar />
        <main className="flex-1">
          <Routes>
            {/* Public routes — always render immediately */}
            <Route path="/" element={<HomePage />} />
            <Route path="/courses" element={<CoursesPage />} />
            <Route path="/courses/:slug" element={<CourseDetailPage />} />
            <Route path="/search" element={<SearchPage />} />

            {/* Auth routes */}
            <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
            <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />

            {/* Student routes */}
            <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
            <Route path="/learn/:slug" element={<PrivateRoute><LearnPage /></PrivateRoute>} />
            <Route path="/learn/:slug/quiz/:quizId" element={<PrivateRoute><QuizPage /></PrivateRoute>} />
            <Route path="/checkout/:courseId" element={<PrivateRoute><CheckoutPage /></PrivateRoute>} />
            <Route path="/certificates" element={<PrivateRoute><CertificatesPage /></PrivateRoute>} />
            <Route path="/profile" element={<PrivateRoute><ProfilePage /></PrivateRoute>} />

            {/* Instructor routes */}
            <Route path="/instructor" element={
              <RoleRoute roles={['instructor', 'admin']}><InstructorDashboardPage /></RoleRoute>
            } />

            {/* Admin routes */}
            <Route path="/admin-panel" element={
              <RoleRoute roles={['admin']}><AdminDashboardPage /></RoleRoute>
            } />

            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}
