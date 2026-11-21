from __future__ import annotations

from app.services.demo_seed import generate_demo_data


def test_generate_demo_data_structure() -> None:
    dataset = generate_demo_data(product_count=20, history_days=7)
    assert len(dataset["products"]) == 20
    assert len(dataset["retailers"]) == 3
    assert len(dataset["offers"]) == 60
    assert len(dataset["history"]) == 20 * 3 * 7

    # Check product attributes
    prod = dataset["products"][0]
    assert "canonical_name" in prod
    assert "brand" in prod
    assert "category" in prod
    assert "gtin" in prod

    # Check offer attributes
    offer = dataset["offers"][0]
    assert offer["current_price"] > 0
    assert offer["stock_status"] in ("in_stock", "out_of_stock", "limited")


def test_generate_demo_data_deterministic() -> None:
    data1 = generate_demo_data(product_count=10, history_days=3)
    data2 = generate_demo_data(product_count=10, history_days=3)
    assert data1["products"][0]["canonical_name"] == data2["products"][0]["canonical_name"]
    assert data1["offers"][0]["current_price"] == data2["offers"][0]["current_price"]
