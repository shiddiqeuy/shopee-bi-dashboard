"use client";

import { ShoppingBag, TrendingUp, Sparkles } from "lucide-react";

export function MarketBasket() {
  const bundles = [
    {
      itemA: "Krimer Non-Dairy 1kg (Horeca Pack)",
      itemB: "Gula Aren Semut Organik 1kg",
      category: "Beverage Raw Materials",
      support: "18.4%",
      confidence: "74.2%",
      lift: "3.24x",
      suggestion: "Create Shopee Horeca Starter Bundle Discount (Save Rp 5.000)",
      badge: "High Synergy",
    },
    {
      itemA: "Sirup Flavored Hazelnut 750ml",
      itemB: "Susu Evaporasi UHT 385g",
      category: "Cafe Supplies",
      support: "14.2%",
      confidence: "68.9%",
      lift: "2.85x",
      suggestion: "Cross-sell in checkout banner for Coffee Shop owners",
      badge: "Trending",
    },
    {
      itemA: "Kopi Robusta Lampung Ground 500g",
      itemB: "Paper Filter V60 100pcs",
      category: "Coffee & Accessories",
      support: "11.7%",
      confidence: "61.5%",
      lift: "2.41x",
      suggestion: "Bundle Barista Kit promotion during Shopee PayDay campaign",
      badge: "Recommended",
    },
  ];

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6 shadow-sm">
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
            <ShoppingBag className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-gray-800">Market Basket & Cross-Selling Insights</h2>
            <p className="text-xs text-gray-500">Association rule mining and product bundling recommendations for Horeca & Cafe clients.</p>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-purple-100 text-purple-700 font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          AI Association Engine
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {bundles.map((b, idx) => (
          <div key={idx} className="border border-gray-200 rounded-xl p-4 flex flex-col justify-between hover:border-purple-300 transition-colors bg-gradient-to-b from-white to-gray-50/50">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-50 text-purple-700">
                  {b.category}
                </span>
                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                  {b.badge}
                </span>
              </div>

              {/* Bundling Items */}
              <div className="space-y-2 mb-4 bg-white p-3 rounded-lg border border-gray-100">
                <div className="flex items-start gap-2 text-xs font-medium text-gray-800">
                  <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px] shrink-0 font-bold">1</span>
                  <span className="line-clamp-1">{b.itemA}</span>
                </div>
                <div className="flex items-center justify-center text-gray-400 my-0.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-purple-500 bg-purple-50 px-2 py-0.5 rounded-full">+ Bundled With</span>
                </div>
                <div className="flex items-start gap-2 text-xs font-medium text-gray-800">
                  <span className="w-4 h-4 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center text-[10px] shrink-0 font-bold">2</span>
                  <span className="line-clamp-1">{b.itemB}</span>
                </div>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-3 gap-2 mb-4 text-center">
                <div className="bg-gray-50 p-2 rounded-lg border border-gray-100">
                  <p className="text-[10px] text-gray-400 uppercase font-medium">Support</p>
                  <p className="text-xs font-bold text-gray-800 mt-0.5">{b.support}</p>
                </div>
                <div className="bg-gray-50 p-2 rounded-lg border border-gray-100">
                  <p className="text-[10px] text-gray-400 uppercase font-medium">Confidence</p>
                  <p className="text-xs font-bold text-green-600 mt-0.5">{b.confidence}</p>
                </div>
                <div className="bg-gray-50 p-2 rounded-lg border border-gray-100">
                  <p className="text-[10px] text-gray-400 uppercase font-medium">Lift Score</p>
                  <p className="text-xs font-bold text-blue-600 mt-0.5">{b.lift}</p>
                </div>
              </div>
            </div>

            {/* Suggested Action */}
            <div className="bg-purple-50/80 border border-purple-100 rounded-lg p-2.5 text-xs text-purple-900 flex items-start gap-2">
              <TrendingUp className="w-4 h-4 text-purple-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold block mb-0.5">Suggested Action:</span>
                <span>{b.suggestion}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
