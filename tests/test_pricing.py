import pytest

from app.utils.pricing import (
    apply_discount,
    calculate_bulk_discount_percent,
    calculate_discount,
    calculate_order_total,
    calculate_shipping,
    calculate_tax,
)


@pytest.mark.parametrize(
    "amount,rate,expected",
    [
        (100, 0.08, 8.0),
        (0, 0.08, 0.0),
        (50, 0.1, 5.0),
        (99.99, 0.08, 8.0),
    ],
)
def test_calculate_tax(amount, rate, expected):
    assert calculate_tax(amount, rate) == expected


def test_calculate_tax_negative_amount_raises():
    with pytest.raises(ValueError):
        calculate_tax(-1)


def test_calculate_tax_negative_rate_raises():
    with pytest.raises(ValueError):
        calculate_tax(10, rate=-0.1)


@pytest.mark.parametrize(
    "amount,percent,expected",
    [
        (100, 10, 10.0),
        (100, 0, 0.0),
        (100, 100, 100.0),
        (50, 50, 25.0),
    ],
)
def test_calculate_discount(amount, percent, expected):
    assert calculate_discount(amount, percent) == expected


@pytest.mark.parametrize("percent", [-1, 101, 150])
def test_calculate_discount_invalid_percent_raises(percent):
    with pytest.raises(ValueError):
        calculate_discount(100, percent)


def test_calculate_discount_negative_amount_raises():
    with pytest.raises(ValueError):
        calculate_discount(-10, 10)


@pytest.mark.parametrize(
    "amount,percent,expected",
    [
        (100, 10, 90.0),
        (100, 0, 100.0),
        (200, 25, 150.0),
    ],
)
def test_apply_discount(amount, percent, expected):
    assert apply_discount(amount, percent) == expected


@pytest.mark.parametrize(
    "weight,expected",
    [
        (0, 0.0),
        (0.5, 4.99),
        (1, 4.99),
        (1.01, 9.99),
        (5, 9.99),
        (5.5, 19.99),
        (20, 19.99),
        (20.1, 39.99),
        (100, 39.99),
    ],
)
def test_calculate_shipping(weight, expected):
    assert calculate_shipping(weight) == expected


def test_calculate_shipping_negative_raises():
    with pytest.raises(ValueError):
        calculate_shipping(-1)


@pytest.mark.parametrize(
    "quantity,expected",
    [
        (0, 0.0),
        (5, 0.0),
        (9, 0.0),
        (10, 5.0),
        (19, 5.0),
        (20, 10.0),
        (49, 10.0),
        (50, 15.0),
        (99, 15.0),
        (100, 20.0),
        (500, 20.0),
    ],
)
def test_calculate_bulk_discount_percent(quantity, expected):
    assert calculate_bulk_discount_percent(quantity) == expected


def test_calculate_bulk_discount_percent_negative_raises():
    with pytest.raises(ValueError):
        calculate_bulk_discount_percent(-1)


def test_calculate_order_total_basic():
    result = calculate_order_total(100, discount_percent=10, tax_rate=0.08, shipping_weight_kg=0.5)
    assert result["subtotal"] == 100
    assert result["discount"] == 10.0
    assert result["shipping"] == 4.99
    # discounted = 90, tax = 90*0.08 = 7.2, total = 90+7.2+4.99
    assert result["tax"] == 7.2
    assert result["total"] == pytest.approx(102.19, abs=0.01)


def test_calculate_order_total_no_discount_no_shipping():
    result = calculate_order_total(50)
    assert result["discount"] == 0.0
    assert result["shipping"] == 0.0
    assert result["total"] == pytest.approx(54.0, abs=0.01)


def test_calculate_order_total_negative_subtotal_raises():
    with pytest.raises(ValueError):
        calculate_order_total(-10)


@pytest.mark.parametrize("discount", [0, 25, 50, 75, 100])
def test_calculate_order_total_various_discounts(discount):
    result = calculate_order_total(200, discount_percent=discount)
    assert result["total"] >= 0
