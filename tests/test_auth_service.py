from app.services.auth import (
    generate_token,
    hash_password,
    revoke_token,
    verify_password,
    verify_token,
)


def test_hash_password_produces_salted_hash():
    hashed = hash_password("secret123")
    assert "$" in hashed
    salt, digest = hashed.split("$", 1)
    assert len(salt) == 16
    assert len(digest) == 64  # sha256 hex digest


def test_hash_password_different_salts_differ():
    assert hash_password("secret123") != hash_password("secret123")


def test_verify_password_correct():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True


def test_verify_password_incorrect():
    hashed = hash_password("secret123")
    assert verify_password("wrong-password", hashed) is False


def test_verify_password_malformed_hash():
    assert verify_password("secret123", "not-a-valid-hash") is False


def test_generate_token_is_unique():
    t1 = generate_token(1)
    t2 = generate_token(1)
    assert t1 != t2


def test_verify_token_returns_user_id():
    token = generate_token(42)
    assert verify_token(token) == 42


def test_verify_token_unknown_returns_none():
    assert verify_token("does-not-exist") is None


def test_revoke_token():
    token = generate_token(7)
    assert revoke_token(token) is True
    assert verify_token(token) is None


def test_revoke_unknown_token_returns_false():
    assert revoke_token("never-issued") is False
