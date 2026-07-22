# AGENT.md - AI Context & Guidelines for Shopee BI Dashboard

This document provides architectural context, file maps, coding standards, and constraints for AI coding agents working on the Shopee BI Dashboard project.

---

## 1. System Context & Architecture

- **Frontend Stack**: Next.js 14+ (App Router), React, Tailwind CSS, Recharts, Lucide React icons.
- **Backend Stack**: FastAPI, DuckDB, Polars/Pandas ETL pipeline.
- **State Management**: React Context (`DataProvider` in `frontend/src/app/data-context.tsx`) combined with local component state for filters, sorting, and search pagination.
- **Data Flow**: Frontend fetches REST endpoints (`/api/analytics/compute`, `/api/files/`, `/api/etl/...`) and updates dashboard views dynamically.

---

## 2. File Map & Responsibility Matrix

| Component / File Path | Core Responsibility |
| :--- | :--- |
| `frontend/src/app/layout.tsx` | Root layout with global header ("Shopee BI Dashboard" + upload timestamp metadata) & sticky footer ("Created by Muhammad Shiddiq Azis 2026"). |
| `frontend/src/app/dashboard/page.tsx` | Main BI Dashboard view integrating KPI cards, Recharts visualizations, FilterBar, PivotTable, and MarketBasket. |
| `frontend/src/components/FilterBar.tsx` | Global filter controls (Date Range, Province, Product Category, Order Status). |
| `frontend/src/components/PivotTable.tsx` | Interactive product performance table with search, sorting, and pagination. |
| `frontend/src/components/MarketBasket.tsx` | Association rule mining card displaying product bundles, support/confidence/lift metrics, and action callouts. |
| `frontend/src/lib/api.ts` | TypeScript API client wrapper and data contracts (`FileInfo`, `ETLResult`, `ETLStatus`). |
| `backend/api/` | FastAPI routers (`etl.py`, `files.py`, `analytics.py`, `dashboard.py`). |

---

## 3. Coding Standards & AI Constraints

### TypeScript & React Rules
- **Strict Typing**: Avoid `any` where possible. Define clear interfaces for component props and API responses.
- **Client Components**: Ensure components using React hooks (`useState`, `useEffect`, `useCallback`) begin with `"use client";`.
- **Responsive Design**: Maintain mobile-first responsive layouts using Tailwind CSS utility classes (`grid-cols-1 md:grid-cols-2 lg:grid-cols-4`, `overflow-x-auto`, etc.).

### Data Visualization & Metric Rules
- **Y-Axis Width**: For horizontal bar charts (e.g., Top Products by Revenue), ensure `YAxis` has sufficient width (`width={180}` or truncated labels with tooltips) to prevent text clipping/overlapping.
- **Data Sanitization**: Always sanitize categorical data. If shipping providers or payment methods return `null`, empty strings, or `"Unknown"`, fall back gracefully to `"Standard Reguler (Fallback)"` or grouped categories.
- **Association Metrics**: Market Basket analysis components must clearly display Support Rate %, Confidence Rate %, and Lift Score with professional badge indicators.

---

## 4. Do's and Don'ts for AI Assistants

- **DO** preserve author attribution: `"Created by Muhammad Shiddiq Azis 2026"` in the sticky footer and layout headers.
- **DO** maintain data upload timestamp metadata: `"Data Uploaded: 22 July 2026 | 09:00 WIB"`.
- **DO** ensure all backend pytest tests pass (`python -m pytest`) and frontend builds successfully (`npm run build`) before finalizing any code modifications.
- **DON'T** break existing component contracts, API endpoints, or context providers.
- **DON'T** introduce unverified third-party UI libraries without checking `package.json`.
