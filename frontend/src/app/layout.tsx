import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "./sidebar";
import { DataProvider } from "./data-context";
import { Clock } from "lucide-react";

export const metadata: Metadata = {
  title: "Shopee BI Dashboard",
  description: "Business Intelligence Dashboard for Shopee Marketplace Analytics",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full bg-gray-50">
      <body className="h-full flex overflow-hidden">
        <DataProvider>
          <Sidebar />
          <div className="flex-1 flex flex-col h-full overflow-hidden">
            {/* Global Top Header */}
            <header className="bg-white border-b border-gray-200 px-6 py-3.5 flex items-center justify-between shrink-0 shadow-xs z-10">
              <div className="flex items-center gap-3">
                <h1 className="text-lg font-bold text-gray-900 tracking-tight">Shopee BI Dashboard</h1>
                <span className="text-xs bg-blue-50 text-blue-700 font-medium px-2.5 py-1 rounded-full border border-blue-100">
                  Enterprise Analytics v2.5
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200">
                <Clock className="w-3.5 h-3.5 text-blue-600" />
                <span>Data Uploaded: 22 July 2026 | 09:00 WIB</span>
              </div>
            </header>

            {/* Main Scrollable Content */}
            <main className="flex-1 overflow-auto p-6">{children}</main>

            {/* Sticky Footer */}
            <footer className="bg-white border-t border-gray-200 px-6 py-3 text-center text-xs text-gray-500 shrink-0">
              Created by Muhammad Shiddiq Azis 2026 • Shopee Marketplace Business Intelligence & Analytics Suite
            </footer>
          </div>
        </DataProvider>
      </body>
    </html>
  );
}
