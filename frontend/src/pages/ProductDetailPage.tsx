import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeft,
  ExternalLink,
  ShieldCheck,
  Tag,
  Store,
  Calendar,
  Layers,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { api } from '../lib/api';
import { StatusBadge } from '../components/StatusBadge';

export const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const productId = parseInt(id || '1', 10);

  const { data: product, isLoading: productLoading } = useQuery({
    queryKey: ['product-detail', productId],
    queryFn: () => api.getProduct(productId),
  });

  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['product-history', productId],
    queryFn: () => api.getPriceHistory(productId),
  });

  if (productLoading) {
    return (
      <div className="p-8 max-w-7xl mx-auto space-y-6">
        <div className="h-6 w-32 bg-slate-800 rounded animate-pulse" />
        <div className="h-48 bg-slate-900 rounded-2xl border border-slate-800 animate-pulse" />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <p className="text-slate-400">Product not found.</p>
        <Link to="/products" className="text-sky-400 mt-2 inline-block">
          &larr; Back to Products
        </Link>
      </div>
    );
  }

  // Group historical data by date and retailer
  const chartPointsMap: Record<string, any> = {};
  const retailersSet = new Set<string>();

  if (historyData?.history) {
    historyData.history.forEach((pt) => {
      const dateKey = pt.observed_at.split('T')[0];
      if (!chartPointsMap[dateKey]) {
        chartPointsMap[dateKey] = { date: dateKey };
      }
      chartPointsMap[dateKey][pt.retailer_name] = pt.observed_price;
      retailersSet.add(pt.retailer_name);
    });
  }

  const chartData = Object.values(chartPointsMap).sort((a, b) => a.date.localeCompare(b.date));
  const retailersList = Array.from(retailersSet);
  const colors = ['#38bdf8', '#34d399', '#f43f5e', '#fbbf24', '#a855f7'];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Back button */}
      <div>
        <Link
          to="/products"
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Product Explorer</span>
        </Link>
      </div>

      {/* Main Product Card */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-8 shadow-xl shadow-slate-950/20">
        <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-sky-500/10 text-sky-400 border border-sky-500/20">
                {product.brand}
              </span>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                {product.category}
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">{product.canonical_name}</h1>
            <p className="text-sm text-slate-400 max-w-3xl leading-relaxed">{product.description}</p>
            <div className="flex flex-wrap gap-4 text-xs text-slate-400 pt-2">
              {product.model_number && (
                <div>
                  Model: <span className="text-slate-200 font-medium">{product.model_number}</span>
                </div>
              )}
              {product.gtin && (
                <div>
                  GTIN / Barcode: <span className="text-slate-200 font-medium">{product.gtin}</span>
                </div>
              )}
            </div>
          </div>

          {/* Pricing Highlight Pill */}
          <div className="rounded-2xl bg-slate-950/70 border border-slate-800 p-6 lg:min-w-64 text-right flex flex-col justify-between">
            <div className="text-xs text-slate-400 mb-1">Lowest Market Price</div>
            <div className="text-3xl font-black text-emerald-400">${product.lowest_price.toFixed(2)}</div>
            {product.cheapest_retailer && (
              <div className="text-xs text-slate-400 mt-2">
                Available at <span className="font-semibold text-slate-200">{product.cheapest_retailer}</span>
              </div>
            )}
            <div className="text-[11px] text-slate-500 mt-1">
              Max observed: ${product.highest_price.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Matched Retailer Offers Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 shadow-xl shadow-slate-950/20 overflow-hidden">
        <div className="p-6 border-b border-slate-800/80 flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold text-slate-100">Live Retailer Offers</h3>
            <p className="text-xs text-slate-400 mt-0.5">Matched seller offers across monitored storefronts</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800 text-slate-300">
            {product.offers.length} active offers
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/60 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="px-6 py-4">Retailer</th>
                <th className="px-6 py-4">Current Price</th>
                <th className="px-6 py-4">Stock Status</th>
                <th className="px-6 py-4">SKU / Reference</th>
                <th className="px-6 py-4">Last Checked</th>
                <th className="px-6 py-4 text-right">Storefront</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {product.offers.map((offer) => {
                const isBestPrice = offer.current_price === product.lowest_price;
                return (
                  <tr key={offer.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-100 flex items-center gap-2">
                        <span>{offer.retailer_name}</span>
                        {isBestPrice && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                            Best Deal
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-bold text-slate-100">
                      ${offer.current_price.toFixed(2)}{' '}
                      <span className="text-xs font-normal text-slate-400">{offer.currency}</span>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={offer.stock_status} type="stock" />
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400 font-mono">
                      {offer.retailer_sku || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {offer.last_checked_at
                        ? new Date(offer.last_checked_at).toLocaleString()
                        : 'Recently'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {offer.product_url ? (
                        <a
                          href={offer.product_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-xs font-semibold text-sky-400 hover:text-sky-300"
                        >
                          <span>Store Link</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      ) : (
                        <span className="text-xs text-slate-500">Internal</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Historical Price Chart */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-base font-semibold text-slate-100">Historical Price Trajectory</h3>
            <p className="text-xs text-slate-400 mt-0.5">Track price adjustments across competing retailers over time</p>
          </div>
          <span className="text-xs text-slate-400 flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5" />
            90-Day Observation Window
          </span>
        </div>

        {historyLoading ? (
          <div className="h-72 flex items-center justify-center text-slate-400">Loading historical observations...</div>
        ) : chartData.length > 0 ? (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
                <Legend wrapperStyle={{ paddingTop: '10px' }} />
                {retailersList.map((ret, idx) => (
                  <Line
                    key={ret}
                    type="monotone"
                    dataKey={ret}
                    stroke={colors[idx % colors.length]}
                    strokeWidth={2}
                    dot={false}
                    name={ret}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-48 flex items-center justify-center text-slate-500 text-sm">
            No historical price snapshots recorded yet for this product.
          </div>
        )}
      </div>
    </div>
  );
};
