def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_register_success(client):
    resp = client.post(
        "/auth/register",
        json={"username": "johndoe", "email": "john@example.com", "password": "Str0ngPass!"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "johndoe"
    assert "id" in body


def test_register_invalid_email_returns_400(client):
    resp = client.post(
        "/auth/register",
        json={"username": "johndoe", "email": "not-an-email", "password": "Str0ngPass!"},
    )
    assert resp.status_code == 400


def test_register_duplicate_email_returns_400(client):
    payload = {"username": "johndoe", "email": "john@example.com", "password": "Str0ngPass!"}
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json={**payload, "username": "janedoe"})
    assert resp.status_code == 400


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"username": "johndoe", "email": "john@example.com", "password": "Str0ngPass!"},
    )
    resp = client.post("/auth/login", json={"email": "john@example.com", "password": "Str0ngPass!"})
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_login_wrong_password_returns_401(client):
    client.post(
        "/auth/register",
        json={"username": "johndoe", "email": "john@example.com", "password": "Str0ngPass!"},
    )
    resp = client.post("/auth/login", json={"email": "john@example.com", "password": "WrongPass!"})
    assert resp.status_code == 401


def test_get_user_not_found_returns_404(client):
    resp = client.get("/users/999")
    assert resp.status_code == 404


def test_get_user_found(client):
    created = client.post(
        "/auth/register",
        json={"username": "johndoe", "email": "john@example.com", "password": "Str0ngPass!"},
    ).json()
    resp = client.get(f"/users/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "john@example.com"


def test_list_users_empty(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    assert resp.json() == []


def test_delete_user_success(client):
    created = client.post(
        "/auth/register",
        json={"username": "johndoe", "email": "john@example.com", "password": "Str0ngPass!"},
    ).json()
    resp = client.delete(f"/users/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/users/{created['id']}").status_code == 404


def test_delete_user_not_found_returns_404(client):
    resp = client.delete("/users/999")
    assert resp.status_code == 404
