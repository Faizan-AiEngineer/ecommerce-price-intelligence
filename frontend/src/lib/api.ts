import {
  AlertItem,
  CompetitorComparisonResponse,
  DashboardSummary,
  JobItem,
  PriceHistoryPoint,
  ProductDetail,
  ProductItem,
  RetailerItem,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const errorBody = await res.text().catch(() => '');
    throw new Error(`API error ${res.status}: ${errorBody || res.statusText}`);
  }
  return res.json();
}

export const api = {
  getDashboardSummary(): Promise<DashboardSummary> {
    return fetchJson<DashboardSummary>(`${API_BASE_URL}/dashboard/summary`);
  },

  getProducts(params?: {
    q?: string;
    category?: string;
    brand?: string;
    retailer?: string;
    stock?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ items: ProductItem[]; total: number; limit: number; offset: number }> {
    const query = new URLSearchParams();
    if (params?.q) query.set('q', params.q);
    if (params?.category) query.set('category', params.category);
    if (params?.brand) query.set('brand', params.brand);
    if (params?.retailer) query.set('retailer', params.retailer);
    if (params?.stock) query.set('stock', params.stock);
    if (params?.limit) query.set('limit', String(params.limit));
    if (params?.offset) query.set('offset', String(params.offset));

    const qs = query.toString();
    return fetchJson(`${API_BASE_URL}/products${qs ? `?${qs}` : ''}`);
  },

  getProduct(id: number): Promise<ProductDetail> {
    return fetchJson<ProductDetail>(`${API_BASE_URL}/products/${id}`);
  },

  getPriceHistory(productId: number): Promise<{ product_id: number; history: PriceHistoryPoint[] }> {
    return fetchJson(`${API_BASE_URL}/products/${productId}/price-history`);
  },

  getRetailers(): Promise<{ items: RetailerItem[] }> {
    return fetchJson(`${API_BASE_URL}/retailers`);
  },

  getCompetitorComparison(
    referenceRetailerId: number,
    category?: string,
    limit: number = 50,
    offset: number = 0,
  ): Promise<CompetitorComparisonResponse> {
    const query = new URLSearchParams({
      reference_retailer: String(referenceRetailerId),
      limit: String(limit),
      offset: String(offset),
    });
    if (category) query.set('category', category);

    return fetchJson<CompetitorComparisonResponse>(`${API_BASE_URL}/competitors/comparison?${query.toString()}`);
  },

  getAlerts(params?: { status?: string; alert_type?: string }): Promise<{ items: AlertItem[]; total: number }> {
    const query = new URLSearchParams();
    if (params?.status) query.set('status', params.status);
    if (params?.alert_type) query.set('alert_type', params.alert_type);

    const qs = query.toString();
    return fetchJson(`${API_BASE_URL}/alerts${qs ? `?${qs}` : ''}`);
  },

  acknowledgeAlert(alertId: number, status: 'acknowledged' | 'resolved' = 'acknowledged'): Promise<{ id: number; status: string }> {
    return fetchJson(`${API_BASE_URL}/alerts/${alertId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
  },

  getJobs(): Promise<{ items: JobItem[] }> {
    return fetchJson(`${API_BASE_URL}/jobs`);
  },

  triggerJob(): Promise<JobItem> {
    return fetchJson(`${API_BASE_URL}/jobs/trigger`, {
      method: 'POST',
    });
  },

  getSettings(): Promise<Record<string, any>> {
    return fetchJson(`${API_BASE_URL}/settings`);
  },

  updateSettings(data: Record<string, any>): Promise<any> {
    return fetchJson(`${API_BASE_URL}/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  getExportUrl(format: 'csv' | 'xlsx', category?: string): string {
    const params = new URLSearchParams({ file_format: format });
    if (category) params.set('category', category);
    return `${API_BASE_URL}/reports/export?${params.toString()}`;
  },
};
