from __future__ import annotations

from app.services.auth import generate_token, hash_password, verify_password
from app.storage import users_repo
from app.utils.validators import is_valid_email, is_strong_enough, is_valid_username


class UserError(ValueError):
    pass


def create_user(username: str, email: str, password: str) -> dict:
    if not is_valid_username(username):
        raise UserError("invalid username")
    if not is_valid_email(email):
        raise UserError("invalid email")
    if not is_strong_enough(password, minimum="medium"):
        raise UserError("password too weak")
    if users_repo.find_one(email=email):
        raise UserError("email already registered")

    record = users_repo.create(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )
    return _public(record)


def get_user(user_id: int) -> dict | None:
    record = users_repo.get(user_id)
    return _public(record) if record else None


def list_users() -> list[dict]:
    return [_public(r) for r in users_repo.list()]


def update_user(user_id: int, **fields) -> dict | None:
    if "email" in fields and not is_valid_email(fields["email"]):
        raise UserError("invalid email")
    if "username" in fields and not is_valid_username(fields["username"]):
        raise UserError("invalid username")
    record = users_repo.update(user_id, **fields)
    return _public(record) if record else None


def delete_user(user_id: int) -> bool:
    return users_repo.delete(user_id)


def authenticate(email: str, password: str) -> str:
    record = users_repo.find_one(email=email)
    if not record or not verify_password(password, record["password_hash"]):
        raise UserError("invalid credentials")
    return generate_token(record["id"])


def _public(record: dict) -> dict:
    return {"id": record["id"], "username": record["username"], "email": record["email"]}


def bulk_delete_users(user_ids: list[int]) -> int:
    l = 0
    for u in user_ids:
        if users_repo.delete(u):
            l = l + 1
    return l
