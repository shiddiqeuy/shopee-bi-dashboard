"""
Constants enumerations for the Shopee BI Dashboard.

All enum values are stable identifiers used across the application.
Marketplace-specific values belong in config.py mappings, not here.
"""

from __future__ import annotations

from enum import Enum, auto


class SheetName(str, Enum):
    EXECUTIVE = "Executive Dashboard"
    KPI = "KPI Summary"
    CITY = "City Performance"
    PROVINCE = "Province Performance"
    PRODUCT = "Product Performance"
    CUSTOMER = "Customer Behaviour"
    TREND = "Monthly Trend"
    SHIPPING = "Shipping"
    PAYMENT = "Payment"
    CANCELLATION = "Cancellation"
    INSIGHT = "Hidden Insight"
    RAW = "Raw Data"
    METHODOLOGY = "Methodology"


class Metric(str, Enum):
    REVENUE = "revenue"
    ORDER_COUNT = "order_count"
    CUSTOMER_COUNT = "customer_count"
    AVG_BASKET = "avg_basket"
    REPEAT_RATE = "repeat_rate"
    CLV = "customer_lifetime_value"
    CANCELLATION_RATE = "cancellation_rate"
    SHIPPING_COST = "shipping_cost"
    GROWTH_RATE = "growth_rate"
    CONTRIBUTION = "contribution"


class OrderStatus(str, Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SHIPPED = "shipped"
    PROCESSING = "processing"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    COD = "cod"
    E_WALLET = "e_wallet"
    CREDIT_CARD = "credit_card"
    VIRTUAL_ACCOUNT = "virtual_account"
    OTHERS = "others"


class ShippingProvider(str, Enum):
    JNE = "jne"
    JNT = "jnt"
    SICEPAT = "sicepat"
    POS = "pos_indonesia"
    ANTERAJA = "anteraja"
    NINJA = "ninja_express"
    SHOPEE_EXPRESS = "shopee_express"
    GOSEND = "gosend"
    GRAB = "grab_express"
    OTHERS = "others"


class CustomerSegment(str, Enum):
    CHAMPION = "champion"
    LOYAL = "loyal"
    POTENTIAL = "potential"
    NEW = "new"
    AT_RISK = "at_risk"
    NEEDS_ATTENTION = "needs_attention"
    ABOUT_TO_SLEEP = "about_to_sleep"
    HIBERNATING = "hibernating"
    LOST = "lost"


class ProductClass(str, Enum):
    A = "A"  # Top 70% revenue
    B = "B"  # Next 20%
    C = "C"  # Bottom 10%


class InsightType(str, Enum):
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    ANOMALY = "anomaly"
    RECOMMENDATION = "recommendation"
    HIDDEN_POTENTIAL = "hidden_potential"
    GEOGRAPHIC_AFFINITY = "geographic_affinity"


class DatabaseTable(str, Enum):
    ORDERS = "orders"
    CUSTOMERS = "customers"
    PRODUCTS = "products"
    CITIES = "cities"
    PROVINCES = "provinces"
    SHIPPING = "shipping"
    PAYMENTS = "payments"
    CALENDAR = "calendar"
    FACT_SALES = "fact_sales"
    DIM_CUSTOMER = "dim_customer"
    DIM_PRODUCT = "dim_product"
    DIM_CITY = "dim_city"
    DIM_DATE = "dim_date"
