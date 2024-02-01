import pytest
import json

from base64 import b64decode

from server.tests.utils import get_token
from server.storage import models
from server.routes.users import (
    authenticate_user,
    AuthenticationException,
)


def test_authenticate_user(db):
    # Valid credentials
    admin = db.query(models.User).filter_by(username="admin").one_or_none()
    response = authenticate_user(db, "admin", "admin")
    assert response == admin

    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    response = authenticate_user(db, "user_1", "user_1")
    assert response == user_1

    user_2 = db.query(models.User).filter_by(username="user_2").one_or_none()
    response = authenticate_user(db, "user_2", "user_2")
    assert response == user_2

    # Invalid username
    with pytest.raises(AuthenticationException, match=".*doesn't exist"):
        authenticate_user(db, "user_3", "user_3")

    # Invalid password
    with pytest.raises(AuthenticationException, match="Incorrect password.*"):
        authenticate_user(db, "user_1", "wrongpassword")


def test_create_token(client):
    # Valid credentials
    response = client.post(
        "/api/token", data={"username": "user_1", "password": "user_1"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"

    header, claims, _ = data["access_token"].split(".")

    header = json.loads(b64decode(header))
    assert header["alg"] == "HS256"
    assert header["typ"] == "JWT"

    claims = json.loads(b64decode(claims))
    assert claims["sub"] == "user_1"

    # Invalid username
    response = client.post(
        "/api/token", data={"username": "user_3", "password": "user_1"}
    )
    assert response.status_code == 401

    data = response.json()
    assert data["detail"] == "Incorrect username or password"

    # Invalid password
    response = client.post(
        "/api/token", data={"username": "user_1", "password": "user_3"}
    )
    assert response.status_code == 401

    data = response.json()
    assert data["detail"] == "Incorrect username or password"


def test_create_user(client):
    # Required fields included
    response = client.post(
        "/api/users",
        json={"username": "user_3", "password": "user_3"},
    )
    assert response.status_code == 200

    user_3 = response.json()
    assert user_3["username"] == "user_3"
    assert user_3["role"] == "user"

    # Required fields excluded
    response = client.post(
        "/api/users",
        json={"username": "user_3"},
    )
    assert response.status_code == 422

    # Invalid type for username field
    response = client.post(
        "/api/users",
        json={"username": 3, "password": "user_3"},
    )
    assert response.status_code == 422

    # Username already exists
    response = client.post(
        "/api/users",
        json={"username": "user_1", "password": "user_3"},
    )
    assert response.status_code == 400

    data = response.json()
    assert data["detail"] == "Username 'user_1' already taken"


def test_list_users(client):
    # Test as admin
    admin_token = get_token("admin")
    response = client.get(
        "/api/users", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3

    # Test that users are sorted alphabetically by username
    assert data["items"][0]["username"] == "admin"
    assert data["items"][1]["username"] == "user_1"
    assert data["items"][2]["username"] == "user_2"

    # Test as user
    user_1_token = get_token("user_1")
    response = client.get(
        "/api/users", headers={"Authorization": f"Bearer {user_1_token}"}
    )
    assert response.status_code == 403

    data = response.json()
    assert data["detail"] == "Only admins can list users"

    # Test filtering by params
    admin_token = get_token("admin")
    response = client.get(
        "/api/users",
        params={"role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 2
    for user in data["items"]:
        assert user["role"] == "user"


def test_get_user_self(db, client):
    # Test admin
    admin_token = get_token("admin")
    admin = db.query(models.User).filter_by(username="admin").one_or_none()

    response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == admin.id
    assert data["username"] == admin.username
    assert data["role"] == admin.role

    # Test user_1
    user_1_token = get_token("user_1")
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()

    response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {user_1_token}"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_1.id
    assert data["username"] == user_1.username
    assert data["role"] == user_1.role

    # Test user_2
    user_2_token = get_token("user_2")
    user_2 = db.query(models.User).filter_by(username="user_2").one_or_none()

    response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {user_2_token}"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_2.id
    assert data["username"] == user_2.username
    assert data["role"] == user_2.role


def test_update_user(db, client):
    # Test updating password for same user as requester
    user_1_token = get_token("user_1")
    original_user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()

    response = client.put(
        f"/api/users/{original_user_1.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"password": "new_user_1_password"},
    )
    assert response.status_code == 200

    new_user_1 = response.json()
    assert new_user_1["id"] == original_user_1.id
    response = client.post(
        "/api/token", data={"username": "user_1", "password": "new_user_1_password"}
    )
    assert response.status_code == 200

    # Test updating password for different user than requester
    user_2_token = get_token("user_2")
    response = client.put(
        f"/api/users/{original_user_1.id}",
        headers={"Authorization": f"Bearer {user_2_token}"},
        json={"password": "new_user_1_password"},
    )
    assert response.status_code == 403

    data = response.json()
    assert data["detail"] == "Passwords can only be updated for same user as requester"

    # Test updating role as admin
    admin_token = get_token("admin")
    original_user_2 = db.query(models.User).filter_by(username="user_2").one_or_none()

    response = client.put(
        f"/api/users/{original_user_2.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "admin"},
    )
    assert response.status_code == 200

    new_user_2 = response.json()
    assert new_user_2["id"] == original_user_2.id
    assert new_user_2["role"] == "admin"

    user_2_token = get_token("user_2")
    response = client.put(
        f"/api/users/{original_user_2.id}",
        headers={"Authorization": f"Bearer {user_2_token}"},
        json={"role": "user"},
    )
    assert response.status_code == 200

    new_new_user_2 = response.json()
    assert new_new_user_2["id"] == original_user_2.id
    assert new_new_user_2["role"] == "user"

    # Test updating role as user
    response = client.put(
        f"/api/users/{original_user_1.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"role": "admin"},
    )
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Roles can only be updated by admin users"
