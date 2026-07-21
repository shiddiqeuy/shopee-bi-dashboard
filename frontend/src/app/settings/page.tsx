"use client";

import { useEffect, useState } from "react";
import { api, ETLStatus } from "@/lib/api";
import { Database, FileText, Trash2 } from "lucide-react";

export default function SettingsPage() {
  const [status, setStatus] = useState<ETLStatus | null>(null);
  const [files, setFiles] = useState<any[]>([]);

  useEffect(() => {
    api.etl.status().then(setStatus).catch(() => {});
    api.files.list().then((d) => setFiles(d.files)).catch(() => {});
  }, []);

  async function handleResetWarehouse() {
    // Clear files and data - this removes input files and rebuilds from scratch
    if (!confirm("Clear all data? This will delete all uploaded files.")) return;
    await api.files.clear();
    setFiles([]);
    setStatus(null);
  }

  return (
    <div>
      <h1 className="page-header">Settings</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* System Info */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Database className="w-5 h-5 text-blue-600" />
            <h2 className="font-semibold text-gray-800">System Info</h2>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Data Available</span>
              <span className={status?.data_available ? "text-green-600 font-medium" : "text-gray-400"}>
                {status?.data_available ? "Yes" : "No"}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Total Rows</span>
              <span className="text-gray-800 font-medium">{status?.total_rows ?? "—"}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Uploaded Files</span>
              <span className="text-gray-800 font-medium">{files.length}</span>
            </div>
          </div>
        </div>

        {/* Data Management */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Trash2 className="w-5 h-5 text-red-500" />
            <h2 className="font-semibold text-gray-800">Data Management</h2>
          </div>
          <p className="text-sm text-gray-500 mb-4">
            Clear all uploaded files and reset the warehouse. This action cannot be undone.
          </p>
          <button
            onClick={handleResetWarehouse}
            className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors"
          >
            Clear All Data
          </button>
        </div>
      </div>
    </div>
  );
}
