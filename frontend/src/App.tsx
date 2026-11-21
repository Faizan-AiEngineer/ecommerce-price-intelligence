import React from 'react';
import { Outlet } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Sidebar } from './components/Sidebar';
import { api } from './lib/api';

export default function App() {
  const { data: summary } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => api.getDashboardSummary(),
    refetchInterval: 60000,
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      {/* Fixed Sidebar */}
      <Sidebar activeAlertsCount={summary?.active_alerts ?? 0} />

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}
