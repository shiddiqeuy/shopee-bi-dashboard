import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "./sidebar";
import { DataProvider } from "./data-context";

export const metadata: Metadata = {
  title: "Shopee BI Dashboard",
  description: "Business Intelligence Dashboard for Shopee Marketplace Analytics",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full flex">
        <DataProvider>
          <Sidebar />
          <main className="flex-1 overflow-auto p-6">{children}</main>
        </DataProvider>
      </body>
    </html>
  );
}
