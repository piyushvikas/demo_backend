import pytest

from app.services.products import (
    ProductError,
    create_product,
    delete_product,
    get_product,
    list_products,
    low_stock_products,
    update_stock,
)


def test_create_product_success():
    product = create_product("Widget", 9.99, 100)
    assert product["name"] == "Widget"
    assert product["price"] == 9.99
    assert product["stock"] == 100


def test_create_product_strips_name():
    product = create_product("  Widget  ", 9.99, 10)
    assert product["name"] == "Widget"


@pytest.mark.parametrize("name", ["", "   "])
def test_create_product_empty_name_raises(name):
    with pytest.raises(ProductError):
        create_product(name, 9.99, 10)


@pytest.mark.parametrize("price", [0, -5, -0.01])
def test_create_product_non_positive_price_raises(price):
    with pytest.raises(ProductError):
        create_product("Widget", price, 10)


def test_create_product_negative_stock_raises():
    with pytest.raises(ProductError):
        create_product("Widget", 9.99, -1)


def test_get_product_found():
    created = create_product("Widget", 9.99, 10)
    assert get_product(created["id"]) == created


def test_get_product_not_found():
    assert get_product(999) is None


def test_list_products_empty():
    assert list_products() == []


def test_list_products_multiple():
    create_product("Widget", 9.99, 10)
    create_product("Gadget", 19.99, 5)
    assert len(list_products()) == 2


def test_update_stock_increase():
    created = create_product("Widget", 9.99, 10)
    updated = update_stock(created["id"], 5)
    assert updated["stock"] == 15


def test_update_stock_decrease():
    created = create_product("Widget", 9.99, 10)
    updated = update_stock(created["id"], -3)
    assert updated["stock"] == 7


def test_update_stock_below_zero_raises():
    created = create_product("Widget", 9.99, 5)
    with pytest.raises(ProductError):
        update_stock(created["id"], -10)


def test_update_stock_not_found_raises():
    with pytest.raises(ProductError):
        update_stock(999, 5)


def test_low_stock_products_default_threshold():
    create_product("Widget", 9.99, 3)
    create_product("Gadget", 19.99, 50)
    low = low_stock_products()
    assert len(low) == 1
    assert low[0]["name"] == "Widget"


def test_low_stock_products_custom_threshold():
    create_product("Widget", 9.99, 10)
    low = low_stock_products(threshold=20)
    assert len(low) == 1


def test_delete_product_success():
    created = create_product("Widget", 9.99, 10)
    assert delete_product(created["id"]) is True
    assert get_product(created["id"]) is None


def test_delete_product_not_found():
    assert delete_product(999) is False
