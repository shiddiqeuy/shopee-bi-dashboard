const BASE = "/api";

async function errorFromResponse(res: Response, fallback: string): Promise<Error> {
  try {
    const body = await res.json();
    const message = body?.detail || body?.error || fallback;
    return new Error(message);
  } catch {
    return new Error(fallback);
  }
}

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, init);
  if (!res.ok) {
    throw await errorFromResponse(res, `API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export interface FileInfo {
  name: string;
  path: string;
  size: number;
  size_display: string;
  modified: number;
}

export interface ETLResult {
  filename: string;
  rows_loaded: number;
  warehouse_built: boolean;
  total_rows: number;
  status: string;
  error?: string;
}

export interface ETLStatus {
  data_available: boolean;
  total_rows: number;
}

export interface ETLLogEntry {
  timestamp: string;
  source_file: string;
  rows_extracted: number;
  rows_loaded: number;
  rows_invalid: number;
  status: string;
  error_message?: string | null;
  extra?: Record<string, unknown>;
}

export const api = {
  health: () => fetchJSON<{ status: string }>("/health"),

  etl: {
    upload: async (file: File): Promise<ETLResult> => {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${BASE}/etl/upload`, { method: "POST", body: form });
      if (!res.ok) throw await errorFromResponse(res, `Upload failed: ${res.status}`);
      return res.json();
    },
    uploadMultiple: async (files: FileList | File[]): Promise<{ results: ETLResult[] }> => {
      const form = new FormData();
      for (const file of Array.from(files)) {
        form.append("files", file);
      }
      const res = await fetch(`${BASE}/etl/upload-multiple`, { method: "POST", body: form });
      if (!res.ok) throw await errorFromResponse(res, `Multiple upload failed: ${res.status}`);
      return res.json();
    },
    status: () => fetchJSON<ETLStatus>("/etl/status"),
    logs: (limit = 25) => fetchJSON<{ logs: ETLLogEntry[] }>(`/etl/logs?limit=${limit}`),
    reload: (filename: string): Promise<ETLResult> =>
      fetchJSON<ETLResult>(`/etl/reload/${encodeURIComponent(filename)}`, { method: "POST" }),
    reloadAll: (): Promise<{ results: ETLResult[] }> =>
      fetchJSON<{ results: ETLResult[] }>("/etl/reload-all", { method: "POST" }),
    fileStatus: (filename: string): Promise<{ filename: string; exists: boolean; status: string; total_rows: number }> =>
      fetchJSON(`/etl/status/${encodeURIComponent(filename)}`),
  },

  analytics: {
    compute: () => fetchJSON<unknown>("/analytics/compute"),
  },

  dashboard: {
    download: () => `${BASE}/dashboard/download`,
  },

  files: {
    list: () => fetchJSON<{ files: FileInfo[] }>("/files/"),
    delete: (name: string) =>
      fetchJSON<{ deleted: boolean }>(`/files/${encodeURIComponent(name)}`, { method: "DELETE" }),
    clear: () => fetchJSON<{ deleted_count: number }>("/files/clear", { method: "POST" }),
    replace: async (name: string, file: File): Promise<ETLResult & { replaced: boolean }> => {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${BASE}/files/${encodeURIComponent(name)}`, { method: "PUT", body: form });
      if (!res.ok) throw await errorFromResponse(res, `File replacement failed: ${res.status}`);
      return res.json();
    },
  },
};
