import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { authAPI } from '../services/api';
import { useAuthStore } from '../context/authStore';
import { toast } from 'react-toastify';

export default function ProfilePage() {
  const { user, setAuth, accessToken, refreshToken } = useAuthStore();
  const [tab, setTab] = useState('profile');

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      bio: user?.bio || '',
      phone: user?.phone || '',
    }
  });

  const { register: regPwd, handleSubmit: handlePwd, formState: { errors: pwdErrors }, reset: resetPwd } = useForm();

  const updateMutation = useMutation({
    mutationFn: (data) => authAPI.updateProfile(data),
    onSuccess: (res) => {
      setAuth(res.data, accessToken, refreshToken);
      toast.success('Profile updated!');
    },
    onError: () => toast.error('Update failed'),
  });

  const pwdMutation = useMutation({
    mutationFn: (data) => authAPI.changePassword(data),
    onSuccess: () => { toast.success('Password changed!'); resetPwd(); },
    onError: (err) => toast.error(err.response?.data?.old_password?.[0] || 'Failed'),
  });

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Account Settings</h1>

      <div className="flex gap-1 border-b border-gray-200 mb-8">
        {['profile', 'password'].map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-5 py-2.5 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
              tab === t ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}>
            {t === 'profile' ? 'Profile' : 'Password'}
          </button>
        ))}
      </div>

      {tab === 'profile' && (
        <div className="card p-6">
          <div className="flex items-center gap-4 mb-6 pb-6 border-b border-gray-100">
            <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-xl">
              {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase()}
            </div>
            <div>
              <p className="font-semibold text-gray-900">{user?.first_name} {user?.last_name}</p>
              <p className="text-sm text-gray-500">{user?.email}</p>
              <span className="badge bg-primary-100 text-primary-700 mt-1 capitalize">{user?.role}</span>
            </div>
          </div>

          <form onSubmit={handleSubmit((d) => updateMutation.mutate(d))} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input {...register('first_name')} className="input" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <input {...register('last_name')} className="input" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input {...register('phone')} className="input" placeholder="+1 (555) 000-0000" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
              <textarea {...register('bio')} rows={4} className="input" placeholder="Tell us about yourself..." />
            </div>
            <button type="submit" disabled={updateMutation.isPending} className="btn-primary py-2.5">
              {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>
      )}

      {tab === 'password' && (
        <div className="card p-6">
          <form onSubmit={handlePwd((d) => pwdMutation.mutate(d))} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
              <input type="password" {...regPwd('old_password', { required: 'Required' })} className="input" />
              {pwdErrors.old_password && <p className="text-red-500 text-xs mt-1">{pwdErrors.old_password.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
              <input type="password" {...regPwd('new_password', { required: 'Required', minLength: { value: 8, message: 'Min 8 chars' } })} className="input" />
              {pwdErrors.new_password && <p className="text-red-500 text-xs mt-1">{pwdErrors.new_password.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
              <input type="password" {...regPwd('new_password_confirm', { required: 'Required' })} className="input" />
            </div>
            <button type="submit" disabled={pwdMutation.isPending} className="btn-primary py-2.5">
              {pwdMutation.isPending ? 'Updating...' : 'Update Password'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
