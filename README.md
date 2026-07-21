# Shopee BI Dashboard

Enterprise-grade Business Intelligence Dashboard for Shopee marketplace analytics. Automatically generates a professional Excel dashboard from Shopee Order Export files.

## Architecture

```
input/*.xlsx → ETL → DuckDB → Analytics Engine → Excel Dashboard
                                      ↘ Streamlit BI App (interactive)
```

Built with Clean Architecture, SOLID principles, and a modular plugin system for future marketplace integration (Tokopedia, TikTok Shop, Lazada, etc.).

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline (CLI)
python main.py

# Or run individual stages
python main.py --etl-only
python main.py --analytics-only
python main.py --dashboard-only
python main.py --list-files
```

## Streamlit BI App (Interactive)

```bash
python -m streamlit run streamlit_app/app.py
```

Web-based interactive dashboard with:
- **Dashboard** — KPI grid, Top Customers table (name + revenue + orders + reorder count), 8 Altair chart panels (mobile-responsive), business insights
- **Upload** — Upload files via browser (saved to `input/`), preview columns, column validation, run ETL with live progress, manage existing files (list, run/re-run ETL, delete)
- **Reports** — Generate and download the Excel dashboard
- **Settings** — System info, analytics parameters, data management

## Dashboard Output

The generated Excel file (`output/Shopee_Geographic_BI_Dashboard.xlsx`) contains 13 sheets:

| Sheet | Content |
|-------|---------|
| Navigation | Clickable index |
| Executive Dashboard | Top KPIs + revenue trend chart |
| KPI Summary | Full metric table |
| City Performance | City ranking, growth, opportunity scores |
| Province Performance | Province ranking and contribution |
| Product Performance | ABC, Pareto, product affinity |
| Customer Behaviour | RFM, segmentation, top customers |
| Monthly Trend | Revenue, orders, MoM growth, moving average |
| Shipping | Courier performance and cost analysis |
| Payment | Method distribution and regional preference |
| Cancellation | Cancellation rate, reasons, breakdown |
| Hidden Insight | AI-generated business recommendations |
| Raw Data | Full order data for reference |
| Methodology | Metrics definitions and methodology |

## Project Structure

```
app/            → Application wiring
core/           → Domain entities, interfaces, exceptions
etl/            → Extract, transform, load pipelines
  shopee/       → Shopee-specific ETL
database/       → DuckDB connection, migrations, warehouse
analytics/      → Business logic modules (9 modules)
dashboard/      → Excel generation (13 sheet writers)
  sheets/       → Individual sheet implementations
charts/         → Chart builders (Excel + Plotly)
excel/          → XlsxWriter engine, styles, navigation
config/         → Configuration, constants, mappings
utils/          → Logger, helpers, decorators
tests/          → Pytest test suite
streamlit_app/  → Streamlit BI app (16 files)
  pages/        → Dashboard, Upload, Reports, Settings pages
  services/     → ETL, Analytics, Dashboard services
  components/   → Reusable UI components
input/          → Uploaded Shopee export files (managed from frontend)
output/         → Generated dashboard (.xlsx)
logs/           → ETL and application logs
```

## Database

DuckDB embedded analytics database is created at `output/warehouse.duckdb` with a star schema:

- `orders` — Staging table
- `dim_customer` — Customer dimension
- `dim_product` — Product dimension
- `dim_city` — Geographic city dimension
- `dim_date` — Calendar dimension
- `fact_sales` — Sales fact table

## Extending for New Marketplaces

1. Create `etl/<marketplace>/` with Extractor, Transformer, Loader
2. Add column mappings to `config/config.py`
3. Register the pipeline in `main.py`
4. Analytics modules work automatically

## Testing

```bash
pytest tests/
```

## License

MIT
