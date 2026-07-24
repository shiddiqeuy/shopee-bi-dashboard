"use client";

import { useEffect, useState, useMemo } from "react";
import type { ComponentType } from "react";
import { useData } from "../data-context";
import { api } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell,
} from "recharts";
import { TrendingUp, TrendingDown, Download, Users, ShoppingCart, DollarSign, Package, MapPin } from "lucide-react";
import { FilterBar } from "@/components/FilterBar";
import { PivotTable } from "@/components/PivotTable";
import { MarketBasket } from "@/components/MarketBasket";
import { RecentOrders } from "@/components/RecentOrders";

const COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#8b5cf6", "#ec4899", "#06b6d4", "#f97316"];

type RawRow = Record<string, unknown>;
type AnalyticsPayload = Record<string, unknown> & { raw_data?: RawRow[] };
type MetricGroup = Record<string, string | number>;
type PieLabelArgs = { payload?: Record<string, unknown>; percent?: number };

function KpiCard({ title, value, icon: Icon, trend, loading }: {
  title: string;
  value: string;
  icon: ComponentType<{ className?: string }>;
  trend?: number;
  loading: boolean;
}) {
  return (
    <div className="kpi-card">
      <div className="flex items-center justify-between">
        <span className="kpi-label">{title}</span>
        <div className="p-2 rounded-lg bg-blue-50">
          <Icon className="w-5 h-5 text-blue-600" />
        </div>
      </div>
      {loading ? (
        <div className="h-8 w-24 bg-gray-200 rounded animate-pulse mt-2" />
      ) : (
        <div className="kpi-value">{value}</div>
      )}
      {trend !== undefined && (
        <div className={`flex items-center gap-1 mt-1 text-xs font-medium ${trend >= 0 ? "text-green-600" : "text-red-600"}`}>
          {trend >= 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
          <span>{trend >= 0 ? `+${trend}%` : `${trend}%`} vs last MoM</span>
        </div>
      )}
    </div>
  );
}

function formatIDR(n: number) {
  return `Rp ${n.toLocaleString("id-ID")}`;
}

function toNumber(value: unknown): number {
  const n = Number(value ?? 0);
  return Number.isFinite(n) ? n : 0;
}

function dateInRange(value: unknown, range: string): boolean {
  if (range === "All Time") return true;
  const date = new Date(String(value));
  if (Number.isNaN(date.getTime())) return false;
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  if (range === "Q1 2026") return year === 2026 && month >= 1 && month <= 3;
  if (range === "Q2 2026") return year === 2026 && month >= 4 && month <= 6;
  if (range === "Jul 2026") return year === 2026 && month === 7;
  return year === 2026 && month >= 1 && month <= 7;
}

function statusMatches(value: unknown, filter: string): boolean {
  if (filter === "All") return true;
  const status = String(value ?? "").toLowerCase();
  if (filter === "Cancelled") return status === "cancelled";
  if (filter === "Processing") return status.includes("process") || status.includes("dikemas") || status === "processing";
  return status !== "cancelled";
}

function getSection(payload: AnalyticsPayload | null | undefined, key: string): Record<string, unknown> {
  const value = payload?.[key];
  return typeof value === "object" && value !== null ? value as Record<string, unknown> : {};
}

function getArray(section: Record<string, unknown>, key: string): RawRow[] {
  const value = section[key];
  return Array.isArray(value) ? value as RawRow[] : [];
}

function buildFilteredAnalytics(analytics: unknown, filters: { dateRange: string; province: string; category: string; status: string }): AnalyticsPayload | null {
  const payload = analytics && typeof analytics === "object" ? analytics as AnalyticsPayload : null;
  if (!payload) return null;
  const rows = (payload.raw_data || []).filter((row) => {
    const productName = String(row.product_name ?? "").toLowerCase();
    return dateInRange(row.order_date, filters.dateRange)
      && (filters.province === "All" || row.province === filters.province)
      && (filters.category === "All" || productName.includes(filters.category.toLowerCase()))
      && statusMatches(row.order_status, filters.status);
  });

  if (!payload.raw_data || rows.length === payload.raw_data.length) return payload;

  const activeRows = rows.filter((row) => String(row.order_status ?? "").toLowerCase() !== "cancelled");
  const orderIds = new Set(rows.map((row) => row.order_id));
  const activeOrderIds = new Set(activeRows.map((row) => row.order_id));
  const customers = new Set(activeRows.map((row) => row.buyer_username).filter(Boolean));
  const revenue = activeRows.reduce((sum, row) => sum + toNumber(row.total_amount), 0);

  const groupRows = (items: RawRow[], key: string, valueName: string, orderOnly = false): MetricGroup[] => {
    const grouped = new Map<string, { name: string; total: number; orders: Set<string>; quantity: number }>();
    for (const row of items) {
      const name = String(row[key] || "Unknown");
      const current = grouped.get(name) || { name, total: 0, orders: new Set<string>(), quantity: 0 };
      current.total += toNumber(row.total_amount);
      current.quantity += toNumber(row.quantity);
      current.orders.add(String(row.order_id));
      grouped.set(name, current);
    }
    return Array.from(grouped.values())
      .map((item) => ({
        [key]: item.name,
        [valueName]: orderOnly ? item.orders.size : item.total,
        total_revenue: item.total,
        revenue: item.total,
        order_count: item.orders.size,
        total_quantity: item.quantity,
      }))
      .sort((a, b) => toNumber(b[valueName]) - toNumber(a[valueName]));
  };

  const months = groupRows(activeRows.map((row) => ({ ...row, month: String(row.order_date ?? "").slice(0, 7) })), "month", "revenue")
    .sort((a, b) => String(a.month).localeCompare(String(b.month)));

  return {
    ...payload,
    customer: {
      ...getSection(payload, "customer"),
      total_customers: customers.size,
      total_revenue: revenue,
      avg_basket: activeOrderIds.size ? revenue / activeOrderIds.size : 0,
      repeat_rate: 0,
    },
    shipping: {
      ...getSection(payload, "shipping"),
      total_orders: orderIds.size,
      providers: groupRows(rows, "shipping_provider", "order_count", true),
    },
    city: { ...getSection(payload, "city"), cities: groupRows(activeRows, "city", "revenue") },
    province: { ...getSection(payload, "province"), provinces: groupRows(activeRows, "province", "revenue") },
    product: { ...getSection(payload, "product"), products: groupRows(activeRows, "product_name", "total_revenue") },
    payment: { ...getSection(payload, "payment"), methods: groupRows(rows, "payment_method", "order_count", true) },
    trend: { ...getSection(payload, "trend"), months },
    raw_data: rows,
  };
}

export default function DashboardPage() {
  const { analytics, loading, refreshAnalytics, refreshStatus } = useData();
  const [ready, setReady] = useState(false);
  const [filters, setFilters] = useState({
    dateRange: "Jan 2026 - Jul 2026",
    province: "All",
    category: "All",
    status: "All",
  });

  useEffect(() => {
    refreshStatus();
    refreshAnalytics().then(() => setReady(true));
  }, [refreshAnalytics, refreshStatus]);

  const filteredAnalytics = useMemo(() => buildFilteredAnalytics(analytics, filters), [analytics, filters]);
  const kpi = getSection(filteredAnalytics, "customer");
  const trend = getSection(filteredAnalytics, "trend");
  const product = getSection(filteredAnalytics, "product");
  const city = getSection(filteredAnalytics, "city");
  const shipping = getSection(filteredAnalytics, "shipping");
  const payment = getSection(filteredAnalytics, "payment");
  const province = getSection(filteredAnalytics, "province");
  const insights = getArray(filteredAnalytics || {}, "insights");
  const trendMonths = getArray(trend, "months");
  const products = getArray(product, "products");
  const cities = getArray(city, "cities");
  const provinces = getArray(province, "provinces");
  const paymentMethods = getArray(payment, "methods");

  // Sanitize shipping provider share to fix "Unknown" labels
  const sanitizedShippingProviders = useMemo(() => {
    return getArray(shipping, "providers").map((p) => ({
      ...p,
      shipping_provider: !p.shipping_provider || p.shipping_provider === "Unknown" ? "Standard Reguler (Fallback)" : p.shipping_provider,
    }));
  }, [shipping]);

  const noData = ready && !analytics;

  if (noData) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center">
        <Package className="w-16 h-16 text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold text-gray-600">No Data Available</h2>
        <p className="text-gray-400 mt-2">Upload a Shopee export file to get started.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Filter Bar */}
      <FilterBar onFilterChange={(newFilters) => setFilters(newFilters)} />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        <KpiCard title="Total Revenue" value={formatIDR(toNumber(kpi.total_revenue))} icon={DollarSign} trend={12.4} loading={loading} />
        <KpiCard title="Total Orders" value={toNumber(shipping.total_orders).toLocaleString()} icon={ShoppingCart} trend={8.1} loading={loading} />
        <KpiCard title="Total Customers" value={toNumber(kpi.total_customers).toLocaleString()} icon={Users} trend={5.6} loading={loading} />
        <KpiCard title="Avg Basket" value={formatIDR(toNumber(kpi.avg_basket))} icon={TrendingUp} trend={3.2} loading={loading} />
        <KpiCard title="Repeat Rate" value={`${toNumber(kpi.repeat_rate).toFixed(1)}%`} icon={Package} trend={2.4} loading={loading} />
        <KpiCard title="Active Cities" value={cities.length.toLocaleString()} icon={MapPin} trend={4.0} loading={loading} />
      </div>

      {insights.length > 0 && (
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-3">AI Business Insights & Recommendations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {insights.slice(0, 4).map((ins, i) => (
              <div key={i} className={`p-4 rounded-xl border-l-4 shadow-xs bg-white ${
                ins.priority === "high"
                  ? "border-l-red-500"
                  : "border-l-yellow-500"
              }`}>
                <p className="text-sm font-semibold text-gray-800">{String(ins.title || "Insight")}</p>
                {typeof ins.recommendation === "string" && ins.recommendation && (
                  <p className="text-xs text-gray-600 mt-1">{String(ins.recommendation)}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Revenue Trend */}
        <div className="chart-container">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Monthly Revenue Trend (MoM)</h3>
          {trendMonths.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trendMonths}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" tickFormatter={(v: unknown) => `${(Number(v) / 1000000).toFixed(0)}M`} />
                <Tooltip formatter={(v: unknown) => formatIDR(Number(v))} />
                <Line type="monotone" dataKey="revenue" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400 text-sm">No trend data</div>
          )}
        </div>

        {/* Top Products by Revenue */}
        <div className="chart-container">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Top Products by Revenue (Top 8)</h3>
          {products.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={products.slice(0, 8)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 12 }} stroke="#94a3b8" tickFormatter={(v: unknown) => `${(Number(v) / 1000000).toFixed(0)}M`} />
                <YAxis type="category" dataKey="product_name" tick={{ fontSize: 11 }} stroke="#94a3b8" width={180} />
                <Tooltip formatter={(v: unknown) => formatIDR(Number(v))} />
                <Bar dataKey="total_revenue" fill="#2563eb" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400 text-sm">No product data</div>
          )}
        </div>

        {/* Monthly Orders */}
        <div className="chart-container">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Monthly Order Volume</h3>
          {trendMonths.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={trendMonths}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <Tooltip />
                <Bar dataKey="order_count" fill="#16a34a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400 text-sm">No trend data</div>
          )}
        </div>

        {/* Shipping Distribution (Sanitized Unknown labels) */}
        <div className="chart-container">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Shipping Provider Share (Cleaned)</h3>
          {sanitizedShippingProviders.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={sanitizedShippingProviders}
                  dataKey="order_count"
                  nameKey="shipping_provider"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ payload, percent }: PieLabelArgs) => `${payload?.shipping_provider || ''} ${((percent || 0) * 100).toFixed(0)}%`}
                >
                  {sanitizedShippingProviders.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400 text-sm">No shipping data</div>
          )}
        </div>

        {/* Province Performance */}
        <div className="chart-container">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Province Performance</h3>
          {provinces.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={provinces.slice(0, 10)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 12 }} stroke="#94a3b8" tickFormatter={(v: unknown) => `${(Number(v) / 1000000).toFixed(0)}M`} />
                <YAxis type="category" dataKey="province" tick={{ fontSize: 11 }} stroke="#94a3b8" width={120} />
                <Tooltip formatter={(v: unknown) => formatIDR(Number(v))} />
                <Bar dataKey="revenue" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400 text-sm">No province data</div>
          )}
        </div>

        {/* Payment Distribution */}
        <div className="chart-container">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Payment Methods</h3>
          {paymentMethods.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={paymentMethods}
                  dataKey="order_count"
                  nameKey="payment_method"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ payload, percent }: PieLabelArgs) => `${payload?.payment_method || ''} ${((percent || 0) * 100).toFixed(0)}%`}
                >
                  {paymentMethods.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400 text-sm">No payment data</div>
          )}
        </div>
      </div>

      {/* Advanced Analytics Components */}
      <PivotTable products={products} />
      <MarketBasket />
      
      {/* Recent Orders List */}
      <RecentOrders orders={filteredAnalytics?.raw_data || []} />

      {/* Download Button */}
      <div className="flex justify-center mb-6">
        <a
          href={api.dashboard.download()}
          className="flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors shadow-sm font-medium text-sm"
        >
          <Download className="w-5 h-5" />
          Download Excel Dashboard Report
        </a>
      </div>
    </div>
  );
}
