"use client";

import { useState } from "react";
import { Filter, Calendar, MapPin, Tag, CheckCircle2, RotateCcw, Check } from "lucide-react";

interface FilterValues {
  dateRange: string;
  province: string;
  category: string;
  status: string;
}

interface FilterBarProps {
  onFilterChange: (filters: FilterValues) => void;
}

const DEFAULT_FILTERS: FilterValues = {
  dateRange: "Jan 2026 - Jul 2026",
  province: "All",
  category: "All",
  status: "All",
};

export function FilterBar({ onFilterChange }: FilterBarProps) {
  // Draft selection: updated as the user picks values in the dropdowns.
  const [selected, setSelected] = useState<FilterValues>(DEFAULT_FILTERS);

  const updateSelected = (patch: Partial<FilterValues>) => {
    setSelected((prev) => ({ ...prev, ...patch }));
  };

  const handleApply = () => {
    onFilterChange(selected);
  };

  const handleReset = () => {
    setSelected(DEFAULT_FILTERS);
    onFilterChange(DEFAULT_FILTERS);
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6 shadow-sm">
      <div className="flex items-center gap-2 text-gray-800 font-semibold text-sm mb-3 pb-2 border-b border-gray-100">
        <Filter className="w-4 h-4 text-blue-600" />
        <span>Global Dashboard Filters</span>
      </div>

      {/* Row 1: filter fields */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Date Range */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1 flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-gray-400" />
            Date Range
          </label>
          <select
            value={selected.dateRange}
            onChange={(e) => updateSelected({ dateRange: e.target.value })}
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
            value={selected.province}
            onChange={(e) => updateSelected({ province: e.target.value })}
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
            value={selected.category}
            onChange={(e) => updateSelected({ category: e.target.value })}
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
            value={selected.status}
            onChange={(e) => updateSelected({ status: e.target.value })}
            className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="All">All Statuses (Completed & Active)</option>
            <option value="Completed">Completed / Selesai</option>
            <option value="Processing">Processing / Dikemas</option>
            <option value="Cancelled">Cancelled / Dibatalkan</option>
          </select>
        </div>
      </div>

      {/* Row 2: explicit actions — dropdown changes only update local selection above */}
      <div className="flex items-center justify-end gap-2 mt-4 pt-3 border-t border-gray-100">
        <button
          onClick={handleReset}
          className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-gray-600 hover:text-blue-600 border border-gray-300 rounded-lg hover:border-blue-300 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset Filters
        </button>
        <button
          onClick={handleApply}
          className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Check className="w-3.5 h-3.5" />
          Apply Filters
        </button>
      </div>
    </div>
  );
}
