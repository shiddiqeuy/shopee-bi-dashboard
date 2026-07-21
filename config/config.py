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
    # ── Additional Shopee Indonesia export columns ──
    "no. pesanan": "order_id",
    "tipe pesanan": "order_type",
    "status pesanan": "order_status",
    "status pembatalan/ pengembalian": "return_status",
    "no. resi": "tracking_number",
    "opsi pengiriman": "shipping_method",
    "antar ke counter/ pick-up": "pickup_option",
    "pesanan harus dikirimkan sebelum (menghindari keterlambatan)": "must_ship_before",
    "waktu pengiriman diatur": "scheduled_shipping",
    "waktu pesanan dibuat": "order_date",
    "waktu pembayaran dilakukan": "payment_date",
    "metode pembayaran": "payment_method",
    "sku induk": "parent_sku",
    "nama produk": "product_name",
    "nomor referensi sku": "product_sku",
    "nama variasi": "variation",
    "harga awal": "original_price",
    "harga setelah diskon": "price",
    "jumlah": "quantity",
    "returned quantity": "returned_qty",
    "subtotal pesanan": "total_amount",
    "total diskon": "total_discount",
    "diskon dari penjual": "voucher_seller",
    "diskon dari shopee": "voucher_shopee",
    "berat produk": "product_weight",
    "jumlah produk di pesan": "product_count_in_order",
    "total berat": "total_weight",
    "voucher ditanggung penjual": "voucher_seller",
    "cashback koin": "coin_cashback",
    "voucher ditanggung shopee": "voucher_shopee",
    "paket diskon": "discount_pack",
    "paket diskon (diskon dari shopee)": "discount_pack_shopee",
    "paket diskon (diskon dari penjual)": "discount_pack_seller",
    "potongan koin shopee": "shopee_coin_discount",
    "diskon kartu kredit": "credit_card_discount",
    "ongkos kirim dibayar oleh pembeli": "shipping_cost",
    "estimasi potongan biaya pengiriman": "estimated_shipping_discount",
    "ongkos kirim pengembalian barang": "return_shipping_cost",
    "total pembayaran": "total_payment",
    "perkiraan ongkos kirim": "estimated_shipping_cost",
    "catatan dari pembeli": "buyer_note",
    "catatan": "note",
    "username (pembeli)": "buyer_username",
    "nama penerima": "buyer_name",
    "no. telepon": "phone",
    "alamat pengiriman": "shipping_address",
    "kota/kabupaten": "city",
    "provinsi": "province",
    "waktu pesanan selesai": "completed_date",
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
# City coordinates (lat, lon) for map visualisation
# ---------------------------------------------------------------------------
CITY_COORDS: dict[str, tuple[float, float]] = {
    "Jakarta Pusat": (-6.1818, 106.8223),
    "Jakarta Selatan": (-6.2615, 106.8103),
    "Jakarta Barat": (-6.1674, 106.7588),
    "Jakarta Timur": (-6.2250, 106.9000),
    "Jakarta Utara": (-6.1258, 106.8366),
    "Bandung": (-6.9175, 107.6191),
    "Surabaya": (-7.2504, 112.7688),
    "Medan": (3.5952, 98.6722),
    "Tangerang": (-6.1783, 106.6300),
    "Tangerang Selatan": (-6.2889, 106.7189),
    "Bekasi": (-6.2349, 106.9896),
    "Depok": (-6.4025, 106.7942),
    "Semarang": (-6.9932, 110.4203),
    "Makassar": (-5.1477, 119.4327),
    "Palembang": (-2.9761, 104.7754),
    "Yogyakarta": (-7.7971, 110.3688),
    "Malang": (-7.9819, 112.6265),
    "Surakarta": (-7.5566, 110.8317),
    "Balikpapan": (-1.2675, 116.8289),
    "Batam": (1.1261, 104.0495),
    "Pekanbaru": (0.5337, 101.4496),
    "Denpasar": (-8.6563, 115.2220),
    "Bogor": (-6.5977, 106.7990),
    "Bandar Lampung": (-5.4293, 105.2618),
    "Padang": (-0.9492, 100.3543),
    "Samarinda": (-0.4948, 117.1470),
    "Pontianak": (-0.0263, 109.3425),
    "Banjarmasin": (-3.3194, 114.5908),
    "Manado": (1.4916, 124.8418),
    "Mataram": (-8.5833, 116.1167),
    "Jambi": (-1.5899, 103.6143),
    "Aceh": (5.5483, 95.3238),
    "Banda Aceh": (5.5483, 95.3238),
    "Ambon": (-3.6554, 128.1908),
    "Kupang": (-10.1772, 123.6070),
    "Palangkaraya": (-2.2100, 113.9200),
    "Tanjung Pinang": (0.9167, 104.4667),
    "Gorontalo": (0.5333, 123.0667),
    "Mamuju": (-2.6833, 118.8833),
    "Kendari": (-3.9720, 122.5152),
    "Palu": (-0.8983, 119.8700),
    "Ternate": (0.7833, 127.3667),
    "Manokwari": (-0.8667, 134.0833),
    "Jayapura": (-2.5333, 140.7000),
    "Serang": (-6.1149, 106.1503),
    "Cilegon": (-6.0188, 106.0563),
    "Cimahi": (-6.8821, 107.5430),
    "Tasikmalaya": (-7.3274, 108.2207),
    "Cirebon": (-6.7152, 108.5681),
    "Kediri": (-7.8188, 112.0154),
    "Madiun": (-7.6311, 111.5305),
    "Blitar": (-8.0983, 112.1674),
    "Pasuruan": (-7.6454, 112.9067),
    "Probolinggo": (-7.7828, 113.2149),
    "Mojokerto": (-7.4722, 112.4381),
    "Salatiga": (-7.3305, 110.5042),
    "Magelang": (-7.4706, 110.2198),
    "Pekalongan": (-6.8888, 109.6737),
    "Tegal": (-6.8696, 109.1400),
    "Bukittinggi": (-0.3037, 100.3656),
    "Padang Panjang": (-0.4667, 100.4000),
    "Sawahlunto": (-0.6833, 100.7833),
    "Payakumbuh": (-0.2167, 100.6333),
    "Solok": (-0.8000, 100.6500),
    "Dumai": (1.6667, 101.4500),
    "Binjai": (3.6000, 98.5000),
    "Tebing Tinggi": (3.3333, 99.1667),
    "Pematang Siantar": (2.9667, 99.0667),
    "Sibolga": (1.7500, 98.7833),
    "Lhokseumawe": (5.1333, 97.1333),
    "Langsa": (4.4667, 97.9667),
    "Sabang": (5.8833, 95.3167),
    "Tarakan": (3.3000, 117.6000),
    "Bontang": (0.1333, 117.5000),
    "Singkawang": (0.9000, 109.0000),
    "Sukabumi": (-6.9246, 106.9262),
    "Banjarbaru": (-3.4630, 114.8413),
    "Pangkal Pinang": (-2.1312, 106.1138),
    "Unknown City": (-2.0, 118.0),
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
# Order status normalisation (canonical English → match codebase queries)
# ---------------------------------------------------------------------------
STATUS_ALIASES: dict[str, str] = {
    "batal": "cancelled",
    "dibatalkan": "cancelled",
    "cancel": "cancelled",
    "cancelled": "cancelled",
    "selesai": "completed",
    "completed": "completed",
    "selesai": "completed",
    "dikirim": "shipped",
    "telah dikirim": "shipped",
    "sedang dikirim": "in_transit",
    "perlu dikirim": "pending_shipment",
    "belum bayar": "pending_payment",
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
