"""Order pricing math — tax, discounts, shipping tiers."""

from __future__ import annotations


def calculate_tax(amount: float, rate: float = 0.08) -> float:
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if rate < 0:
        raise ValueError("rate must be non-negative")
    return round(amount * rate, 2)


def calculate_discount(amount: float, percent: float) -> float:
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(amount * (percent / 100), 2)


def apply_discount(amount: float, percent: float) -> float:
    return round(amount - calculate_discount(amount, percent), 2)


def calculate_shipping(weight_kg: float) -> float:
    """Tiered flat-rate shipping."""
    if weight_kg < 0:
        raise ValueError("weight_kg must be non-negative")
    if weight_kg == 0:
        return 0.0
    if weight_kg <= 1:
        return 4.99
    if weight_kg <= 5:
        return 9.99
    if weight_kg <= 20:
        return 19.99
    return 39.99


def calculate_order_total(
    subtotal: float,
    discount_percent: float = 0,
    tax_rate: float = 0.08,
    shipping_weight_kg: float = 0,
) -> dict[str, float]:
    if subtotal < 0:
        raise ValueError("subtotal must be non-negative")

    discounted = apply_discount(subtotal, discount_percent)
    tax = calculate_tax(discounted, tax_rate)
    shipping = calculate_shipping(shipping_weight_kg)
    total = round(discounted + tax + shipping, 2)

    return {
        "subtotal": round(subtotal, 2),
        "discount": calculate_discount(subtotal, discount_percent),
        "tax": tax,
        "shipping": shipping,
        "total": total,
    }
