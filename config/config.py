"""
Central configuration for the Shopee BI Dashboard.

All tunable settings live here. No hardcoded magic strings in business logic.
Marketplace-specific normalisation maps are defined here so new platforms
only need to add a new mapping block.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "logs"
DB_PATH = OUTPUT_DIR / "warehouse.duckdb"
DASHBOARD_OUTPUT = OUTPUT_DIR / "Shopee_Geographic_BI_Dashboard.xlsx"

# Ensure output / log dirs exist at import time
for _dir in (OUTPUT_DIR, LOG_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Theme ― Professional Green-Blue palette
# ---------------------------------------------------------------------------
THEME = {
    "primary": "#1B98F5",
    "secondary": "#0B6FA6",
    "accent": "#00C9A7",
    "background": "#F0F4F8",
    "card_bg": "#FFFFFF",
    "header_bg": "#1B98F5",
    "header_fg": "#FFFFFF",
    "table_header_bg": "#2E86AB",
    "table_header_fg": "#FFFFFF",
    "table_alt_row": "#E8F4F8",
    "kpi_bg": "#FFFFFF",
    "kpi_border": "#1B98F5",
    "positive": "#00C9A7",
    "negative": "#FF6B6B",
    "warning": "#FFB74D",
    "neutral": "#90A4AE",
    "chart_colors": [
        "#1B98F5", "#00C9A7", "#FF6B6B", "#FFB74D",
        "#A29BFE", "#FD79A8", "#55EFC4", "#FDCB6E",
        "#6C5CE7", "#00CEC9", "#E17055", "#0984E3",
    ],
}

# ---------------------------------------------------------------------------
# Column mapping ― Shopee export → canonical name
# ---------------------------------------------------------------------------
COLUMN_MAP = {
    "no. pesanan": "order_id",
    "nomor pesanan": "order_id",
    "order id": "order_id",
    "pesanan #": "order_id",
    "status pesanan": "order_status",
    "status": "order_status",
    "nama produk": "product_name",
    "produk": "product_name",
    "nama barang": "product_name",
    "sku": "product_sku",
    "varian": "variation",
    "tipe": "variation",
    "jumlah": "quantity",
    "kuantitas": "quantity",
    "qty": "quantity",
    "harga": "price",
    "harga satuan": "price",
    "total harga": "total_amount",
    "total": "total_amount",
    "subtotal": "total_amount",
    "nama pembeli": "buyer_name",
    "pembeli": "buyer_name",
    "username": "buyer_username",
    "pembeli username": "buyer_username",
    "kota": "city",
    "kota/kabupaten": "city",
    "kabupaten": "city",
    "provinsi": "province",
    "provinsi": "province",
    "metode pengiriman": "shipping_method",
    "kurir": "shipping_provider",
    "jasa kirim": "shipping_provider",
    "ongkos kirim": "shipping_cost",
    "biaya kirim": "shipping_cost",
    "metode pembayaran": "payment_method",
    "pembayaran": "payment_method",
    "tgl pesanan": "order_date",
    "tanggal pesanan": "order_date",
    "tgl pembayaran": "payment_date",
    "tanggal pembayaran": "payment_date",
    "tgl pengiriman": "shipping_date",
    "tanggal pengiriman": "shipping_date",
    "voucher toko": "voucher_seller",
    "voucher shopee": "voucher_shopee",
    "alasan pembatalan": "cancellation_reason",
    "alasan": "cancellation_reason",
}

# ---------------------------------------------------------------------------
# Columns that form the canonical schema
# ---------------------------------------------------------------------------
CANONICAL_COLUMNS = [
    "order_id",
    "order_status",
    "product_name",
    "product_sku",
    "variation",
    "quantity",
    "price",
    "total_amount",
    "buyer_name",
    "buyer_username",
    "city",
    "province",
    "shipping_provider",
    "shipping_method",
    "shipping_cost",
    "payment_method",
    "order_date",
    "payment_date",
    "shipping_date",
    "voucher_seller",
    "voucher_shopee",
    "cancellation_reason",
]

# ---------------------------------------------------------------------------
# Currency / format
# ---------------------------------------------------------------------------
CURRENCY = "IDR"
CURRENCY_FORMAT = 'Rp #,##0'
CURRENCY_FORMAT_FULL = 'Rp #,##0.00'
PERCENT_FORMAT = "0.00%"
NUMERIC_FORMAT = "#,##0"
DECIMAL_FORMAT = "#,##0.00"

# ---------------------------------------------------------------------------
# City name normalisation  (lowercase input → canonical)
# ---------------------------------------------------------------------------
CITY_ALIASES: dict[str, str] = {
    "jakarta pusat": "Jakarta Pusat",
    "jakpus": "Jakarta Pusat",
    "jakarta-pusat": "Jakarta Pusat",
    "jakarta selatan": "Jakarta Selatan",
    "jaksel": "Jakarta Selatan",
    "jakarta-selatan": "Jakarta Selatan",
    "jakarta barat": "Jakarta Barat",
    "jakbar": "Jakarta Barat",
    "jakarta-barat": "Jakarta Barat",
    "jakarta timur": "Jakarta Timur",
    "jaktim": "Jakarta Timur",
    "jakarta-timur": "Jakarta Timur",
    "jakarta utara": "Jakarta Utara",
    "jakut": "Jakarta Utara",
    "jakarta-utara": "Jakarta Utara",
    "bandung": "Bandung",
    "kota bandung": "Bandung",
    "surabaya": "Surabaya",
    "kota surabaya": "Surabaya",
    "medan": "Medan",
    "kota medan": "Medan",
    "tangerang": "Tangerang",
    "kota tangerang": "Tangerang",
    "tangerang selatan": "Tangerang Selatan",
    "tangsel": "Tangerang Selatan",
    "bekasi": "Bekasi",
    "kota bekasi": "Bekasi",
    "depok": "Depok",
    "kota depok": "Depok",
    "semarang": "Semarang",
    "kota semarang": "Semarang",
    "makassar": "Makassar",
    "kota makassar": "Makassar",
    "palembang": "Palembang",
    "kota palembang": "Palembang",
    "yogyakarta": "Yogyakarta",
    "kota yogyakarta": "Yogyakarta",
    "jogja": "Yogyakarta",
    "malang": "Malang",
    "kota malang": "Malang",
    "solo": "Surakarta",
    "surakarta": "Surakarta",
    "balikpapan": "Balikpapan",
    "kota balikpapan": "Balikpapan",
    "batam": "Batam",
    "kota batam": "Batam",
    "pekanbaru": "Pekanbaru",
    "kota pekanbaru": "Pekanbaru",
    "denpasar": "Denpasar",
    "kota denpasar": "Denpasar",
    "bogor": "Bogor",
    "kota bogor": "Bogor",
}

# ---------------------------------------------------------------------------
# Province name normalisation
# ---------------------------------------------------------------------------
PROVINCE_ALIASES: dict[str, str] = {
    "dki jakarta": "DKI Jakarta",
    "d.k.i. jakarta": "DKI Jakarta",
    "jakarta": "DKI Jakarta",
    "jawa barat": "Jawa Barat",
    "jabar": "Jawa Barat",
    "jawa timur": "Jawa Timur",
    "jatim": "Jawa Timur",
    "jawa tengah": "Jawa Tengah",
    "jateng": "Jawa Tengah",
    "sumatera utara": "Sumatera Utara",
    "sumut": "Sumatera Utara",
    "sumatera selatan": "Sumatera Selatan",
    "sumsel": "Sumatera Selatan",
    "sumatera barat": "Sumatera Barat",
    "sumbar": "Sumatera Barat",
    "kalimantan timur": "Kalimantan Timur",
    "kaltim": "Kalimantan Timur",
    "kalimantan selatan": "Kalimantan Selatan",
    "kalsel": "Kalimantan Selatan",
    "kalimantan barat": "Kalimantan Barat",
    "kalbar": "Kalimantan Barat",
    "kalimantan tengah": "Kalimantan Tengah",
    "kalteng": "Kalimantan Tengah",
    "sulawesi selatan": "Sulawesi Selatan",
    "sulsel": "Sulawesi Selatan",
    "sulawesi utara": "Sulawesi Utara",
    "sulut": "Sulawesi Utara",
    "banten": "Banten",
    "kepulauan riau": "Kepulauan Riau",
    "kepri": "Kepulauan Riau",
    "aceh": "Aceh",
    "nanggroe aceh darussalam": "Aceh",
    "bali": "Bali",
    "lampung": "Lampung",
    "riau": "Riau",
    "ntt": "Nusa Tenggara Timur",
    "nusa tenggara timur": "Nusa Tenggara Timur",
    "ntb": "Nusa Tenggara Barat",
    "nusa tenggara barat": "Nusa Tenggara Barat",
    "papua": "Papua",
    "papua barat": "Papua Barat",
}

# ---------------------------------------------------------------------------
# Shipping provider normalisation
# ---------------------------------------------------------------------------
SHIPPING_ALIASES: dict[str, str] = {
    "jne": "JNE",
    "j&t": "J&T",
    "jnt": "J&T",
    "j and t": "J&T",
    "sicepat": "SiCepat",
    "sicepat express": "SiCepat",
    "pos indonesia": "POS Indonesia",
    "pos": "POS Indonesia",
    "anteraja": "AnterAja",
    "ninja express": "Ninja Express",
    "ninja": "Ninja Express",
    "shopee express": "Shopee Express",
    "spx": "Shopee Express",
    "gosend": "GoSend",
    "go send": "GoSend",
    "grab express": "Grab Express",
    "grab": "Grab Express",
}

# ---------------------------------------------------------------------------
# Payment method normalisation
# ---------------------------------------------------------------------------
PAYMENT_ALIASES: dict[str, str] = {
    "transfer bank": "Transfer Bank",
    "transfer": "Transfer Bank",
    "bank transfer": "Transfer Bank",
    "bca": "Transfer Bank",
    "mandiri": "Transfer Bank",
    "bni": "Transfer Bank",
    "bri": "Transfer Bank",
    "cod": "COD",
    "cash on delivery": "COD",
    "bayar di tempat": "COD",
    "ovo": "OVO",
    "gopay": "GoPay",
    "dana": "DANA",
    "linkaja": "LinkAja",
    "shopee pay": "ShopeePay",
    "shopeepay": "ShopeePay",
    "kartu kredit": "Kartu Kredit",
    "kredit": "Kartu Kredit",
    "credit card": "Kartu Kredit",
    "virtual account": "Virtual Account",
    "va": "Virtual Account",
}

# ---------------------------------------------------------------------------
# Product normalisation (brand / product mapping)
# ---------------------------------------------------------------------------
PRODUCT_ALIASES: dict[str, str] = {
    # Extend this with your actual product catalogue over time
}

# ---------------------------------------------------------------------------
# Analytics parameters
# ---------------------------------------------------------------------------
ANALYTICS = {
    "rfm_recency_days": 90,
    "rfm_frequency_bins": 4,
    "rfm_monetary_bins": 4,
    "pareto_threshold": 0.80,
    "abc_a_threshold": 0.70,
    "abc_b_threshold": 0.90,
    "fast_moving_days": 30,
    "slow_moving_days": 90,
    "growth_periods": 3,
    "opportunity_score_weight": {
        "revenue_growth": 0.30,
        "customer_growth": 0.25,
        "repeat_rate": 0.20,
        "avg_basket": 0.15,
        "population_proxy": 0.10,
    },
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
