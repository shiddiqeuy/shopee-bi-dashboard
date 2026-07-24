import { Package, Clock, CheckCircle, XCircle } from "lucide-react";

type RawRow = Record<string, unknown>;

interface RecentOrdersProps {
  orders: RawRow[];
}

const RECENT_ORDERS_LIMIT = 50;

function formatIDR(n: number) {
  return `Rp ${n.toLocaleString("id-ID")}`;
}

function getStatusColor(status: string) {
  const s = status.toLowerCase();
  if (s === "selesai" || s === "completed") return "bg-green-100 text-green-700 border-green-200";
  if (s.includes("batal") || s === "cancelled") return "bg-red-100 text-red-700 border-red-200";
  if (s.includes("process") || s.includes("dikemas") || s === "processing") return "bg-blue-100 text-blue-700 border-blue-200";
  return "bg-gray-100 text-gray-700 border-gray-200";
}

function getStatusIcon(status: string) {
  const s = status.toLowerCase();
  if (s === "selesai" || s === "completed") return <CheckCircle className="w-4 h-4 mr-1" />;
  if (s.includes("batal") || s === "cancelled") return <XCircle className="w-4 h-4 mr-1" />;
  if (s.includes("process") || s.includes("dikemas") || s === "processing") return <Clock className="w-4 h-4 mr-1" />;
  return <Package className="w-4 h-4 mr-1" />;
}

export function RecentOrders({ orders }: RecentOrdersProps) {
  const recentOrders = [...orders]
    .sort((a, b) => {
      // Replace space with 'T' to ensure cross-browser parsing of "YYYY-MM-DD HH:MM:SS"
      const dateA = new Date(String(a.order_date || "").replace(" ", "T")).getTime() || 0;
      const dateB = new Date(String(b.order_date || "").replace(" ", "T")).getTime() || 0;
      return dateB - dateA;
    })
    .slice(0, RECENT_ORDERS_LIMIT);

  if (recentOrders.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center text-gray-500">
        No recent orders available.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-gray-900">Recent Orders</h2>
        <span className="text-sm text-gray-500">Showing {recentOrders.length} latest</span>
      </div>

      {/* Mobile View: Cards (< md) */}
      <div className="flex flex-col gap-4 md:hidden">
        {recentOrders.map((order, i) => (
          <div key={String(order.order_id || i)} className="p-4 rounded-lg border border-gray-100 bg-gray-50 shadow-sm flex flex-col gap-3">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-semibold text-gray-900">#{String(order.order_id || "N/A")}</p>
                <p className="text-xs text-gray-500">{String(order.order_date || "-").split(' ')[0]}</p>
              </div>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(String(order.order_status || ""))}`}>
                {getStatusIcon(String(order.order_status || ""))}
                {String(order.order_status || "Unknown")}
              </span>
            </div>
            
            <div>
              <p className="text-sm text-gray-800 line-clamp-2">{String(order.product_name || "Unknown Product")}</p>
              <p className="text-xs text-gray-500 mt-1">Customer: {String(order.buyer_username || "-")}</p>
            </div>
            
            <div className="flex justify-between items-end mt-1 pt-3 border-t border-gray-200">
              <span className="text-xs text-gray-500">Qty: {String(order.quantity || "0")}</span>
              <span className="text-sm font-bold text-gray-900">{formatIDR(Number(order.total_amount || 0))}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Tablet & Desktop View: Table (>= md) */}
      <div className="hidden md:block overflow-x-auto w-full">
        {/* min-w-[800px] ensures the table will overflow and cause horizontal scrolling on smaller tablets */}
        <table className="w-full min-w-[800px] text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Order ID</th>
              <th className="py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Date</th>
              <th className="py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Customer</th>
              <th className="py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Product</th>
              <th className="py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Amount</th>
              <th className="py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {recentOrders.map((order, i) => (
              <tr key={String(order.order_id || i)} className="hover:bg-gray-50 transition-colors">
                <td className="py-3 px-4 text-sm font-medium text-gray-900 whitespace-nowrap">#{String(order.order_id || "N/A")}</td>
                <td className="py-3 px-4 text-sm text-gray-500 whitespace-nowrap">{String(order.order_date || "-").split(' ')[0]}</td>
                <td className="py-3 px-4 text-sm text-gray-600 whitespace-nowrap">{String(order.buyer_username || "-")}</td>
                <td className="py-3 px-4 text-sm text-gray-800">
                  <div className="max-w-xs truncate">{String(order.product_name || "Unknown Product")}</div>
                </td>
                <td className="py-3 px-4 text-sm font-bold text-gray-900 text-right whitespace-nowrap">
                  {formatIDR(Number(order.total_amount || 0))}
                </td>
                <td className="py-3 px-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(String(order.order_status || ""))}`}>
                    {getStatusIcon(String(order.order_status || ""))}
                    {String(order.order_status || "Unknown")}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
