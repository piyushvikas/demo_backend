import pytest

from app.utils.validators import (
    is_strong_enough,
    is_valid_email,
    is_valid_phone,
    is_valid_username,
    password_strength,
    sanitize_string,
)


@pytest.mark.parametrize(
    "email,expected",
    [
        ("a@b.com", True),
        ("john.doe@example.co.uk", True),
        ("first+tag@example.com", True),
        ("a@b.io", True),
        ("no-at-sign.com", False),
        ("missing@domain", False),
        ("@nouser.com", False),
        ("spaces in@email.com", False),
        ("", False),
        (None, False),
    ],
)
def test_is_valid_email(email, expected):
    assert is_valid_email(email) == expected


def test_is_valid_email_rejects_overlong():
    assert is_valid_email("a" * 250 + "@b.com") is False


@pytest.mark.parametrize(
    "phone,expected",
    [
        ("1234567890", True),
        ("+11234567890", True),
        ("123456789012345", True),
        ("12345", False),
        ("abcdefghij", False),
        ("", False),
        ("1234567890123456", False),
    ],
)
def test_is_valid_phone(phone, expected):
    assert is_valid_phone(phone) == expected


@pytest.mark.parametrize(
    "username,expected",
    [
        ("john", True),
        ("john_doe123", True),
        ("j12", True),
        ("jo", False),  # too short
        ("1john", False),  # can't start with digit
        ("john doe", False),  # space
        ("", False),
        ("a" * 21, False),  # too long
    ],
)
def test_is_valid_username(username, expected):
    assert is_valid_username(username) == expected


@pytest.mark.parametrize(
    "password,expected",
    [
        ("abc", "weak"),
        ("abcdef", "weak"),
        ("abcdefgh", "weak"),
        ("abcdefgH", "medium"),
        ("abcdefgH1", "medium"),
        ("Abcdefgh12", "strong"),
        ("Abcdefgh12!", "strong"),
    ],
)
def test_password_strength(password, expected):
    assert password_strength(password) == expected


def test_is_strong_enough_default_medium():
    assert is_strong_enough("abcdefgH1") is True
    assert is_strong_enough("abc") is False


def test_is_strong_enough_custom_minimum():
    assert is_strong_enough("abcdefgH1", minimum="strong") is False
    assert is_strong_enough("Abcdefgh12!", minimum="strong") is True


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  hello  ", "hello"),
        ("no-trim-needed", "no-trim-needed"),
        (None, ""),
        ("", ""),
    ],
)
def test_sanitize_string(raw, expected):
    assert sanitize_string(raw) == expected


def test_sanitize_string_truncates():
    assert sanitize_string("x" * 300, max_length=10) == "x" * 10
