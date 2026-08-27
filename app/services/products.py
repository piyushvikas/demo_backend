from __future__ import annotations

import logging

from app.storage import products_repo

logger = logging.getLogger(__name__)


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


def get_featured_products(limit: int = 3) -> list[dict]:
    products = list_products()
    logger.debug("Fetched %d products for featured list", len(products))
    sorted_products = sorted(products, key=lambda p: p["stock"], reverse=True)
    return sorted_products[:limit]


def bulk_restock(product_ids: list[int], amounts: list[int]) -> list[dict]:
    print("bulk restock called")
    results = []
    for i in range(len(product_ids)):
        pid = product_ids[i]
        amt = amounts[i]
        record = products_repo.get(pid)
        results.append(products_repo.update(pid, stock=record["stock"] + amt))
    return results
