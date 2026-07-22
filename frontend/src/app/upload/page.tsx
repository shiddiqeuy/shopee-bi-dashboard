"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { api, FileInfo, ETLResult } from "@/lib/api";
import { useData } from "../data-context";
import { Upload, Trash2, FileSpreadsheet, CheckCircle, XCircle, Loader2, RefreshCw, ArrowUpDown, Play } from "lucide-react";

type ETLStepStatus = "pending" | "active" | "done" | "error";

interface ETLStep {
  label: string;
  description: string;
  status: ETLStepStatus;
}

const PROCESS_STEPS: Omit<ETLStep, "status">[] = [
  { label: "Upload", description: "Save selected file(s) to the input folder" },
  { label: "Extract", description: "Read Shopee workbook or CSV rows" },
  { label: "Transform", description: "Normalize columns, clean values, and validate records" },
  { label: "Load", description: "Write clean order rows into the staging table" },
  { label: "Warehouse", description: "Rebuild analytics tables and refresh dashboard status" },
];

function buildSteps(activeIndex = 0): ETLStep[] {
  return PROCESS_STEPS.map((step, index) => ({
    ...step,
    status: index < activeIndex ? "done" : index === activeIndex ? "active" : "pending",
  }));
}

function completedSteps(): ETLStep[] {
  return PROCESS_STEPS.map((step) => ({ ...step, status: "done" }));
}

function failedSteps(activeIndex: number): ETLStep[] {
  return PROCESS_STEPS.map((step, index) => ({
    ...step,
    status: index < activeIndex ? "done" : index === activeIndex ? "error" : "pending",
  }));
}

function errorMessage(err: unknown, fallback: string): string {
  return err instanceof Error ? err.message : fallback;
}

export default function UploadPage() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<ETLResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<"name" | "date" | "size">("date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [etlSteps, setEtlSteps] = useState<ETLStep[]>(buildSteps());
  const [processTitle, setProcessTitle] = useState<string | null>(null);

  const { refreshStatus } = useData();

  const loadFiles = useCallback(async () => {
    try {
      const data = await api.files.list();
      setFiles(data.files);
    } catch {}
  }, []);

  useEffect(() => {
    let active = true;

    async function loadInitialFiles() {
      try {
        const data = await api.files.list();
        if (active) {
          setFiles(data.files);
        }
      } catch {}
    }

    void loadInitialFiles();
    return () => {
      active = false;
    };
  }, []);

  function beginProcess(title: string) {
    setProcessTitle(title);
    setEtlSteps(buildSteps(0));
  }

  function markRunningPipeline() {
    setEtlSteps(buildSteps(2));
  }

  function markRefreshing() {
    setEtlSteps(buildSteps(4));
  }

  function markComplete() {
    setEtlSteps(completedSteps());
  }

  function markFailed(activeIndex: number) {
    setEtlSteps(failedSteps(activeIndex));
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files;
    if (!selected || selected.length === 0) return;
    setUploading(true);
    setResults(null);
    setError(null);
    beginProcess(`Uploading ${selected.length} file${selected.length === 1 ? "" : "s"}`);
    try {
      markRunningPipeline();
      const res = await api.etl.uploadMultiple(selected);
      setResults(res.results);
      markRefreshing();
      await loadFiles();
      await refreshStatus();
      if (res.results.some((r) => r.status !== "success")) {
        markFailed(3);
        setError("Beberapa file gagal diproses. Detail teknis sudah dicatat di backend log.");
      } else {
        markComplete();
      }
    } catch (err: unknown) {
      markFailed(2);
      setError(errorMessage(err, "Upload failed"));
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleReplace(name: string, e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    setResults(null);
    beginProcess(`Replacing ${name}`);
    try {
      markRunningPipeline();
      const res = await api.files.replace(name, file);
      setResults([res]);
      markRefreshing();
      await loadFiles();
      await refreshStatus();
      if (res.status !== "success") {
        markFailed(3);
        setError(res.error || "File gagal diproses. Detail teknis sudah dicatat di backend log.");
      } else {
        markComplete();
      }
    } catch (err: unknown) {
      markFailed(2);
      setError(errorMessage(err, "File replacement failed"));
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleReload(name: string) {
    setUploading(true);
    setError(null);
    setResults(null);
    beginProcess(`Running ETL for ${name}`);
    try {
      markRunningPipeline();
      const res = await api.etl.reload(name);
      setResults([res]);
      markRefreshing();
      await loadFiles();
      await refreshStatus();
      if (res.status !== "success") {
        markFailed(3);
        setError(res.error || "ETL gagal diproses. Detail teknis sudah dicatat di backend log.");
      } else {
        markComplete();
      }
    } catch (err: unknown) {
      markFailed(2);
      setError(errorMessage(err, "ETL reload failed"));
    } finally {
      setUploading(false);
    }
  }

  async function handleReloadAll() {
    setUploading(true);
    setError(null);
    setResults(null);
    beginProcess(`Running ETL for ${files.length} file${files.length === 1 ? "" : "s"}`);
    try {
      markRunningPipeline();
      const res = await api.etl.reloadAll();
      setResults(res.results);
      markRefreshing();
      await loadFiles();
      await refreshStatus();
      if (res.results.some((r) => r.status !== "success")) {
        markFailed(3);
        setError("Sebagian proses ETL gagal. Detail teknis sudah dicatat di backend log.");
      } else {
        markComplete();
      }
    } catch (err: unknown) {
      markFailed(2);
      setError(errorMessage(err, "ETL reload all failed"));
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(name: string) {
    await api.files.delete(name);
    setSelectedFiles((prev) => prev.filter((n) => n !== name));
    await loadFiles();
  }

  async function handleBulkDelete() {
    if (selectedFiles.length === 0) return;
    for (const name of selectedFiles) {
      await api.files.delete(name);
    }
    setSelectedFiles([]);
    await loadFiles();
  }

  async function handleClear() {
    await api.files.clear();
    setSelectedFiles([]);
    await loadFiles();
  }

  function toggleSelectAll() {
    if (selectedFiles.length === files.length) {
      setSelectedFiles([]);
    } else {
      setSelectedFiles(files.map((f) => f.name));
    }
  }

  function toggleSelectFile(name: string) {
    setSelectedFiles((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name]
    );
  }

  const sortedFiles = useMemo(() => {
    return [...files].sort((a, b) => {
      let cmp = 0;
      if (sortBy === "name") {
        cmp = a.name.localeCompare(b.name);
      } else if (sortBy === "date") {
        cmp = a.modified - b.modified;
      } else if (sortBy === "size") {
        cmp = a.size - b.size;
      }
      return sortOrder === "asc" ? cmp : -cmp;
    });
  }, [files, sortBy, sortOrder]);

  const successCount = results?.filter((r) => r.status === "success").length || 0;
  const failCount = results?.filter((r) => r.status !== "success").length || 0;

  return (
    <div>
      <h1 className="page-header">Upload & File Management</h1>

      {/* Upload Area */}
      <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-8 mb-6 text-center hover:border-blue-400 transition-colors">
        <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
        <p className="text-sm text-gray-600 mb-4">
          Upload Shopee order export files (.xlsx, .xls, .csv) - Multiple files supported
        </p>
        <label className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors">
          <FileSpreadsheet className="w-4 h-4" />
          Choose Files
          <input type="file" multiple accept=".xlsx,.xls,.csv" onChange={handleUpload} className="hidden" disabled={uploading} />
        </label>
        {uploading && (
          <div className="flex items-center justify-center gap-2 mt-4 text-blue-600">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="text-sm">Processing files & ETL pipeline...</span>
          </div>
        )}
      </div>

      {/* ETL Process */}
      {processTitle && (
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
          <div className="flex items-center justify-between gap-3 mb-4 flex-wrap">
            <div>
              <h2 className="font-semibold text-gray-800">ETL Process</h2>
              <p className="text-xs text-gray-500 mt-1">{processTitle}</p>
            </div>
            <span className="text-xs font-medium text-gray-500 bg-gray-100 rounded-full px-3 py-1">
              {uploading ? "Running" : error ? "Needs attention" : "Complete"}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            {etlSteps.map((step, index) => {
              const isActive = step.status === "active";
              const isDone = step.status === "done";
              const isError = step.status === "error";
              return (
                <div
                  key={step.label}
                  className={`rounded-lg border p-3 ${
                    isError
                      ? "border-red-200 bg-red-50"
                      : isDone
                      ? "border-green-200 bg-green-50"
                      : isActive
                      ? "border-blue-200 bg-blue-50"
                      : "border-gray-200 bg-gray-50"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${
                        isError
                          ? "bg-red-600 text-white"
                          : isDone
                          ? "bg-green-600 text-white"
                          : isActive
                          ? "bg-blue-600 text-white"
                          : "bg-gray-200 text-gray-500"
                      }`}
                    >
                      {isActive ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : isDone ? "✓" : isError ? "!" : index + 1}
                    </div>
                    <span className="text-sm font-medium text-gray-800">{step.label}</span>
                  </div>
                  <p className="text-xs text-gray-500 leading-relaxed">{step.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Results Summary */}
      {results && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2 text-blue-700 font-medium mb-2">
            <CheckCircle className="w-5 h-5" />
            Operation Complete ({successCount} succeeded{failCount > 0 ? `, ${failCount} failed` : ""})
          </div>
          <div className="space-y-1">
            {results.map((r, i) => (
              <div key={i} className="text-sm flex items-center justify-between text-gray-700 py-1 border-t border-blue-100">
                <span className="font-medium">{r.filename}</span>
                <span className={r.status === "success" ? "text-green-600" : "text-red-600"}>
                  {r.status === "success" ? `${r.rows_loaded ?? 0} rows loaded` : "Failed"}
                </span>
                {r.status !== "success" && r.error && (
                  <span className="text-xs text-red-500 md:ml-4">{r.error}</span>
                )}
              </div>
            ))}
          </div>
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

      {/* File List & Management */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="flex items-center justify-between p-4 border-b border-gray-200 flex-wrap gap-3">
          <div className="flex items-center gap-3 flex-wrap">
            <h2 className="font-semibold text-gray-800">Uploaded Files ({files.length})</h2>
            {selectedFiles.length > 0 && (
              <button
                onClick={handleBulkDelete}
                className="text-xs bg-red-100 text-red-600 hover:bg-red-200 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 font-medium"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Delete Selected ({selectedFiles.length})
              </button>
            )}
            {files.length > 0 && (
              <button
                onClick={handleReloadAll}
                disabled={uploading}
                className="text-xs bg-emerald-100 text-emerald-700 hover:bg-emerald-200 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 font-medium disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5" />
                Re-run All ETL
              </button>
            )}
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <ArrowUpDown className="w-3.5 h-3.5" />
              <span>Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as "name" | "date" | "size")}
                className="border border-gray-300 rounded px-2 py-1 text-xs bg-white text-gray-700"
              >
                <option value="date">Date</option>
                <option value="name">Name</option>
                <option value="size">Size</option>
              </select>
              <button
                onClick={() => setSortOrder((o) => (o === "asc" ? "desc" : "asc"))}
                className="border border-gray-300 rounded px-2 py-1 text-xs bg-white hover:bg-gray-50"
              >
                {sortOrder === "asc" ? "ASC" : "DESC"}
              </button>
            </div>

            {files.length > 0 && (
              <button onClick={handleClear} className="text-sm text-red-600 hover:text-red-700 font-medium">
                Clear All
              </button>
            )}
          </div>
        </div>

        {files.length === 0 ? (
          <div className="p-8 text-center text-gray-400 text-sm">No files uploaded yet</div>
        ) : (
          <div>
            <div className="flex items-center px-4 py-2 bg-gray-50 border-b border-gray-100 text-xs font-medium text-gray-500">
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={selectedFiles.length === files.length && files.length > 0}
                  onChange={toggleSelectAll}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span>Name</span>
              </div>
              <div className="ml-auto flex items-center gap-8 pr-40 text-right">
                <span>Size</span>
                <span>Upload Date</span>
              </div>
            </div>
            <div className="divide-y divide-gray-100">
              {sortedFiles.map((f) => {
                const isSelected = selectedFiles.includes(f.name);
                const dateStr = new Date(f.modified * 1000).toLocaleString();
                return (
                  <div key={f.name} className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleSelectFile(f.name)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <FileSpreadsheet className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-800">{f.name}</p>
                        <p className="text-xs text-gray-400 md:hidden">{f.size_display} • {dateStr}</p>
                      </div>
                    </div>

                    <div className="hidden md:flex items-center gap-8 text-xs text-gray-500">
                      <span>{f.size_display}</span>
                      <span className="w-36 text-right">{dateStr}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleReload(f.name)}
                        disabled={uploading}
                        className="inline-flex items-center gap-1 text-xs px-2.5 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-colors disabled:opacity-50"
                        title="Re-run ETL on this file"
                      >
                        <Play className="w-3.5 h-3.5" />
                        Re-run ETL
                      </button>
                      <label className="inline-flex items-center gap-1 text-xs px-2.5 py-1.5 border border-gray-300 text-gray-700 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                        <RefreshCw className="w-3.5 h-3.5" />
                        Replace
                        <input
                          type="file"
                          accept=".xlsx,.xls,.csv"
                          onChange={(e) => handleReplace(f.name, e)}
                          className="hidden"
                          disabled={uploading}
                        />
                      </label>
                      <button
                        onClick={() => handleDelete(f.name)}
                        className="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
                        title="Delete file"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
