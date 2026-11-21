export interface DashboardSummary {
  monitored_products: number;
  active_retailers: number;
  active_offers: number;
  average_product_price: number;
  recent_price_drops: number;
  out_of_stock_products: number;
  active_alerts: number;
  last_successful_collection: string | null;
  price_trends: Array<{
    date: string;
    avg_price: number;
    min_price: number;
    max_price: number;
  }>;
  category_distribution: Array<{
    category: string;
    product_count: number;
    avg_price: number;
  }>;
  retailer_summary: Array<{
    retailer: string;
    offer_count: number;
    avg_price: number;
  }>;
}

export interface RetailerOffer {
  id: number;
  retailer_id: number;
  retailer_name: string;
  retailer_website?: string;
  retailer_sku?: string;
  product_url?: string;
  current_price: number;
  currency: string;
  stock_status: string;
  last_checked_at: string | null;
}

export interface ProductItem {
  id: number;
  canonical_name: string;
  brand: string;
  category: string;
  model_number?: string;
  gtin?: string;
  description?: string;
  min_price: number;
  max_price: number;
  avg_price: number;
  offer_count: number;
  stock_status: string;
  offers: RetailerOffer[];
  created_at: string | null;
  updated_at: string | null;
}

export interface ProductDetail extends ProductItem {
  lowest_price: number;
  highest_price: number;
  cheapest_retailer?: string;
}

export interface PriceHistoryPoint {
  id: number;
  retailer_product_id: number;
  retailer_id: number;
  retailer_name: string;
  observed_price: number;
  original_price: number | null;
  stock_status: string;
  observed_at: string;
}

export interface CompetitorComparisonItem {
  product_id: number;
  product_name: string;
  category: string;
  brand: string;
  reference_retailer: string;
  reference_price: number;
  reference_stock: string;
  competitor_retailer: string;
  competitor_price: number;
  competitor_stock: string;
  absolute_difference: number;
  percentage_difference: number;
  cheaper_competitor: boolean;
}

export interface CompetitorComparisonResponse {
  reference_retailer: string | null;
  items: CompetitorComparisonItem[];
  total: number;
  limit: number;
  offset: number;
  summary: {
    total_comparisons: number;
    competitor_cheaper_count: number;
    reference_cheaper_count: number;
    same_price_count: number;
  };
}

export interface AlertItem {
  id: number;
  product_id: number;
  product_name: string;
  category?: string;
  retailer_product_id?: number;
  retailer_name?: string;
  alert_type: string;
  message: string;
  previous_value: number | null;
  current_value: number | null;
  threshold: number | null;
  status: 'active' | 'acknowledged' | 'resolved';
  created_at: string;
}

export interface JobItem {
  id: number;
  source_id?: number;
  source_name: string;
  started_at: string | null;
  finished_at: string | null;
  duration_seconds: number | null;
  status: 'queued' | 'running' | 'completed' | 'failed';
  records_extracted: number;
  records_loaded: number;
  error_count: number;
  error_message?: string;
}

export interface RetailerItem {
  id: number;
  name: string;
  website: string;
  currency: string;
  country: string;
  active: boolean;
  offer_count: number;
  avg_price: number;
  min_price: number;
  max_price: number;
  created_at: string | null;
}
