import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      retryDelay: 1000,
      staleTime: 30 * 1000,        // 30 seconds — data won't re-fetch on every nav
      gcTime: 5 * 60 * 1000,       // 5 minutes cache
      refetchOnWindowFocus: false, // prevents re-fetch flash when switching tabs
      refetchOnMount: true,
    },
  },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ToastContainer position="top-right" autoClose={3000} hideProgressBar={false} />
    </QueryClientProvider>
  </React.StrictMode>
);
