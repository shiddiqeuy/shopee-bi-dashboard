# Shopee BI & Analytics Dashboard

> **Data Uploaded:** 22 July 2026 | 09:00 WIB  
> **Author:** Created by Muhammad Shiddiq Azis 2026

An enterprise-grade Business Intelligence (BI) and analytics dashboard designed specifically for Shopee marketplace merchants, featuring advanced Horeca & Cafe bundling recommendations, interactive pivot tables, global filter controls, and sanitized data visualizations.

---

## Project Links

- **Documentation Wiki**: [Open the project Wiki](https://github.com/shiddiqeuy/shopee-bi-dashboard/wiki) for architecture, setup, ETL, analytics, and agent guidelines.
- **Contribution Guide**: Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening your first Pull Request.
- **Discussions**: Share ideas, questions, and improvement proposals in [GitHub Discussions](https://github.com/shiddiqeuy/shopee-bi-dashboard/discussions).
- **Improvement Ideas**: Use the [Ideas category](https://github.com/shiddiqeuy/shopee-bi-dashboard/discussions/categories/ideas) for suggestions before they become Issues.

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

## Deployment: Vercel Frontend + Railway Backend

This monorepo can be deployed as two services from the same GitHub repository.

### Backend on Railway

- **Root Directory**: repository root
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variable**: `CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000`
- **Health Check Path**: `/api/health`

`CORS_ORIGINS` accepts a comma-separated list of allowed origins. The local default remains `http://localhost:3000`.

### Frontend on Vercel

- **Root Directory**: `frontend`
- **Install Command**: `npm ci`
- **Build Command**: `npm run build`
- **Environment Variable**: `BACKEND_URL=https://<your-railway-backend-url>`

The frontend proxies `/api/*` requests to `BACKEND_URL`, so the existing frontend API client can continue using `/api` in both local and production environments.

---

## Contribution & Workflow Guidelines

Contributions are welcome. If this is your first open source contribution, start with the [Contribution Guide](CONTRIBUTING.md).

1. **Discuss First**: Use [GitHub Discussions](https://github.com/shiddiqeuy/shopee-bi-dashboard/discussions) for questions and improvement ideas.
2. **Branching Strategy**: Create feature branches from `master` (e.g., `feature/your-feature-name` or `fix/...`).
3. **Issues & Milestones**: Link all pull requests to corresponding GitHub issues and milestones when available.
4. **Documentation**: Check the [Project Wiki](https://github.com/shiddiqeuy/shopee-bi-dashboard/wiki) for architecture, setup, and workflow context.
5. **Testing**: Run backend tests (`python -m pytest`) and frontend builds (`npm --prefix frontend run build`) before opening a pull request.
6. **Attribution**: Always preserve copyright and author attribution (`Created by Muhammad Shiddiq Azis 2026`).
