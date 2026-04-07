import React from 'react';

// ─── LoadingSpinner ───────────────────────────────────────────────────────────
export function LoadingSpinner({ size = 'md', text = '' }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' };
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-10">
      <div className={`${sizes[size]} border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin`} />
      {text && <p className="text-sm text-gray-500">{text}</p>}
    </div>
  );
}

// ─── EmptyState ───────────────────────────────────────────────────────────────
export function EmptyState({ icon = '📭', title, description, action }) {
  return (
    <div className="text-center py-16 px-4">
      <div className="text-5xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      {description && <p className="text-gray-500 text-sm mb-6">{description}</p>}
      {action && (
        <div className="flex justify-center">{action}</div>
      )}
    </div>
  );
}

// ─── ProgressBar ──────────────────────────────────────────────────────────────
export function ProgressBar({ value, max = 100, showLabel = true, color = 'primary', size = 'md' }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const colors = {
    primary: 'bg-primary-600',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  };
  const heights = { sm: 'h-1.5', md: 'h-2.5', lg: 'h-4' };

  return (
    <div className="w-full">
      <div className={`bg-gray-200 rounded-full ${heights[size]} overflow-hidden`}>
        <div
          className={`${colors[color]} ${heights[size]} rounded-full transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-gray-500 mt-1 text-right">{Math.round(pct)}%</p>
      )}
    </div>
  );
}

// ─── Modal ────────────────────────────────────────────────────────────────────
export function Modal({ isOpen, onClose, title, children, size = 'md' }) {
  if (!isOpen) return null;
  const sizes = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl', xl: 'max-w-4xl' };
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className={`relative bg-white rounded-2xl shadow-2xl w-full ${sizes[size]} max-h-[90vh] flex flex-col`}>
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 className="text-xl font-bold text-gray-900">{title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        <div className="overflow-y-auto flex-1 p-6">{children}</div>
      </div>
    </div>
  );
}

// ─── Badge ────────────────────────────────────────────────────────────────────
export function Badge({ children, variant = 'gray' }) {
  const variants = {
    gray: 'bg-gray-100 text-gray-700',
    primary: 'bg-primary-100 text-primary-700',
    green: 'bg-green-100 text-green-700',
    yellow: 'bg-yellow-100 text-yellow-700',
    red: 'bg-red-100 text-red-700',
    purple: 'bg-purple-100 text-purple-700',
  };
  return (
    <span className={`badge ${variants[variant]}`}>{children}</span>
  );
}

// ─── Alert ────────────────────────────────────────────────────────────────────
export function Alert({ type = 'info', title, message, onClose }) {
  const styles = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    error: 'bg-red-50 border-red-200 text-red-800',
  };
  const icons = { info: 'ℹ️', success: '✅', warning: '⚠️', error: '❌' };
  return (
    <div className={`flex items-start gap-3 p-4 rounded-lg border ${styles[type]}`}>
      <span className="flex-shrink-0">{icons[type]}</span>
      <div className="flex-1">
        {title && <p className="font-semibold text-sm">{title}</p>}
        {message && <p className="text-sm mt-0.5">{message}</p>}
      </div>
      {onClose && (
        <button onClick={onClose} className="opacity-60 hover:opacity-100">&times;</button>
      )}
    </div>
  );
}

// ─── StarRating ───────────────────────────────────────────────────────────────
export function StarRating({ rating, max = 5, size = 'sm' }) {
  const sizes = { sm: 'w-3.5 h-3.5', md: 'w-5 h-5', lg: 'w-6 h-6' };
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: max }).map((_, i) => (
        <svg key={i} className={`${sizes[size]} ${i < Math.round(rating) ? 'text-yellow-400' : 'text-gray-200'}`}
          fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
      ))}
      {rating > 0 && <span className="text-xs text-gray-600 ml-1">{Number(rating).toFixed(1)}</span>}
    </div>
  );
}
