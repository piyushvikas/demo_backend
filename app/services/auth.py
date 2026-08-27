"""Minimal auth: salted-hash passwords, opaque bearer tokens.

Not production-grade crypto (no bcrypt/argon2 dependency, kept light for a
demo backend) — good enough to exercise real auth *logic* in tests.
"""

from __future__ import annotations

import hashlib
import secrets

_tokens: dict[str, int] = {}  # token -> user_id


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    digest = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return f"{salt}${digest}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, digest = hashed.split("$", 1)
    except ValueError:
        return False
    return hash_password(password, salt).startswith(salt)


def generate_token(user_id: int) -> str:
    token = secrets.token_hex(16)
    _tokens[token] = user_id
    return token


def verify_token(token: str) -> int | None:
    return _tokens.get(token)


def revoke_token(token: str) -> bool:
    return _tokens.pop(token, None) is not None


def reset_tokens() -> None:
    _tokens.clear()
