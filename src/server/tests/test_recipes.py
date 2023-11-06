from server.tests.conftest import client
from server.tests.utils import get_token
from server.storage import models


def test_authentication():
    # Try without auth
    user_response = client.get("/api/users/me")
    assert user_response.status_code == 401
    # Get Token
    token_request = client.post(
        "/api/token",
        data="username=admin&password=admin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_request.status_code == 200
    token_request_data = token_request.json()
    token = token_request_data["access_token"]
    # Try with auth
    user_response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert user_response.status_code == 200
    user_response_data = user_response.json()
    assert user_response_data["username"] == "admin"
    assert user_response_data["role"] == "admin"


def test_create_recipes(db):
    pass


def test_list_recipes():
    admin_token = get_token("admin")
    response = client.get(
        "/api/recipes", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
