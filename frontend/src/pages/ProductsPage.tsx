import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Search, Filter, ChevronLeft, ChevronRight, Eye } from 'lucide-react';
import { api } from '../lib/api';
import { StatusBadge } from '../components/StatusBadge';

export const ProductsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedStock, setSelectedStock] = useState<string>('');
  const [page, setPage] = useState(0);
  const limit = 20;

  const { data, isLoading, error } = useQuery({
    queryKey: ['products-list', searchTerm, selectedCategory, selectedStock, page],
    queryFn: () =>
      api.getProducts({
        q: searchTerm || undefined,
        category: selectedCategory || undefined,
        stock: selectedStock || undefined,
        limit,
        offset: page * limit,
      }),
  });

  const categories = ['Laptops', 'Smartphones', 'Audio', 'Wearables', 'Home Office', 'Accessories'];

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100">Product Explorer</h2>
          <p className="text-sm text-slate-400 mt-1">Cross-store catalog matching, pricing disparities, and stock status</p>
        </div>
        <div className="text-xs text-slate-400">
          Total items: <span className="font-semibold text-sky-400">{data?.total ?? 0}</span>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-4 shadow-xl shadow-slate-950/20 flex flex-col md:flex-row gap-4 items-center justify-between">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search products, brands, models..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(0);
            }}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors"
          />
        </div>

        {/* Category & Stock Selectors */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-slate-400" />
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setPage(0);
              }}
              className="py-2 px-3 rounded-xl bg-slate-950/80 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <select
            value={selectedStock}
            onChange={(e) => {
              setSelectedStock(e.target.value);
              setPage(0);
            }}
            className="py-2 px-3 rounded-xl bg-slate-950/80 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
          >
            <option value="">All Inventory</option>
            <option value="in_stock">In Stock Only</option>
            <option value="out_of_stock">Out of Stock</option>
          </select>
        </div>
      </div>

      {/* Products Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/90 shadow-xl shadow-slate-950/20 overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400">Loading catalog offerings...</div>
        ) : error ? (
          <div className="p-12 text-center text-rose-400">Error loading catalog products</div>
        ) : !data?.items.length ? (
          <div className="p-12 text-center text-slate-400">No products match your search criteria.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950/60 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4">Product</th>
                  <th className="px-6 py-4">Brand</th>
                  <th className="px-6 py-4">Category</th>
                  <th className="px-6 py-4">Price Range</th>
                  <th className="px-6 py-4">Retailers</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {data.items.map((prod) => (
                  <tr key={prod.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-100">{prod.canonical_name}</div>
                      <div className="text-xs text-slate-400">{prod.model_number || prod.gtin || 'Standard SKU'}</div>
                    </td>
                    <td className="px-6 py-4 text-slate-300 font-medium">{prod.brand}</td>
                    <td className="px-6 py-4">
                      <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                        {prod.category}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-sky-400">${prod.min_price.toFixed(2)}</div>
                      {prod.max_price > prod.min_price && (
                        <div className="text-xs text-slate-400">up to ${prod.max_price.toFixed(2)}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-slate-300">{prod.offer_count} offers</td>
                    <td className="px-6 py-4">
                      <StatusBadge status={prod.stock_status} type="stock" />
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        to={`/products/${prod.id}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/30 text-xs font-semibold transition-colors"
                      >
                        <Eye className="h-3.5 w-3.5" />
                        <span>Inspect</span>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {data && data.total > limit && (
          <div className="px-6 py-4 border-t border-slate-800/80 bg-slate-950/40 flex items-center justify-between">
            <span className="text-xs text-slate-400">
              Showing <span className="font-semibold text-slate-200">{page * limit + 1}</span> to{' '}
              <span className="font-semibold text-slate-200">{Math.min((page + 1) * limit, data.total)}</span> of{' '}
              <span className="font-semibold text-slate-200">{data.total}</span> products
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
                disabled={(page + 1) * limit >= data.total}
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
