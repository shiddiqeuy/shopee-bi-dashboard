"""
Tests for the Shopee transformer.
"""

from __future__ import annotations

from etl.shopee.transformer import ShopeeTransformer


def test_transform_empty() -> None:
    transformer = ShopeeTransformer()
    df = transformer.transform([])
    assert df.is_empty()


def test_transform_valid_rows() -> None:
    transformer = ShopeeTransformer()
    rows = [
        {
            "order_id": "ORD-001",
            "order_status": "Completed",
            "product_name": "Product A",
            "product_sku": "SKU-A",
            "variation": "Red",
            "quantity": 2,
            "price": "50000",
            "total_amount": "100000",
            "buyer_name": "Budi",
            "buyer_username": "budi01",
            "city": "Jakarta Pusat",
            "province": "DKI Jakarta",
            "shipping_provider": "JNE",
            "shipping_method": "REG",
            "shipping_cost": "10000",
            "payment_method": "Transfer Bank",
            "order_date": "2024-01-15 10:00:00",
            "payment_date": "2024-01-15 10:05:00",
            "shipping_date": "2024-01-15 12:00:00",
            "voucher_seller": "0",
            "voucher_shopee": "0",
            "cancellation_reason": "",
        },
    ]
    df = transformer.transform(rows)
    assert df.height == 1
    row = df.row(0, named=True)
    assert row["order_id"] == "ORD-001"
    assert row["order_status"] == "completed"
    assert row["city"] == "Jakarta Pusat"
    assert row["province"] == "DKI Jakarta"
    assert row["shipping_provider"] == "JNE"
    assert row["payment_method"] == "Transfer Bank"


def test_transform_city_alias() -> None:
    transformer = ShopeeTransformer()
    rows = [
        {
            "order_id": "ORD-001",
            "order_status": "completed",
            "product_name": "Product A",
            "quantity": 1,
            "total_amount": "50000",
            "buyer_username": "budi01",
            "city": "Jakpus",
            "province": "DKI Jakarta",
        },
    ]
    df = transformer.transform(rows)
    row = df.row(0, named=True)
    assert row["city"] == "Jakarta Pusat"


def test_transform_username_normalization() -> None:
    transformer = ShopeeTransformer()
    rows = [
        {
            "order_id": "ORD-001",
            "order_status": "completed",
            "product_name": "Product A",
            "quantity": 1,
            "total_amount": "50000",
            "buyer_username": "Buyer: budi01",
            "city": "Jakarta",
        },
    ]
    df = transformer.transform(rows)
    row = df.row(0, named=True)
    assert row["buyer_username"] == "budi01"
