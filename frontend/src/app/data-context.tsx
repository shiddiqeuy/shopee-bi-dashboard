"use client";

import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { api, ETLStatus } from "@/lib/api";

interface DataState {
  analytics: unknown | null;
  status: ETLStatus | null;
  loading: boolean;
}

interface DataContextType extends DataState {
  refreshAnalytics: () => Promise<void>;
  refreshStatus: () => Promise<void>;
}

const DataContext = createContext<DataContextType | null>(null);

export function DataProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DataState>({
    analytics: null,
    status: null,
    loading: false,
  });

  const refreshAnalytics = useCallback(async () => {
    setState((s) => ({ ...s, loading: true }));
    try {
      const analytics = await api.analytics.compute();
      setState((s) => ({ ...s, analytics, loading: false }));
    } catch {
      setState((s) => ({ ...s, loading: false }));
    }
  }, []);

  const refreshStatus = useCallback(async () => {
    try {
      const status = await api.etl.status();
      setState((s) => ({ ...s, status }));
    } catch {
      // ignore
    }
  }, []);

  return (
    <DataContext.Provider value={{ ...state, refreshAnalytics, refreshStatus }}>
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error("useData must be inside DataProvider");
  return ctx;
}
