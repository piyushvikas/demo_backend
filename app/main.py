from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.models import (
    LoginRequest,
    OrderCreate,
    ProductCreate,
    ResetPasswordRequest,
    StockAdjustment,
    UserCreate,
)
from app.services import orders as orders_service
from app.services import products as products_service
from app.services import users as users_service
from app.services.orders import OrderError
from app.services.products import ProductError
from app.services.users import UserError

app = FastAPI(title="Demo Backend")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# ── Auth / Users ────────────────────────────────────────────────────

@app.post("/auth/register", status_code=201)
def register(payload: UserCreate) -> dict:
    try:
        return users_service.create_user(payload.username, payload.email, payload.password)
    except UserError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login")
def login(payload: LoginRequest) -> dict:
    try:
        token = users_service.authenticate(payload.email, payload.password)
        return {"token": token}
    except UserError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/users")
def list_users() -> list[dict]:
    return users_service.list_users()


@app.get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    user = users_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int) -> None:
    if not users_service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="user not found")


@app.post("/users/{user_id}/reset-password")
def reset_password(user_id: int, payload: ResetPasswordRequest) -> dict:
    try:
        return users_service.reset_password(user_id, payload.new_password)
    except UserError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Products ─────────────────────────────────────────────────────────

@app.post("/products", status_code=201)
def create_product(payload: ProductCreate) -> dict:
    try:
        return products_service.create_product(payload.name, payload.price, payload.stock)
    except ProductError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/products")
def list_products() -> list[dict]:
    return products_service.list_products()


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict:
    product = products_service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")
    return product


@app.patch("/products/{product_id}/stock")
def adjust_stock(product_id: int, payload: StockAdjustment) -> dict:
    try:
        return products_service.update_stock(product_id, payload.delta)
    except ProductError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Orders ───────────────────────────────────────────────────────────

@app.post("/orders", status_code=201)
def create_order(payload: OrderCreate) -> dict:
    try:
        return orders_service.create_order(
            payload.user_id,
            [item.model_dump() for item in payload.items],
            discount_percent=payload.discount_percent,
            shipping_weight_kg=payload.shipping_weight_kg,
        )
    except OrderError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/{order_id}")
def get_order(order_id: int) -> dict:
    order = orders_service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int) -> dict:
    try:
        return orders_service.cancel_order(order_id)
    except OrderError as e:
        raise HTTPException(status_code=400, detail=str(e))
