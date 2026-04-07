import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../context/authStore';
import { authAPI } from '../services/api';
import { toast } from 'react-toastify';

export default function Navbar() {
  const { user, accessToken, refreshToken, logout, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchQ, setSearchQ] = useState('');

  const handleLogout = async () => {
    try { await authAPI.logout(refreshToken); } catch {}
    logout();
    navigate('/');
    toast.success('Logged out successfully');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQ.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQ.trim())}`);
      setSearchQ('');
    }
  };

  const navLink = (to, label) => (
    <Link
      to={to}
      className={`text-sm font-medium transition-colors ${
        location.pathname === to
          ? 'text-primary-600'
          : 'text-gray-700 hover:text-primary-600'
      }`}
    >
      {label}
    </Link>
  );

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 flex-shrink-0">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">L</span>
            </div>
            <span className="font-bold text-gray-900 text-lg">LearnHub</span>
          </Link>

          {/* Search */}
          <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-md">
            <div className="relative w-full">
              <input
                type="text"
                value={searchQ}
                onChange={(e) => setSearchQ(e.target.value)}
                placeholder="Search courses..."
                className="input pr-10 text-sm"
              />
              <button type="submit" className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-primary-600">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </form>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6">
            {navLink('/courses', 'Courses')}
            {isAuthenticated() && navLink('/dashboard', 'My Learning')}
            {user?.role === 'instructor' && navLink('/instructor', 'Teach')}
            {user?.role === 'admin' && navLink('/admin-panel', 'Admin')}

            {isAuthenticated() ? (
              <div className="relative group">
                <button className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-semibold text-sm">
                    {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase()}
                  </div>
                </button>
                <div className="absolute right-0 mt-1 w-48 bg-white border border-gray-200 rounded-xl shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all py-1">
                  <Link to="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Profile</Link>
                  <Link to="/certificates" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Certificates</Link>
                  <hr className="my-1 border-gray-100" />
                  <button onClick={handleLogout} className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">
                    Logout
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link to="/login" className="text-sm font-medium text-gray-700 hover:text-primary-600">Log in</Link>
                <Link to="/register" className="btn-primary text-sm py-1.5">Get Started</Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <button className="md:hidden p-2" onClick={() => setMenuOpen(!menuOpen)}>
            <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen
                ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />}
            </svg>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden py-4 border-t border-gray-100 space-y-3">
            <form onSubmit={handleSearch} className="pb-2">
              <input
                type="text"
                value={searchQ}
                onChange={(e) => setSearchQ(e.target.value)}
                placeholder="Search courses..."
                className="input text-sm"
              />
            </form>
            <Link to="/courses" className="block text-sm font-medium text-gray-700" onClick={() => setMenuOpen(false)}>Courses</Link>
            {isAuthenticated() && (
              <>
                <Link to="/dashboard" className="block text-sm font-medium text-gray-700" onClick={() => setMenuOpen(false)}>My Learning</Link>
                <Link to="/profile" className="block text-sm font-medium text-gray-700" onClick={() => setMenuOpen(false)}>Profile</Link>
                <button onClick={handleLogout} className="block text-sm font-medium text-red-600">Logout</button>
              </>
            )}
            {!isAuthenticated() && (
              <div className="flex gap-3">
                <Link to="/login" className="btn-secondary text-sm" onClick={() => setMenuOpen(false)}>Log in</Link>
                <Link to="/register" className="btn-primary text-sm" onClick={() => setMenuOpen(false)}>Register</Link>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
