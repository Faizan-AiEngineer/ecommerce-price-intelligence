import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KPICardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  trendPositive?: boolean;
  subtitle?: string;
}

export const KPICard: React.FC<KPICardProps> = ({
  label,
  value,
  icon: Icon,
  trend,
  trendPositive,
  subtitle,
}) => {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-5 shadow-lg shadow-slate-950/20 hover:border-slate-700 transition-all">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-slate-400">{label}</span>
        <div className="rounded-xl bg-slate-800/80 p-2.5 text-sky-400 border border-slate-700/50">
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <div className="flex items-baseline justify-between">
        <span className="text-2xl font-bold tracking-tight text-slate-100">{value}</span>
        {trend && (
          <span
            className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
              trendPositive
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
            }`}
          >
            {trend}
          </span>
        )}
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
    </div>
  );
};
