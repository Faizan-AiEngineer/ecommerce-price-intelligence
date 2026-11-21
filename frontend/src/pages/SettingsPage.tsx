import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Settings,
  Download,
  FileSpreadsheet,
  FileText,
  Save,
  Check,
  Shield,
  Clock,
  DollarSign,
} from 'lucide-react';
import { api } from '../lib/api';

export const SettingsPage: React.FC = () => {
  const [dropThreshold, setDropThreshold] = useState<number>(5.0);
  const [increaseThreshold, setIncreaseThreshold] = useState<number>(5.0);
  const [intervalMinutes, setIntervalMinutes] = useState<number>(60);
  const [baseCurrency, setBaseCurrency] = useState<string>('USD');
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  const { data: currentSettings } = useQuery({
    queryKey: ['app-settings'],
    queryFn: () => api.getSettings(),
  });

  useEffect(() => {
    if (currentSettings) {
      if (currentSettings.alert_price_drop_threshold_pct) {
        setDropThreshold(currentSettings.alert_price_drop_threshold_pct);
      }
      if (currentSettings.alert_price_increase_threshold_pct) {
        setIncreaseThreshold(currentSettings.alert_price_increase_threshold_pct);
      }
      if (currentSettings.collection_interval_minutes) {
        setIntervalMinutes(currentSettings.collection_interval_minutes);
      }
      if (currentSettings.base_currency) {
        setBaseCurrency(currentSettings.base_currency);
      }
    }
  }, [currentSettings]);

  const saveMutation = useMutation({
    mutationFn: () =>
      api.updateSettings({
        alert_price_drop_threshold_pct: dropThreshold,
        alert_price_increase_threshold_pct: increaseThreshold,
        collection_interval_minutes: intervalMinutes,
        base_currency: baseCurrency,
      }),
    onSuccess: () => {
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    },
  });

  const handleExport = (format: 'csv' | 'xlsx') => {
    window.location.href = api.getExportUrl(format);
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-100">System Configuration & Data Export</h2>
        <p className="text-sm text-slate-400 mt-1">Configure automated alert thresholds, scheduler intervals, and export clean datasets</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Settings */}
        <div className="lg:col-span-2 space-y-6">
          {/* Alert Thresholds Card */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20 space-y-6">
            <div className="flex items-center gap-3 border-b border-slate-800/80 pb-4">
              <div className="rounded-xl bg-rose-500/10 p-2 text-rose-400 border border-rose-500/20">
                <Shield className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-slate-100">Alert Sensitivity Thresholds</h3>
                <p className="text-xs text-slate-400">Specify percentage deviation to trigger automated alerts</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300">Price Drop Alert Threshold (%)</label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    step="0.5"
                    min="1"
                    max="50"
                    value={dropThreshold}
                    onChange={(e) => setDropThreshold(parseFloat(e.target.value) || 0)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-semibold focus:outline-none focus:border-sky-500"
                  />
                  <span className="text-sm text-slate-400 font-medium">%</span>
                </div>
                <p className="text-[11px] text-slate-500">Triggers when competitor price decreases by this percentage</p>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300">Price Increase Alert Threshold (%)</label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    step="0.5"
                    min="1"
                    max="50"
                    value={increaseThreshold}
                    onChange={(e) => setIncreaseThreshold(parseFloat(e.target.value) || 0)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-semibold focus:outline-none focus:border-sky-500"
                  />
                  <span className="text-sm text-slate-400 font-medium">%</span>
                </div>
                <p className="text-[11px] text-slate-500">Triggers when seller increases price by this percentage</p>
              </div>
            </div>
          </div>

          {/* Collection Scheduler Card */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20 space-y-6">
            <div className="flex items-center gap-3 border-b border-slate-800/80 pb-4">
              <div className="rounded-xl bg-sky-500/10 p-2 text-sky-400 border border-sky-500/20">
                <Clock className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-slate-100">Scheduler & Currency</h3>
                <p className="text-xs text-slate-400">Configure harvest cadences and base reporting currency</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300">Collection Cadence</label>
                <select
                  value={intervalMinutes}
                  onChange={(e) => setIntervalMinutes(parseInt(e.target.value, 10))}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-medium focus:outline-none focus:border-sky-500"
                >
                  <option value={15}>Every 15 Minutes</option>
                  <option value={30}>Every 30 Minutes</option>
                  <option value={60}>Every 1 Hour (Standard)</option>
                  <option value={360}>Every 6 Hours</option>
                  <option value={1440}>Every 24 Hours</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300">Base Currency</label>
                <select
                  value={baseCurrency}
                  onChange={(e) => setBaseCurrency(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-medium focus:outline-none focus:border-sky-500"
                >
                  <option value="USD">USD ($ - United States Dollar)</option>
                  <option value="EUR">EUR (€ - Euro)</option>
                  <option value="GBP">GBP (£ - British Pound)</option>
                </select>
              </div>
            </div>

            <div className="pt-2 flex items-center justify-between">
              {savedSuccess ? (
                <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
                  <Check className="h-4 w-4" />
                  <span>Configuration saved successfully!</span>
                </div>
              ) : (
                <div />
              )}

              <button
                onClick={() => saveMutation.mutate()}
                disabled={saveMutation.isPending}
                className="px-5 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 disabled:opacity-50 text-slate-950 font-bold text-xs flex items-center gap-2 transition-all shadow-md shadow-sky-500/20"
              >
                <Save className="h-3.5 w-3.5" />
                <span>{saveMutation.isPending ? 'Saving...' : 'Save Settings'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right Col: Analytical Export Hub */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20 space-y-6">
            <div className="flex items-center gap-3 border-b border-slate-800/80 pb-4">
              <div className="rounded-xl bg-emerald-500/10 p-2 text-emerald-400 border border-emerald-500/20">
                <Download className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-slate-100">Export Intelligence Data</h3>
                <p className="text-xs text-slate-400">Download formatted reports</p>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Export complete structured datasets containing current prices, retailer stock levels, catalog SKUs, and cross-seller comparisons.
            </p>

            <div className="space-y-3">
              <button
                onClick={() => handleExport('csv')}
                className="w-full p-3.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 flex items-center justify-between text-left transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <FileText className="h-5 w-5 text-sky-400" />
                  <div>
                    <h4 className="text-xs font-bold text-slate-200">Export CSV Format</h4>
                    <p className="text-[11px] text-slate-500">Universal comma-separated format</p>
                  </div>
                </div>
                <Download className="h-4 w-4 text-slate-500 group-hover:text-slate-300 transition-colors" />
              </button>

              <button
                onClick={() => handleExport('xlsx')}
                className="w-full p-3.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 flex items-center justify-between text-left transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="h-5 w-5 text-emerald-400" />
                  <div>
                    <h4 className="text-xs font-bold text-slate-200">Export Microsoft Excel (.xlsx)</h4>
                    <p className="text-[11px] text-slate-500">Structured multi-column workbook</p>
                  </div>
                </div>
                <Download className="h-4 w-4 text-slate-500 group-hover:text-slate-300 transition-colors" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
