from __future__ import annotations

from app.services import products as products_service
from app.storage import orders_repo, users_repo
from app.utils.pricing import calculate_order_total


class OrderError(ValueError):
    pass


def create_order(
    user_id: int,
    items: list[dict],
    discount_percent: float = 0,
    shipping_weight_kg: float = 0,
) -> dict:
    if users_repo.get(user_id) is None:
        raise OrderError("user not found")
    if not items:
        raise OrderError("order must contain at least one item")

    subtotal = 0.0
    for item in items:
        product = products_service.get_product(item["product_id"])
        if product is None:
            raise OrderError(f"product {item['product_id']} not found")
        quantity = item["quantity"]
        if quantity <= 0:
            raise OrderError("quantity must be positive")
        if product["stock"] < quantity:
            raise OrderError(f"insufficient stock for product {product['id']}")
        subtotal += product["price"] * quantity

    pricing = calculate_order_total(
        subtotal,
        discount_percent=discount_percent,
        shipping_weight_kg=shipping_weight_kg,
    )

    # Reserve stock only after all validation passed
    for item in items:
        products_service.update_stock(item["product_id"], -item["quantity"])

    return orders_repo.create(
        user_id=user_id,
        items=items,
        status="confirmed",
        **pricing,
    )


def get_order(order_id: int) -> dict | None:
    return orders_repo.get(order_id)


def list_orders_for_user(user_id: int) -> list[dict]:
    return [o for o in orders_repo.list() if o["user_id"] == user_id]


def cancel_order(order_id: int) -> dict:
    order = orders_repo.get(order_id)
    if order is None:
        raise OrderError("order not found")
    if order["status"] == "cancelled":
        raise OrderError("order already cancelled")

    for item in order["items"]:
        products_service.update_stock(item["product_id"], item["quantity"])

    return orders_repo.update(order_id, status="cancelled")


def apply_refund(order_id: int, amount: float, requesting_user_id: int) -> dict:
    order = orders_repo.get(order_id)
    if order is None:
        raise OrderError("order not found")
    if order["user_id"] != requesting_user_id:
        raise OrderError("not authorized to refund this order")
    if amount <= 0:
        raise OrderError("refund amount must be positive")

    already_refunded = order.get("refunded_amount", 0)
    remaining = order["total"] - already_refunded
    if amount > remaining:
        raise OrderError(f"refund amount exceeds remaining refundable total ({remaining})")

    return orders_repo.update(order_id, refunded_amount=already_refunded + amount)
