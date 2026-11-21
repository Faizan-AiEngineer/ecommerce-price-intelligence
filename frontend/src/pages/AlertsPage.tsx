import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Bell,
  CheckCircle2,
  Filter,
  TrendingDown,
  TrendingUp,
  AlertOctagon,
  Package,
} from 'lucide-react';
import { api } from '../lib/api';
import { StatusBadge } from '../components/StatusBadge';

export const AlertsPage: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['alerts-list', statusFilter, typeFilter],
    queryFn: () =>
      api.getAlerts({
        status: statusFilter || undefined,
        alert_type: typeFilter || undefined,
      }),
  });

  const acknowledgeMutation = useMutation({
    mutationFn: (alertId: number) => api.acknowledgeAlert(alertId, 'acknowledged'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts-list'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
    },
  });

  const alertTypes = [
    { value: 'price_drop', label: 'Price Drops' },
    { value: 'price_increase', label: 'Price Increases' },
    { value: 'competitor_undercut', label: 'Competitor Undercut' },
    { value: 'out_of_stock', label: 'Out of Stock' },
    { value: 'back_in_stock', label: 'Back in Stock' },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100">Pricing & Stock Alerts</h2>
          <p className="text-sm text-slate-400 mt-1">Real-time triggers generated from automated collection and threshold monitoring</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-800 text-sky-400 border border-slate-700">
            {data?.total ?? 0} Recorded Alerts
          </span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-4 shadow-xl shadow-slate-950/20 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="py-1.5 px-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none"
            >
              <option value="">All Statuses</option>
              <option value="active">Active Only</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="py-1.5 px-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none"
          >
            <option value="">All Trigger Types</option>
            {alertTypes.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <span className="text-xs text-slate-400">
          Showing triggers updated via automated surveillance
        </span>
      </div>

      {/* Alerts Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 shadow-xl shadow-slate-950/20 overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400">Scanning alert events...</div>
        ) : error ? (
          <div className="p-12 text-center text-rose-400">Error loading alerts.</div>
        ) : !data?.items.length ? (
          <div className="p-12 text-center text-slate-400">No alerts matching your criteria.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950/60 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4">Trigger Type</th>
                  <th className="px-6 py-4">Product</th>
                  <th className="px-6 py-4">Retailer</th>
                  <th className="px-6 py-4">Event Details</th>
                  <th className="px-6 py-4">Timestamp</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {data.items.map((alert) => (
                  <tr key={alert.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4">
                      <StatusBadge status={alert.alert_type} type="alert" />
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-100 max-w-xs truncate">
                      {alert.product_name}
                    </td>
                    <td className="px-6 py-4 text-slate-300 font-medium">
                      {alert.retailer_name || 'Market Comparison'}
                    </td>
                    <td className="px-6 py-4 text-slate-300 max-w-sm">
                      {alert.message}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {new Date(alert.created_at).toLocaleString([], {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={alert.status} type="alert" />
                    </td>
                    <td className="px-6 py-4 text-right">
                      {alert.status === 'active' ? (
                        <button
                          onClick={() => acknowledgeMutation.mutate(alert.id)}
                          disabled={acknowledgeMutation.isPending}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-400 text-xs font-semibold transition-colors border border-slate-700"
                        >
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          <span>Acknowledge</span>
                        </button>
                      ) : (
                        <span className="text-xs text-slate-500 italic">Dismissed</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
