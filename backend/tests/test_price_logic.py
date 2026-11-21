from __future__ import annotations

from decimal import Decimal

from app.analytics.pricing import (
    calculate_percentage_difference,
    normalize_currency,
    normalize_price,
)


def test_normalize_price_standard() -> None:
    assert normalize_price("$129.99") == Decimal("129.99")
    assert normalize_price("129,99") == Decimal("129.99")
    assert normalize_price(149.50) == Decimal("149.50")
    assert normalize_price(Decimal("49.99")) == Decimal("49.99")


def test_normalize_price_edge_cases() -> None:
    assert normalize_price(None) == Decimal("0.00")
    assert normalize_price("") == Decimal("0.00")
    assert normalize_price("$ 1,299.99") == Decimal("1299.99")
    assert normalize_price("€450.00") == Decimal("450.00")
    assert normalize_price("£89.95") == Decimal("89.95")


def test_normalize_currency() -> None:
    assert normalize_currency("usd") == "USD"
    assert normalize_currency("EUR") == "EUR"
    assert normalize_currency("$") == "USD"
    assert normalize_currency("€") == "EUR"
    assert normalize_currency("£") == "GBP"
    assert normalize_currency(None) == "USD"
    assert normalize_currency("") == "USD"


def test_calculate_percentage_difference() -> None:
    # Competitor is 80, reference is 100 -> -20%
    assert calculate_percentage_difference(Decimal(100), Decimal(80)) == Decimal("-20.00")
    # Competitor is 125, reference is 100 -> +25%
    assert calculate_percentage_difference(Decimal(100), Decimal(125)) == Decimal("25.00")
    # Reference is 0 -> 0%
    assert calculate_percentage_difference(Decimal(0), Decimal(100)) == Decimal("0.00")
