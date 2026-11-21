from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal

_CURRENCY_MAP = {
    "usd": "USD",
    "eur": "EUR",
    "gbp": "GBP",
    "cad": "CAD",
    "aud": "AUD",
    "jpy": "JPY",
    "inr": "INR",
    "sek": "SEK",
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
}


def normalize_price(raw_value: str | Decimal | float | None) -> Decimal:
    if raw_value is None:
        return Decimal(0)
    if isinstance(raw_value, Decimal):
        return raw_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if isinstance(raw_value, (int, float)):
        return Decimal(str(raw_value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    value = str(raw_value).strip()
    value = value.replace("$", "").replace("€", "").replace("£", "")
    value = value.replace(",", "") if "." in value else value.replace(",", ".")
    if value == "":
        return Decimal(0)
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def normalize_currency(currency: str | None) -> str:
    if not currency:
        return "USD"
    key = currency.strip().lower()
    if key in _CURRENCY_MAP:
        return _CURRENCY_MAP[key]
    code = re.sub(r"[^A-Za-z]", "", currency).upper()
    return code or "USD"


def calculate_percentage_difference(reference: Decimal, competitor: Decimal) -> Decimal:
    if reference == 0:
        return Decimal("0.00")
    diff = ((competitor - reference) / reference) * Decimal(100)
    return diff.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
