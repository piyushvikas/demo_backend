import pytest

from app.services.users import (
    UserError,
    authenticate,
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)


def test_create_user_success():
    user = create_user("johndoe", "john@example.com", "Str0ngPass!")
    assert user["username"] == "johndoe"
    assert user["email"] == "john@example.com"
    assert "password_hash" not in user
    assert "id" in user


def test_create_user_invalid_username_raises():
    with pytest.raises(UserError):
        create_user("j", "john@example.com", "Str0ngPass!")


def test_create_user_invalid_email_raises():
    with pytest.raises(UserError):
        create_user("johndoe", "not-an-email", "Str0ngPass!")


def test_create_user_weak_password_raises():
    with pytest.raises(UserError):
        create_user("johndoe", "john@example.com", "weak")


def test_create_user_duplicate_email_raises():
    create_user("johndoe", "john@example.com", "Str0ngPass!")
    with pytest.raises(UserError):
        create_user("janedoe", "john@example.com", "Str0ngPass!")


def test_get_user_found():
    created = create_user("johndoe", "john@example.com", "Str0ngPass!")
    fetched = get_user(created["id"])
    assert fetched == created


def test_get_user_not_found():
    assert get_user(999) is None


def test_list_users_empty():
    assert list_users() == []


def test_list_users_multiple():
    create_user("johndoe", "john@example.com", "Str0ngPass!")
    create_user("janedoe", "jane@example.com", "Str0ngPass!")
    assert len(list_users()) == 2


def test_update_user_username():
    created = create_user("johndoe", "john@example.com", "Str0ngPass!")
    updated = update_user(created["id"], username="johnny")
    assert updated["username"] == "johnny"


def test_update_user_invalid_email_raises():
    created = create_user("johndoe", "john@example.com", "Str0ngPass!")
    with pytest.raises(UserError):
        update_user(created["id"], email="bad-email")


def test_update_user_not_found_returns_none():
    assert update_user(999, username="ghost") is None


def test_delete_user_success():
    created = create_user("johndoe", "john@example.com", "Str0ngPass!")
    assert delete_user(created["id"]) is True
    assert get_user(created["id"]) is None


def test_delete_user_not_found():
    assert delete_user(999) is False


def test_authenticate_success():
    create_user("johndoe", "john@example.com", "Str0ngPass!")
    token = authenticate("john@example.com", "Str0ngPass!")
    assert isinstance(token, str) and len(token) > 0


def test_authenticate_wrong_password_raises():
    create_user("johndoe", "john@example.com", "Str0ngPass!")
    with pytest.raises(UserError):
        authenticate("john@example.com", "WrongPass!")


def test_authenticate_unknown_email_raises():
    with pytest.raises(UserError):
        authenticate("ghost@example.com", "whatever")
