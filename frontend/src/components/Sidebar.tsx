import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  Scale,
  Bell,
  RefreshCw,
  Settings,
  TrendingUp,
} from 'lucide-react';

interface SidebarProps {
  activeAlertsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeAlertsCount = 0 }) => {
  const navItems = [
    { to: '/', label: 'Overview', icon: LayoutDashboard },
    { to: '/products', label: 'Product Explorer', icon: Search },
    { to: '/competitors', label: 'Competitor Intel', icon: Scale },
    { to: '/alerts', label: 'Price Alerts', icon: Bell, badge: activeAlertsCount },
    { to: '/jobs', label: 'Collection Jobs', icon: RefreshCw },
    { to: '/settings', label: 'Settings & Export', icon: Settings },
  ];

  return (
    <aside className="w-64 flex-shrink-0 border-r border-slate-800 bg-slate-900/95 flex flex-col justify-between h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-sky-500/20">
            <TrendingUp className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-100 tracking-tight leading-tight">PriceIntel</h1>
            <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Competitor Radar</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-sky-500/15 text-sky-400 border border-sky-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <item.icon className="h-4 w-4" />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/80">
        <div className="rounded-xl bg-slate-950/60 p-3 border border-slate-800/50">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-semibold text-slate-300">Live Surveillance</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">Automated multi-retailer monitoring active</p>
        </div>
      </div>
    </aside>
  );
};
