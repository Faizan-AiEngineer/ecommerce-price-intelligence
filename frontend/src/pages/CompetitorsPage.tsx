import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Scale,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Filter,
} from 'lucide-react';
import { api } from '../lib/api';

export const CompetitorsPage: React.FC = () => {
  const [selectedRefRetailer, setSelectedRefRetailer] = useState<number>(1);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [page, setPage] = useState<number>(0);
  const limit = 25;

  const { data: retailersData } = useQuery({
    queryKey: ['retailers-list'],
    queryFn: () => api.getRetailers(),
  });

  const { data: comparisonData, isLoading, error } = useQuery({
    queryKey: ['competitors-comparison', selectedRefRetailer, selectedCategory, page],
    queryFn: () =>
      api.getCompetitorComparison(selectedRefRetailer, selectedCategory || undefined, limit, page * limit),
    enabled: !!selectedRefRetailer,
  });

  const categories = ['Laptops', 'Smartphones', 'Audio', 'Wearables', 'Home Office', 'Accessories'];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100">Competitor Price Intelligence</h2>
          <p className="text-sm text-slate-400 mt-1">Direct head-to-head pricing benchmark against market competitors</p>
        </div>

        {/* Reference Retailer Selector */}
        <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 p-2 rounded-2xl shadow-lg">
          <span className="text-xs font-semibold text-slate-400 pl-2">Reference Store:</span>
          <select
            value={selectedRefRetailer}
            onChange={(e) => {
              setSelectedRefRetailer(Number(e.target.value));
              setPage(0);
            }}
            className="bg-slate-950 border border-slate-800 text-sky-400 font-semibold text-sm rounded-xl px-3 py-1.5 focus:outline-none focus:border-sky-500"
          >
            {retailersData?.items.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} ({r.country})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Competitiveness Summary KPIs */}
      {comparisonData?.summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-5 shadow-lg">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Head-to-Head Comparisons</span>
              <Scale className="h-4 w-4 text-sky-400" />
            </div>
            <div className="text-2xl font-bold text-slate-100">{comparisonData.summary.total_comparisons}</div>
            <div className="text-xs text-slate-500 mt-1">Matched product offers</div>
          </div>

          <div className="rounded-2xl border border-rose-500/20 bg-rose-500/5 p-5 shadow-lg">
            <div className="flex items-center justify-between text-rose-400 mb-2">
              <span className="text-xs font-medium">Competitor Undercutting</span>
              <TrendingDown className="h-4 w-4 text-rose-400" />
            </div>
            <div className="text-2xl font-bold text-rose-400">{comparisonData.summary.competitor_cheaper_count}</div>
            <div className="text-xs text-rose-400/70 mt-1">Products where competitors are cheaper</div>
          </div>

          <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5 shadow-lg">
            <div className="flex items-center justify-between text-emerald-400 mb-2">
              <span className="text-xs font-medium">You Have Lowest Price</span>
              <TrendingUp className="h-4 w-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400">{comparisonData.summary.reference_cheaper_count}</div>
            <div className="text-xs text-emerald-400/70 mt-1">Products where you win on price</div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-5 shadow-lg">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Price Parity</span>
              <AlertTriangle className="h-4 w-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-slate-300">{comparisonData.summary.same_price_count}</div>
            <div className="text-xs text-slate-500 mt-1">Identical market pricing</div>
          </div>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-400" />
          <span className="text-xs font-medium text-slate-400">Filter Category:</span>
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setPage(0);
            }}
            className="py-1.5 px-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none"
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <span className="text-xs text-slate-400">
          Showing results for <span className="text-sky-400 font-semibold">{comparisonData?.reference_retailer}</span>
        </span>
      </div>

      {/* Comparison Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 shadow-xl shadow-slate-950/20 overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400">Calculating competitor price deltas...</div>
        ) : error ? (
          <div className="p-12 text-center text-rose-400">Failed to load competitor comparisons.</div>
        ) : !comparisonData?.items.length ? (
          <div className="p-12 text-center text-slate-400">No competitor offerings found for this retailer.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950/60 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4">Product</th>
                  <th className="px-6 py-4">{comparisonData.reference_retailer} Price</th>
                  <th className="px-6 py-4">Competitor</th>
                  <th className="px-6 py-4">Competitor Price</th>
                  <th className="px-6 py-4">Difference ($)</th>
                  <th className="px-6 py-4">Difference (%)</th>
                  <th className="px-6 py-4 text-right">Verdict</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {comparisonData.items.map((row, idx) => {
                  const isUndercut = row.cheaper_competitor;
                  return (
                    <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-semibold text-slate-100">{row.product_name}</div>
                        <div className="text-xs text-slate-400">{row.category}</div>
                      </td>
                      <td className="px-6 py-4 font-bold text-slate-200">${row.reference_price.toFixed(2)}</td>
                      <td className="px-6 py-4 font-medium text-slate-300">{row.competitor_retailer}</td>
                      <td className="px-6 py-4 font-bold text-slate-200">${row.competitor_price.toFixed(2)}</td>
                      <td className="px-6 py-4 font-mono font-medium text-slate-300">
                        {isUndercut ? '-' : '+'}${row.absolute_difference.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 font-mono font-bold">
                        <span className={isUndercut ? 'text-rose-400' : 'text-emerald-400'}>
                          {row.percentage_difference > 0 ? `+${row.percentage_difference.toFixed(1)}%` : `${row.percentage_difference.toFixed(1)}%`}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        {isUndercut ? (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                            Undercutting
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                            You are cheaper
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {comparisonData && comparisonData.total > limit && (
          <div className="px-6 py-4 border-t border-slate-800/80 bg-slate-950/40 flex items-center justify-between">
            <span className="text-xs text-slate-400">
              Showing <span className="font-semibold text-slate-200">{page * limit + 1}</span> to{' '}
              <span className="font-semibold text-slate-200">{Math.min((page + 1) * limit, comparisonData.total)}</span> of{' '}
              <span className="font-semibold text-slate-200">{comparisonData.total}</span> comparisons
            </span>

            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 transition-colors"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-xs text-slate-400 px-2">Page {page + 1}</span>
              <button
                disabled={(page + 1) * limit >= comparisonData.total}
                onClick={() => setPage((p) => p + 1)}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 transition-colors"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
