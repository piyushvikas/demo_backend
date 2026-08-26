from __future__ import annotations

from app.storage import products_repo


class ProductError(ValueError):
    pass


def create_product(name: str, price: float, stock: int) -> dict:
    if not name or not name.strip():
        raise ProductError("name is required")
    if price <= 0:
        raise ProductError("price must be positive")
    if stock < 0:
        raise ProductError("stock cannot be negative")
    return products_repo.create(name=name.strip(), price=round(price, 2), stock=stock)


def get_product(product_id: int) -> dict | None:
    return products_repo.get(product_id)


def list_products() -> list[dict]:
    return products_repo.list()


def update_stock(product_id: int, delta: int) -> dict:
    record = products_repo.get(product_id)
    if record is None:
        raise ProductError("product not found")
    new_stock = record["stock"] + delta
    if new_stock < 0:
        raise ProductError("insufficient stock")
    return products_repo.update(product_id, stock=new_stock)


def low_stock_products(threshold: int = 5) -> list[dict]:
    return [p for p in products_repo.list() if p["stock"] <= threshold]


def delete_product(product_id: int) -> bool:
    return products_repo.delete(product_id)
