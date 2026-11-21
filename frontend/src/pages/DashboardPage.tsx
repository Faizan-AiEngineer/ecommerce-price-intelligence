import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Package2,
  ShoppingCart,
  DollarSign,
  TrendingDown,
  AlertTriangle,
  Clock,
  Layers,
  ArrowUpRight,
  TrendingUp,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { api } from '../lib/api';
import { KPICard } from '../components/KPICard';
import { StatusBadge } from '../components/StatusBadge';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => api.getDashboardSummary(),
    refetchInterval: 30000,
  });

  const { data: alertsData } = useQuery({
    queryKey: ['recent-alerts'],
    queryFn: () => api.getAlerts({ status: 'active' }),
  });

  if (isLoading) {
    return (
      <div className="p-8 space-y-6">
        <div className="h-8 w-64 bg-slate-800 rounded-lg animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-28 bg-slate-900 rounded-2xl border border-slate-800 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8">
        <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-rose-300">
          <h2 className="text-lg font-semibold">Failed to load dashboard data</h2>
          <p className="mt-1 text-sm text-rose-400">{String(error || 'Unknown error occurred')}</p>
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 rounded-xl text-sm font-medium transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const kpis = [
    { label: 'Monitored Products', value: data.monitored_products.toLocaleString(), icon: Package2 },
    { label: 'Active Retailers', value: data.active_retailers, icon: ShoppingCart },
    { label: 'Active Offers Monitored', value: data.active_offers.toLocaleString(), icon: Layers },
    { label: 'Average Catalog Price', value: `$${data.average_product_price.toFixed(2)}`, icon: DollarSign },
    { label: 'Recent Price Drops', value: data.recent_price_drops, icon: TrendingDown, trend: `${data.recent_price_drops} drops`, trendPositive: true },
    { label: 'Out of Stock Products', value: data.out_of_stock_products, icon: AlertTriangle },
    { label: 'Active Alerts', value: data.active_alerts, icon: TrendingUp },
    {
      label: 'Last Collection Run',
      value: data.last_successful_collection
        ? new Date(data.last_successful_collection).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        : 'Never',
      subtitle: data.last_successful_collection ? new Date(data.last_successful_collection).toLocaleDateString() : 'Awaiting first run',
      icon: Clock,
    },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100">Market Intelligence Radar</h2>
          <p className="text-sm text-slate-400 mt-1">Cross-retailer price movements, trends, and real-time competitor undercutting</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/competitors"
            className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-sm flex items-center gap-2 transition-colors shadow-lg shadow-sky-500/20"
          >
            <span>Compare Competitors</span>
            <ArrowUpRight className="h-4 w-4" />
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi) => (
          <KPICard
            key={kpi.label}
            label={kpi.label}
            value={kpi.value}
            icon={kpi.icon}
            trend={kpi.trend}
            trendPositive={kpi.trendPositive}
            subtitle={kpi.subtitle}
          />
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Price Trends Chart */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-base font-semibold text-slate-100">30-Day Market Price Trend</h3>
              <p className="text-xs text-slate-400 mt-0.5">Average, minimum, and maximum daily observed prices</p>
            </div>
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-slate-800 text-sky-400 border border-slate-700">
              USD
            </span>
          </div>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.price_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="date"
                  stroke="#64748b"
                  fontSize={11}
                  tickFormatter={(val) => {
                    const parts = val.split('-');
                    return parts.length >= 3 ? `${parts[1]}/${parts[2]}` : val;
                  }}
                />
                <YAxis stroke="#64748b" fontSize={11} tickFormatter={(val) => `$${val}`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', color: '#f8fafc' }}
                  formatter={(val: number) => [`$${val.toFixed(2)}`, 'Price']}
                />
                <Area type="monotone" dataKey="avg_price" stroke="#38bdf8" strokeWidth={2.5} fillOpacity={1} fill="url(#priceGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown Chart */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-base font-semibold text-slate-100">Catalog by Category</h3>
              <p className="text-xs text-slate-400 mt-0.5">Number of canonical products monitored per category</p>
            </div>
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-slate-800 text-emerald-400 border border-slate-700">
              Categories
            </span>
          </div>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.category_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="category" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', color: '#f8fafc' }}
                  formatter={(val: number) => [val, 'Products']}
                />
                <Bar dataKey="product_count" fill="#34d399" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Retailer Comparison Summary & Recent Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Retailers Overview */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
          <h3 className="text-base font-semibold text-slate-100 mb-1">Monitored Retailers</h3>
          <p className="text-xs text-slate-400 mb-4">Coverage and average prices across storefronts</p>

          <div className="space-y-3">
            {data.retailer_summary.map((ret) => (
              <div key={ret.retailer} className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/80 flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-semibold text-slate-200">{ret.retailer}</h4>
                  <p className="text-xs text-slate-400">{ret.offer_count} offers tracked</p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-sky-400">${ret.avg_price.toFixed(2)}</span>
                  <p className="text-[10px] text-slate-400">avg offer</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Alerts Feed */}
        <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-slate-100">Recent Price Intelligence Alerts</h3>
              <p className="text-xs text-slate-400">Triggered competitor moves, discounts, and inventory changes</p>
            </div>
            <Link to="/alerts" className="text-xs font-medium text-sky-400 hover:text-sky-300">
              View all &rarr;
            </Link>
          </div>

          <div className="space-y-2.5">
            {alertsData?.items && alertsData.items.length > 0 ? (
              alertsData.items.slice(0, 5).map((alert) => (
                <div
                  key={alert.id}
                  className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/80 flex items-center justify-between gap-4"
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-slate-200">{alert.product_name}</span>
                      <StatusBadge status={alert.alert_type} type="alert" />
                    </div>
                    <p className="text-xs text-slate-400">{alert.message}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="text-xs text-slate-400">
                      {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500 py-6 text-center">No active alerts at this moment.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
