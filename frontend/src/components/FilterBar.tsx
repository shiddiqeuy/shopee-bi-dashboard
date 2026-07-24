"use client";

import { useState } from "react";
import { Filter, Calendar, MapPin, Tag, CheckCircle2, RotateCcw, X } from "lucide-react";

interface FilterBarProps {
  onFilterChange: (filters: {
    dateRange: string;
    province: string;
    category: string;
    status: string;
  }) => void;
}

export function FilterBar({ onFilterChange }: FilterBarProps) {
  // Main state (applied filters)
  const [dateRange, setDateRange] = useState("Jan 2026 - Jul 2026");
  const [province, setProvince] = useState("All");
  const [category, setCategory] = useState("All");
  const [status, setStatus] = useState("All");

  // Mobile drawer state
  const [isOpen, setIsOpen] = useState(false);
  
  // Temporary state for mobile batching
  const [tempDateRange, setTempDateRange] = useState(dateRange);
  const [tempProvince, setTempProvince] = useState(province);
  const [tempCategory, setTempCategory] = useState(category);
  const [tempStatus, setTempStatus] = useState(status);

  // Desktop live apply
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

  // Desktop reset
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

  // Mobile trigger
  const openDrawer = () => {
    setTempDateRange(dateRange);
    setTempProvince(province);
    setTempCategory(category);
    setTempStatus(status);
    setIsOpen(true);
  };

  // Mobile reset (resets both temp and main state, applies, and closes drawer)
  const resetMobileFilters = () => {
    const defaults = {
      dateRange: "Jan 2026 - Jul 2026",
      province: "All",
      category: "All",
      status: "All",
    };
    
    // Reset temp state
    setTempDateRange(defaults.dateRange);
    setTempProvince(defaults.province);
    setTempCategory(defaults.category);
    setTempStatus(defaults.status);
    
    // Reset main state
    setDateRange(defaults.dateRange);
    setProvince(defaults.province);
    setCategory(defaults.category);
    setStatus(defaults.status);
    
    // Apply immediately and close
    onFilterChange(defaults);
    setIsOpen(false);
  };

  // Mobile apply (syncs temp to main and fires callback)
  const applyMobileFilters = () => {
    setDateRange(tempDateRange);
    setProvince(tempProvince);
    setCategory(tempCategory);
    setStatus(tempStatus);
    onFilterChange({
      dateRange: tempDateRange,
      province: tempProvince,
      category: tempCategory,
      status: tempStatus,
    });
    setIsOpen(false);
  };

  return (
    <>
      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6 shadow-sm">
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-gray-100">
          <div className="flex items-center gap-2 text-gray-800 font-semibold text-sm">
            <Filter className="w-4 h-4 text-blue-600" />
            <span>Global Dashboard Filters</span>
          </div>
          
          {/* Desktop Reset Button */}
          <button
            onClick={handleReset}
            className="hidden md:flex items-center gap-1 text-xs text-gray-500 hover:text-blue-600 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset Filters
          </button>
          
          {/* Mobile Filter Trigger Button */}
          <button
            onClick={openDrawer}
            className="md:hidden flex items-center gap-1 text-xs text-blue-600 font-medium hover:text-blue-700 transition-colors bg-blue-50 px-3 py-1.5 rounded-md"
          >
            <Filter className="w-3.5 h-3.5" />
            Filter Data
          </button>
        </div>

        {/* Desktop View: Grid (hidden on mobile) */}
        <div className="hidden md:grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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

      {/* Mobile Drawer (Bottom Sheet) */}
      <div 
        className={`md:hidden fixed inset-0 z-[100] flex flex-col justify-end transition-all duration-300 ${
          isOpen ? "visible" : "invisible pointer-events-none"
        }`}
      >
        {/* Overlay */}
        <div 
          className={`absolute inset-0 bg-black/50 transition-opacity duration-300 ${
            isOpen ? "opacity-100" : "opacity-0"
          }`}
          onClick={() => setIsOpen(false)}
        />
        
        {/* Sheet Content */}
        <div 
          className={`relative bg-white w-full rounded-t-2xl shadow-2xl flex flex-col max-h-[85vh] transition-transform duration-300 ease-out ${
            isOpen ? "translate-y-0" : "translate-y-full"
          }`}
        >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                <Filter className="w-4 h-4 text-blue-600" />
                Filter Data
              </h3>
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1 text-gray-400 hover:text-gray-600 bg-gray-50 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Body (Scrollable) */}
            <div className="p-4 flex-1 overflow-y-auto space-y-5 pb-20">
              {/* Date Range */}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1 flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-gray-400" />
                  Date Range
                </label>
                <select
                  value={tempDateRange}
                  onChange={(e) => setTempDateRange(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                  value={tempProvince}
                  onChange={(e) => setTempProvince(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                  value={tempCategory}
                  onChange={(e) => setTempCategory(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                  value={tempStatus}
                  onChange={(e) => setTempStatus(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="All">All Statuses (Completed & Active)</option>
                  <option value="Completed">Completed / Selesai</option>
                  <option value="Processing">Processing / Dikemas</option>
                  <option value="Cancelled">Cancelled / Dibatalkan</option>
                </select>
              </div>
            </div>

            {/* Footer (Sticky) */}
            <div className="absolute bottom-0 w-full p-4 border-t border-gray-100 flex gap-3 bg-white rounded-b-2xl shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
              <button
                onClick={resetMobileFilters}
                className="flex-1 py-2.5 px-4 text-sm font-medium text-gray-700 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
              <button
                onClick={applyMobileFilters}
                className="flex-1 py-2.5 px-4 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
    </>
  );
}
