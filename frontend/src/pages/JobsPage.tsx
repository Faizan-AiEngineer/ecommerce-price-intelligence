import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RefreshCw, Play, Clock, Database, AlertCircle, CheckCircle } from 'lucide-react';
import { api } from '../lib/api';
import { StatusBadge } from '../components/StatusBadge';

export const JobsPage: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: jobsData, isLoading, error } = useQuery({
    queryKey: ['collection-jobs'],
    queryFn: () => api.getJobs(),
    refetchInterval: 5000,
  });

  const triggerMutation = useMutation({
    mutationFn: () => api.triggerJob(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collection-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
    },
  });

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Title & Action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100">Collection Pipeline Jobs</h2>
          <p className="text-sm text-slate-400 mt-1">Audit trail of automated data harvesting runs, record volumes, and status</p>
        </div>
        <button
          onClick={() => triggerMutation.mutate()}
          disabled={triggerMutation.isPending}
          className="px-4 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 disabled:opacity-50 text-slate-950 font-bold text-sm flex items-center gap-2 transition-all shadow-lg shadow-sky-500/20"
        >
          <Play className="h-4 w-4 fill-current" />
          <span>{triggerMutation.isPending ? 'Initiating Pipeline...' : 'Run Pipeline Now'}</span>
        </button>
      </div>

      {/* Sources Overview Banner */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="rounded-2xl bg-sky-500/10 p-3.5 text-sky-400 border border-sky-500/20">
            <Database className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">Autonomous Scheduler Engine</h3>
            <p className="text-xs text-slate-400 mt-0.5">Recurring background extraction active with strict overlap prevention (max_instances=1)</p>
          </div>
        </div>
        <div className="flex items-center gap-6 text-xs text-slate-300">
          <div>
            Interval: <span className="font-semibold text-sky-400">Every 60 Minutes</span>
          </div>
          <div>
            Connectors: <span className="font-semibold text-emerald-400">Demo Catalog & Playwright</span>
          </div>
        </div>
      </div>

      {/* Execution History Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 shadow-xl shadow-slate-950/20 overflow-hidden">
        <div className="p-6 border-b border-slate-800/80">
          <h3 className="text-base font-semibold text-slate-100">Pipeline Execution History</h3>
          <p className="text-xs text-slate-400 mt-0.5">Detailed records of extraction runs, batch loads, and error logs</p>
        </div>

        {isLoading ? (
          <div className="p-12 text-center text-slate-400">Loading collection runs...</div>
        ) : error ? (
          <div className="p-12 text-center text-rose-400">Error loading jobs history.</div>
        ) : !jobsData?.items.length ? (
          <div className="p-12 text-center text-slate-400">No collection jobs have run yet. Click "Run Pipeline Now" to initiate.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950/60 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4">Run ID</th>
                  <th className="px-6 py-4">Data Source</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Extracted</th>
                  <th className="px-6 py-4">Loaded</th>
                  <th className="px-6 py-4">Duration</th>
                  <th className="px-6 py-4 text-right">Started At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {jobsData.items.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-mono text-xs font-semibold text-slate-300">
                      #{job.id}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-200">{job.source_name}</td>
                    <td className="px-6 py-4">
                      <StatusBadge status={job.status} type="job" />
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200">
                      {job.records_extracted.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 font-semibold text-emerald-400">
                      {job.records_loaded.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400 font-mono">
                      {job.duration_seconds !== null ? `${job.duration_seconds}s` : 'In progress'}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400 text-right">
                      {job.started_at ? new Date(job.started_at).toLocaleString() : 'N/A'}
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
