import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-12 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">L</span>
            </div>
            <span className="text-white font-bold text-lg">LearnHub</span>
          </div>
          <p className="text-sm leading-relaxed">
            Empowering learners worldwide with quality online education.
          </p>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3 text-sm">Platform</h4>
          <ul className="space-y-2 text-sm">
            <li><Link to="/courses" className="hover:text-white transition-colors">Browse Courses</Link></li>
            <li><Link to="/register" className="hover:text-white transition-colors">Become a Student</Link></li>
            <li><Link to="/register?role=instructor" className="hover:text-white transition-colors">Teach on LearnHub</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3 text-sm">Support</h4>
          <ul className="space-y-2 text-sm">
            <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Contact Us</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3 text-sm">Company</h4>
          <ul className="space-y-2 text-sm">
            <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-gray-800 py-4 text-center text-xs">
        © {new Date().getFullYear()} LearnHub. All rights reserved.
      </div>
    </footer>
  );
}
