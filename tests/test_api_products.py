def test_create_product_success(client):
    resp = client.post("/products", json={"name": "Widget", "price": 9.99, "stock": 100})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Widget"
    assert body["stock"] == 100


def test_create_product_invalid_price_returns_400(client):
    resp = client.post("/products", json={"name": "Widget", "price": -1, "stock": 10})
    assert resp.status_code == 400


def test_list_products_empty(client):
    resp = client.get("/products")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_products_after_create(client):
    client.post("/products", json={"name": "Widget", "price": 9.99, "stock": 10})
    client.post("/products", json={"name": "Gadget", "price": 19.99, "stock": 5})
    resp = client.get("/products")
    assert len(resp.json()) == 2


def test_get_product_not_found_returns_404(client):
    resp = client.get("/products/999")
    assert resp.status_code == 404


def test_get_product_found(client):
    created = client.post("/products", json={"name": "Widget", "price": 9.99, "stock": 10}).json()
    resp = client.get(f"/products/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Widget"


def test_adjust_stock_success(client):
    created = client.post("/products", json={"name": "Widget", "price": 9.99, "stock": 10}).json()
    resp = client.patch(f"/products/{created['id']}/stock", json={"delta": -3})
    assert resp.status_code == 200
    assert resp.json()["stock"] == 7


def test_adjust_stock_below_zero_returns_400(client):
    created = client.post("/products", json={"name": "Widget", "price": 9.99, "stock": 2}).json()
    resp = client.patch(f"/products/{created['id']}/stock", json={"delta": -5})
    assert resp.status_code == 400


def test_adjust_stock_not_found_returns_400(client):
    resp = client.patch("/products/999/stock", json={"delta": 1})
    assert resp.status_code == 400


def test_featured_products_empty(client):
    resp = client.get("/products/featured")
    assert resp.status_code == 200
    assert resp.json() == []


def test_featured_products_returns_at_most_three(client):
    for i in range(5):
        client.post("/products", json={"name": f"Product {i}", "price": 9.99, "stock": i})
    resp = client.get("/products/featured")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_featured_products_not_shadowed_by_product_id_route(client):
    # Regression guard: /products/featured must resolve before /products/{product_id}
    resp = client.get("/products/featured")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
