"use client";

import { useEffect, useState } from "react";
import { useData } from "../data-context";
import { api } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell,
} from "recharts";
import { TrendingUp, TrendingDown, Download, Users, ShoppingCart, DollarSign, Package, MapPin, Truck } from "lucide-react";

const COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#8b5cf6", "#ec4899", "#06b6d4", "#f97316"];

function KpiCard({ title, value, icon: Icon, trend, loading }: any) {
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
        <div className={`flex items-center gap-1 mt-1 text-xs ${trend >= 0 ? "text-green-600" : "text-red-600"}`}>
          {trend >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
          <span>{Math.abs(trend)}% vs last period</span>
        </div>
      )}
    </div>
  );
}

function formatIDR(n: number) {
  return `Rp ${n.toLocaleString("id-ID")}`;
}

export default function DashboardPage() {
  const { analytics, loading, refreshAnalytics, refreshStatus } = useData();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    refreshStatus();
    refreshAnalytics().then(() => setReady(true));
  }, []);

  const kpi = analytics?.customer;
  const trend = analytics?.trend;
  const product = analytics?.product;
  const city = analytics?.city;
  const shipping = analytics?.shipping;
  const payment = analytics?.payment;
  const province = analytics?.province;
  const insights = analytics?.insights || [];

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
      <div className="flex items-center justify-between mb-6">
        <h1 className="page-header mb-0">Dashboard</h1>
        <button
          onClick={refreshAnalytics}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        <KpiCard title="Total Revenue" value={kpi ? formatIDR(kpi.total_revenue) : "—"} icon={DollarSign} loading={loading} />
        <KpiCard title="Total Orders" value={shipping ? shipping.total_orders.toLocaleString() : "—"} icon={ShoppingCart} loading={loading} />
        <KpiCard title="Total Customers" value={kpi ? kpi.total_customers.toLocaleString() : "—"} icon={Users} loading={loading} />
        <KpiCard title="Avg Basket" value={kpi ? formatIDR(kpi.avg_basket) : "—"} icon={TrendingUp} loading={loading} />
        <KpiCard title="Repeat Rate" value={kpi ? `${kpi.repeat_rate.toFixed(1)}%` : "—"} icon={Package} loading={loading} />
        <KpiCard title="Cities" value={city ? city.cities.length.toLocaleString() : "—"} icon={MapPin} loading={loading} />
      </div>

      {insights.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {insights.slice(0, 4).map((ins: any, i: number) => (
              <div key={i} className={`p-4 rounded-lg border-l-4 ${
                ins.priority === "high"
                  ? "border-l-red-500 bg-red-50"
                  : "border-l-yellow-500 bg-yellow-50"
              }`}>
                <p className="text-sm font-medium text-gray-800">{ins.title}</p>
                {ins.recommendation && (
                  <p className="text-xs text-gray-500 mt-1">{ins.recommendation}</p>
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
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Monthly Revenue Trend</h3>
          {trend?.months && trend.months.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trend.months}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" tickFormatter={(v: any) => `${(Number(v) / 1000000).toFixed(0)}M`} />
                <Tooltip formatter={(v: any) => formatIDR(Number(v))} />
                <Line type="monotone" dataKey="revenue" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400 text-sm">No trend data</div>
          )}
        </div>

        {/* Top Products */}
        <div className="chart-container">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Top Products by Revenue</h3>
          {product?.products && product.products.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={product.products.slice(0, 8)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 12 }} stroke="#94a3b8" tickFormatter={(v: any) => `${(Number(v) / 1000000).toFixed(0)}M`} />
                <YAxis type="category" dataKey="product_name" tick={{ fontSize: 11 }} stroke="#94a3b8" width={140} />
                <Tooltip formatter={(v: any) => formatIDR(Number(v))} />
                <Bar dataKey="total_revenue" fill="#2563eb" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-gray-400 text-sm">No product data</div>
          )}
        </div>

        {/* Monthly Orders */}
        <div className="chart-container">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Monthly Orders</h3>
          {trend?.months && trend.months.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={trend.months}>
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

        {/* Shipping Distribution */}
        <div className="chart-container">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Shipping Provider Share</h3>
          {shipping?.providers && shipping.providers.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={shipping.providers}
                  dataKey="order_count"
                  nameKey="shipping_provider"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ payload, percent }: any) => `${payload?.shipping_provider || ''} ${((percent || 0) * 100).toFixed(0)}%`}
                >
                  {shipping.providers.map((_: any, i: number) => (
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
          {province?.provinces && province.provinces.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={province.provinces.slice(0, 10)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 12 }} stroke="#94a3b8" tickFormatter={(v: any) => `${(Number(v) / 1000000).toFixed(0)}M`} />
                <YAxis type="category" dataKey="province" tick={{ fontSize: 11 }} stroke="#94a3b8" width={120} />
                <Tooltip formatter={(v: any) => formatIDR(Number(v))} />
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
          {payment?.methods && payment.methods.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={payment.methods}
                  dataKey="order_count"
                  nameKey="payment_method"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ payload, percent }: any) => `${payload?.payment_method || ''} ${((percent || 0) * 100).toFixed(0)}%`}
                >
                  {payment.methods.map((_: any, i: number) => (
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

      {/* Download Button */}
      <div className="flex justify-center mb-6">
        <a
          href={api.dashboard.download()}
          className="flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
        >
          <Download className="w-5 h-5" />
          Download Excel Dashboard
        </a>
      </div>
    </div>
  );
}
