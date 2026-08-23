from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_create_merchant():
    response = client.post(
        "/merchants",
        json={
            "name": "API Merchant",
            "slug": f"api-merchant-{uuid4().hex[:8]}",
            "email": "api@example.com",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "API Merchant"
    assert data["email"] == "api@example.com"
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data


def test_create_merchant_invalid_email():
    response = client.post(
        "/merchants",
        json={
            "name": "Invalid Merchant",
            "slug": f"invalid-{uuid4().hex[:8]}",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422


def test_create_duplicate_merchant_slug():
    slug = f"duplicate-{uuid4().hex[:8]}"

    payload = {
        "name": "First Merchant",
        "slug": slug,
        "email": "first@example.com",
    }

    first_response = client.post(
        "/merchants",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/merchants",
        json={
            "name": "Second Merchant",
            "slug": slug,
            "email": "second@example.com",
        },
    )

    assert second_response.status_code == 409


def test_get_merchant():
    create_response = client.post(
        "/merchants",
        json={
            "name": "Get Merchant",
            "slug": f"get-{uuid4().hex[:8]}",
            "email": "get@example.com",
        },
    )

    assert create_response.status_code == 201

    merchant_id = create_response.json()["id"]

    response = client.get(
        f"/merchants/{merchant_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == merchant_id
    assert data["name"] == "Get Merchant"


def test_get_missing_merchant():
    merchant_id = uuid4()

    response = client.get(
        f"/merchants/{merchant_id}"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Merchant not found"


def test_get_merchant_invalid_uuid():
    response = client.get(
        "/merchants/not-a-valid-uuid"
    )

    assert response.status_code == 422


def test_list_merchants():
    response = client.get(
        "/merchants"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_list_merchants_pagination():
    response = client.get(
        "/merchants?skip=0&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 10


def test_update_merchant():
    create_response = client.post(
        "/merchants",
        json={
            "name": "Before Update",
            "slug": f"update-{uuid4().hex[:8]}",
            "email": "before@example.com",
        },
    )

    assert create_response.status_code == 201

    merchant_id = create_response.json()["id"]

    response = client.patch(
        f"/merchants/{merchant_id}",
        json={
            "name": "After Update",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == merchant_id
    assert data["name"] == "After Update"


def test_update_missing_merchant():
    merchant_id = uuid4()

    response = client.patch(
        f"/merchants/{merchant_id}",
        json={
            "name": "Does Not Exist",
        },
    )

    assert response.status_code == 404


def test_update_duplicate_slug():
    slug_a = f"merchant-a-{uuid4().hex[:8]}"
    slug_b = f"merchant-b-{uuid4().hex[:8]}"

    first = client.post(
        "/merchants",
        json={
            "name": "Merchant A",
            "slug": slug_a,
            "email": "a@example.com",
        },
    )

    second = client.post(
        "/merchants",
        json={
            "name": "Merchant B",
            "slug": slug_b,
            "email": "b@example.com",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    merchant_b_id = second.json()["id"]

    response = client.patch(
        f"/merchants/{merchant_b_id}",
        json={
            "slug": slug_a,
        },
    )

    assert response.status_code == 409


def test_delete_merchant():
    create_response = client.post(
        "/merchants",
        json={
            "name": "Delete Merchant",
            "slug": f"delete-{uuid4().hex[:8]}",
            "email": "delete@example.com",
        },
    )

    assert create_response.status_code == 201

    merchant_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/merchants/{merchant_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/merchants/{merchant_id}"
    )

    assert get_response.status_code == 404


def test_delete_missing_merchant():
    merchant_id = uuid4()

    response = client.delete(
        f"/merchants/{merchant_id}"
    )

    assert response.status_code == 404