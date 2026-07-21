"use client";

import { useState, useEffect, useCallback } from "react";
import { api, FileInfo, ETLResult } from "@/lib/api";
import { useData } from "../data-context";
import { Upload, Trash2, FileSpreadsheet, CheckCircle, XCircle, Loader2 } from "lucide-react";

export default function UploadPage() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<ETLResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { refreshStatus } = useData();

  const loadFiles = useCallback(async () => {
    try {
      const data = await api.files.list();
      setFiles(data.files);
    } catch {}
  }, []);

  useEffect(() => { loadFiles(); }, [loadFiles]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setResult(null);
    setError(null);
    try {
      const res = await api.etl.upload(file);
      setResult(res);
      await loadFiles();
      await refreshStatus();
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(name: string) {
    await api.files.delete(name);
    await loadFiles();
  }

  async function handleClear() {
    await api.files.clear();
    await loadFiles();
  }

  return (
    <div>
      <h1 className="page-header">Upload Data</h1>

      {/* Upload Area */}
      <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-8 mb-6 text-center hover:border-blue-400 transition-colors">
        <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
        <p className="text-sm text-gray-600 mb-4">
          Upload a Shopee order export file (.xlsx, .xls, .csv)
        </p>
        <label className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors">
          <FileSpreadsheet className="w-4 h-4" />
          Choose File
          <input type="file" accept=".xlsx,.xls,.csv" onChange={handleUpload} className="hidden" disabled={uploading} />
        </label>
        {uploading && (
          <div className="flex items-center justify-center gap-2 mt-4 text-blue-600">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="text-sm">Processing ETL pipeline...</span>
          </div>
        )}
      </div>

      {/* Result */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2 text-green-700 font-medium mb-1">
            <CheckCircle className="w-5 h-5" />
            ETL Complete
          </div>
          <p className="text-sm text-green-600">
            Loaded {result.rows_loaded} rows from {result.filename}
            {result.warehouse_built && " • Warehouse built"}
          </p>
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2 text-red-700 font-medium mb-1">
            <XCircle className="w-5 h-5" />
            Error
          </div>
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* File List */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-800">Uploaded Files ({files.length})</h2>
          {files.length > 0 && (
            <button onClick={handleClear} className="text-sm text-red-600 hover:text-red-700">
              Clear All
            </button>
          )}
        </div>
        {files.length === 0 ? (
          <div className="p-8 text-center text-gray-400 text-sm">No files uploaded yet</div>
        ) : (
          <div className="divide-y divide-gray-100">
            {files.map((f) => (
              <div key={f.name} className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-800">{f.name}</p>
                    <p className="text-xs text-gray-400">{f.size_display}</p>
                  </div>
                </div>
                <button onClick={() => handleDelete(f.name)} className="p-1.5 text-gray-400 hover:text-red-500 transition-colors">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
