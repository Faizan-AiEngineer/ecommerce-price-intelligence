import React from 'react';

interface StatusBadgeProps {
  status: string;
  type?: 'stock' | 'alert' | 'job';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'stock' }) => {
  let colorStyles = 'bg-slate-800 text-slate-300 border-slate-700';

  if (type === 'stock') {
    switch (status.toLowerCase()) {
      case 'in_stock':
        colorStyles = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
        break;
      case 'limited':
        colorStyles = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
        break;
      case 'out_of_stock':
        colorStyles = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
        break;
    }
  } else if (type === 'alert') {
    switch (status.toLowerCase()) {
      case 'active':
        colorStyles = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
        break;
      case 'acknowledged':
        colorStyles = 'bg-sky-500/10 text-sky-400 border-sky-500/30';
        break;
      case 'resolved':
        colorStyles = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
        break;
    }
  } else if (type === 'job') {
    switch (status.toLowerCase()) {
      case 'completed':
        colorStyles = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
        break;
      case 'running':
        colorStyles = 'bg-sky-500/10 text-sky-400 border-sky-500/30 animate-pulse';
        break;
      case 'failed':
        colorStyles = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
        break;
      case 'queued':
        colorStyles = 'bg-slate-800 text-slate-400 border-slate-700';
        break;
    }
  }

  const formatText = (text: string) => text.replace(/_/g, ' ');

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorStyles} capitalize`}>
      {formatText(status)}
    </span>
  );
};
