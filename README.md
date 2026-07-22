# Shopee BI & Analytics Dashboard

> **Data Uploaded:** 22 July 2026 | 09:00 WIB  
> **Author:** Created by Muhammad Shiddiq Azis 2026

An enterprise-grade Business Intelligence (BI) and analytics dashboard designed specifically for Shopee marketplace merchants, featuring advanced Horeca & Cafe bundling recommendations, interactive pivot tables, global filter controls, and sanitized data visualizations.

---

## Features & Capabilities

- **Executive KPI Cards**: Track Total Revenue, Total Orders, Total Customers, Average Basket Size, Repeat Customer Rate, and Active Cities with Month-over-Month (MoM) growth indicators.
- **Global Filter Bar**: Dynamically slice data across Date Ranges, Provinces/Regions, Product Categories, and Order Statuses.
- **Advanced Visualizations**:
  - Monthly Revenue Trend (MoM line chart).
  - Top Products by Revenue (Horizontal bar chart with optimized Y-axis margins to eliminate text clipping).
  - Shipping Provider Share (Pie chart with sanitized fallback handling for "Unknown" provider entries).
  - Regional Performance & Payment Method distribution.
- **Interactive Pivot Table**: SKU-level performance table including Units Sold, Total Revenue (Rp), Average Selling Price (ASP), and Cancellation Rate % with text search, sorting, and pagination.
- **Market Basket Analysis**: AI-powered association rule mining for Horeca & Cafe product bundling (Support Rate %, Confidence Rate %, Lift Score, and Suggested Action callouts).

---

## Project Directory Structure

```text
shopee-bi-dashboard/
├── backend/               # FastAPI backend & API routers (etl, files, analytics, dashboard)
├── frontend/              # Next.js 14+ App Router frontend
│   ├── src/
│   │   ├── app/           # App router pages (dashboard, upload, settings)
│   │   │   ├── dashboard/ # Main BI dashboard page
│   │   │   ├── upload/    # Multi-file upload & management page
│   │   │   └── layout.tsx # Root layout with global header and sticky footer
│   │   ├── components/    # Reusable UI components (FilterBar, PivotTable, MarketBasket)
│   │   └── lib/           # API client and TypeScript interfaces
│   └── package.json
├── database/              # DuckDB repository and database connectors
├── etl/                   # Shopee order export extraction, transformation & loading pipeline
├── tests/                 # Comprehensive pytest test suite (API, database, ETL, analytics)
└── README.md
```

---

## Quick Start Guide

### Prerequisites
- **Node.js** (v18+ recommended)
- **Python** (v3.10+)

### Installation & Running

1. **Clone the repository**:
   ```bash
   git clone https://github.com/shiddiqeuy/shopee-bi-dashboard.git
   cd shopee-bi-dashboard
   ```

2. **Run Backend API**:
   ```bash
   python -m uvicorn backend.main:app --reload --port 8000
   ```

3. **Run Frontend Development Server**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Contribution & Workflow Guidelines

1. **Branching Strategy**: Create feature branches from `master` (e.g., `feature/your-feature-name` or `fix/...`).
2. **Issues & Milestones**: Link all pull requests to corresponding GitHub issues and milestones.
3. **Testing**: Run backend tests (`python -m pytest`) and frontend builds (`npm --prefix frontend run build`) before opening a pull request.
4. **Attribution**: Always preserve copyright and author attribution (`Created by Muhammad Shiddiq Azis 2026`).
