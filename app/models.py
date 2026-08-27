from __future__ import annotations

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int = 0


class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    stock: int


class StockAdjustment(BaseModel):
    delta: int


class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    user_id: int
    items: list[OrderItem]
    discount_percent: float = 0
    shipping_weight_kg: float = 0


class BulkRestockRequest(BaseModel):
    product_ids: list[int]
    amounts: list[int]


class BulkDeleteUsersRequest(BaseModel):
    user_ids: list[int]
