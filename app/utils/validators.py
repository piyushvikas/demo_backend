"""Small, dependency-free validation helpers."""

from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
_PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")
_USERNAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{2,19}$")


def is_valid_email(email: str) -> bool:
    if not email or len(email) > 254:
        return False
    return bool(_EMAIL_RE.match(email))


def is_valid_phone(phone: str) -> bool:
    if not phone:
        return False
    return bool(_PHONE_RE.match(phone))


def is_valid_username(username: str) -> bool:
    if not username:
        return False
    return bool(_USERNAME_RE.match(username))


def password_strength(password: str) -> str:
    """Return 'weak', 'medium', or 'strong'."""
    if not password or len(password) < 6:
        return "weak"

    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)
    classes = sum([has_lower, has_upper, has_digit, has_symbol])

    if len(password) >= 10 and classes >= 3:
        return "strong"
    if len(password) >= 8 and classes >= 2:
        return "medium"
    return "weak"


def is_strong_enough(password: str, minimum: str = "medium") -> bool:
    order = {"weak": 0, "medium": 1, "strong": 2}
    return order[password_strength(password)] >= order[minimum]


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Trim whitespace and cap length. Not a security control, just hygiene."""
    if value is None:
        return ""
    return value.strip()[:max_length]
