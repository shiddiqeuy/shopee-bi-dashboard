"use client";

import { useState } from "react";
import { Filter, Calendar, MapPin, Tag, CheckCircle2, RotateCcw } from "lucide-react";

interface FilterBarProps {
  onFilterChange: (filters: {
    dateRange: string;
    province: string;
    category: string;
    status: string;
  }) => void;
}

export function FilterBar({ onFilterChange }: FilterBarProps) {
  const [dateRange, setDateRange] = useState("Jan 2026 - Jul 2026");
  const [province, setProvince] = useState("All");
  const [category, setCategory] = useState("All");
  const [status, setStatus] = useState("All");

  const handleApply = (newValues: { dateRange?: string; province?: string; category?: string; status?: string }) => {
    const updated = {
      dateRange: newValues.dateRange !== undefined ? newValues.dateRange : dateRange,
      province: newValues.province !== undefined ? newValues.province : province,
      category: newValues.category !== undefined ? newValues.category : category,
      status: newValues.status !== undefined ? newValues.status : status,
    };
    if (newValues.dateRange !== undefined) setDateRange(newValues.dateRange);
    if (newValues.province !== undefined) setProvince(newValues.province);
    if (newValues.category !== undefined) setCategory(newValues.category);
    if (newValues.status !== undefined) setStatus(newValues.status);

    onFilterChange(updated);
  };

  const handleReset = () => {
    setDateRange("Jan 2026 - Jul 2026");
    setProvince("All");
    setCategory("All");
    setStatus("All");
    onFilterChange({
      dateRange: "Jan 2026 - Jul 2026",
      province: "All",
      category: "All",
      status: "All",
    });
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6 shadow-sm">
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-gray-100">
        <div className="flex items-center gap-2 text-gray-800 font-semibold text-sm">
          <Filter className="w-4 h-4 text-blue-600" />
          <span>Global Dashboard Filters</span>
        </div>
        <button
          onClick={handleReset}
          className="flex items-center gap-1 text-xs text-gray-500 hover:text-blue-600 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset Filters
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Date Range */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1 flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-gray-400" />
            Date Range
          </label>
          <select
            value={dateRange}
            onChange={(e) => handleApply({ dateRange: e.target.value })}
            className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="Jan 2026 - Jul 2026">Jan 2026 - Jul 2026 (Default)</option>
            <option value="Q1 2026">Q1 2026 (Jan - Mar)</option>
            <option value="Q2 2026">Q2 2026 (Apr - Jun)</option>
            <option value="Jul 2026">Jul 2026 (Current Month)</option>
            <option value="All Time">All Time</option>
          </select>
        </div>

        {/* Province / Region */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1 flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-gray-400" />
            Province / Region
          </label>
          <select
            value={province}
            onChange={(e) => handleApply({ province: e.target.value })}
            className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="All">All Provinces</option>
            <option value="DKI Jakarta">DKI Jakarta</option>
            <option value="Jawa Barat">Jawa Barat</option>
            <option value="Jawa Timur">Jawa Timur</option>
            <option value="Jawa Tengah">Jawa Tengah</option>
            <option value="Sumatera Utara">Sumatera Utara</option>
            <option value="Banten">Banten</option>
          </select>
        </div>

        {/* Product Category */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1 flex items-center gap-1">
            <Tag className="w-3.5 h-3.5 text-gray-400" />
            Product Category
          </label>
          <select
            value={category}
            onChange={(e) => handleApply({ category: e.target.value })}
            className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="All">All Categories</option>
            <option value="Horeca & Beverage">Horeca & Beverage Ingredients</option>
            <option value="Dairy & Creamer">Dairy & Creamer</option>
            <option value="Syrups & Sweeteners">Syrups & Sweeteners</option>
            <option value="Packaging & Supp">Packaging & Supplies</option>
          </select>
        </div>

        {/* Order Status */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-gray-400" />
            Order Status
          </label>
          <select
            value={status}
            onChange={(e) => handleApply({ status: e.target.value })}
            className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="All">All Statuses (Completed & Active)</option>
            <option value="Completed">Completed / Selesai</option>
            <option value="Processing">Processing / Dikemas</option>
            <option value="Cancelled">Cancelled / Dibatalkan</option>
          </select>
        </div>
      </div>
    </div>
  );
}
