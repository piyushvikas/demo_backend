import pytest

from app.services.orders import OrderError, cancel_order, create_order, get_order, list_orders_for_user
from app.services.products import get_product
from app.services.products import create_product
from app.services.users import create_user


@pytest.fixture
def user():
    return create_user("johndoe", "john@example.com", "Str0ngPass!")


@pytest.fixture
def product():
    return create_product("Widget", 10.0, 20)


def test_create_order_success(user, product):
    order = create_order(user["id"], [{"product_id": product["id"], "quantity": 2}])
    assert order["status"] == "confirmed"
    assert order["subtotal"] == 20.0
    assert order["total"] > order["subtotal"]


def test_create_order_deducts_stock(user, product):
    create_order(user["id"], [{"product_id": product["id"], "quantity": 5}])
    assert get_product(product["id"])["stock"] == 15


def test_create_order_unknown_user_raises(product):
    with pytest.raises(OrderError):
        create_order(999, [{"product_id": product["id"], "quantity": 1}])


def test_create_order_empty_items_raises(user):
    with pytest.raises(OrderError):
        create_order(user["id"], [])


def test_create_order_unknown_product_raises(user):
    with pytest.raises(OrderError):
        create_order(user["id"], [{"product_id": 999, "quantity": 1}])


def test_create_order_zero_quantity_raises(user, product):
    with pytest.raises(OrderError):
        create_order(user["id"], [{"product_id": product["id"], "quantity": 0}])


def test_create_order_negative_quantity_raises(user, product):
    with pytest.raises(OrderError):
        create_order(user["id"], [{"product_id": product["id"], "quantity": -1}])


def test_create_order_insufficient_stock_raises(user, product):
    with pytest.raises(OrderError):
        create_order(user["id"], [{"product_id": product["id"], "quantity": 999}])


def test_create_order_insufficient_stock_does_not_partially_deduct(user, product):
    other = create_product("Gadget", 5.0, 1)
    with pytest.raises(OrderError):
        create_order(
            user["id"],
            [
                {"product_id": product["id"], "quantity": 2},
                {"product_id": other["id"], "quantity": 999},
            ],
        )
    # First item's stock must be untouched since the whole order failed validation
    assert get_product(product["id"])["stock"] == 20


def test_create_order_with_discount(user, product):
    order = create_order(user["id"], [{"product_id": product["id"], "quantity": 1}], discount_percent=50)
    assert order["discount"] == 5.0


def test_create_order_with_shipping(user, product):
    order = create_order(
        user["id"], [{"product_id": product["id"], "quantity": 1}], shipping_weight_kg=2
    )
    assert order["shipping"] == 9.99


def test_get_order_found(user, product):
    created = create_order(user["id"], [{"product_id": product["id"], "quantity": 1}])
    assert get_order(created["id"]) == created


def test_get_order_not_found():
    assert get_order(999) is None


def test_list_orders_for_user(user, product):
    create_order(user["id"], [{"product_id": product["id"], "quantity": 1}])
    create_order(user["id"], [{"product_id": product["id"], "quantity": 1}])
    assert len(list_orders_for_user(user["id"])) == 2


def test_list_orders_for_user_empty():
    assert list_orders_for_user(999) == []


def test_cancel_order_restores_stock(user, product):
    order = create_order(user["id"], [{"product_id": product["id"], "quantity": 5}])
    cancel_order(order["id"])
    assert get_product(product["id"])["stock"] == 20


def test_cancel_order_sets_status(user, product):
    order = create_order(user["id"], [{"product_id": product["id"], "quantity": 1}])
    cancelled = cancel_order(order["id"])
    assert cancelled["status"] == "cancelled"


def test_cancel_order_twice_raises(user, product):
    order = create_order(user["id"], [{"product_id": product["id"], "quantity": 1}])
    cancel_order(order["id"])
    with pytest.raises(OrderError):
        cancel_order(order["id"])


def test_cancel_order_not_found_raises():
    with pytest.raises(OrderError):
        cancel_order(999)


@pytest.mark.parametrize("quantity", [1, 2, 3, 4, 5])
def test_create_order_various_quantities(user, product, quantity):
    order = create_order(user["id"], [{"product_id": product["id"], "quantity": quantity}])
    assert order["subtotal"] == 10.0 * quantity
