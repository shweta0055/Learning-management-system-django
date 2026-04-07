import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { jwtDecode } from 'jwt-decode';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,

      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken }),

      logout: () =>
        set({ user: null, accessToken: null, refreshToken: null }),

      isAuthenticated: () => {
        const { accessToken } = get();
        if (!accessToken) return false;
        try {
          const decoded = jwtDecode(accessToken);
          return decoded.exp * 1000 > Date.now();
        } catch {
          return false;
        }
      },

      isRole: (role) => {
        const { user } = get();
        return user?.role === role;
      },

      isAdminOrInstructor: () => {
        const { user } = get();
        return user?.role === 'admin' || user?.role === 'instructor';
      },
    }),
    { name: 'lms-auth' }
  )
);
