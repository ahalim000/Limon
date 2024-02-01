from datetime import datetime, timedelta

from server.tests.utils import get_token
from server.storage import models


def test_create_grocery_lists(db, client):
    # Test when there is an existing grocery list
    user_1_token = get_token("user_1")

    start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
    end_date = datetime.utcnow().isoformat()
    response = client.post(
        "/api/grocery_lists",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    assert response.status_code == 400

    data = response.json()
    assert data["detail"]["message"] == "Only one grocery list can exist at a time"

    # Minimal fields
    user_2_token = get_token("user_2")
    user_2 = db.query(models.User).filter_by(username="user_2").one_or_none()

    start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
    end_date = datetime.utcnow().isoformat()
    response = client.post(
        "/api/grocery_lists",
        headers={"Authorization": f"Bearer {user_2_token}"},
        json={
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    assert response.status_code == 200

    grocery_list = response.json()
    assert grocery_list["extra_items"] == ""
    assert grocery_list["user_id"] == user_2.id

    grocery_list_items = grocery_list["grocery_list_items"]
    assert len(grocery_list_items) == 50

    gl = db.query(models.GroceryList).filter_by(id=grocery_list["id"]).one()
    db.delete(gl)
    db.flush()

    # All fields
    start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
    end_date = datetime.utcnow().isoformat()
    response = client.post(
        "/api/grocery_lists",
        headers={"Authorization": f"Bearer {user_2_token}"},
        json={
            "start_date": start_date,
            "end_date": end_date,
            "extra_items": "Extra Item 1\nExtra Item 2\nExtra Item 3",
        },
    )
    assert response.status_code == 200

    grocery_list = response.json()
    assert grocery_list["extra_items"] == "Extra Item 1\nExtra Item 2\nExtra Item 3"
    assert grocery_list["user_id"] == user_2.id

    grocery_list_items = grocery_list["grocery_list_items"]
    assert len(grocery_list_items) == 53

    gl = db.query(models.GroceryList).filter_by(id=grocery_list["id"]).one()
    db.delete(gl)
    db.flush()


def test_get_grocery_list(db, client):
    # Test when grocery list exists
    user_1_token = get_token("user_1")

    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    gl = db.query(models.GroceryList).filter_by(user_id=user_1.id).one_or_none()

    response = client.get(
        f"/api/grocery_lists/{gl.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
    )
    assert response.status_code == 200

    grocery_list = response.json()
    assert grocery_list["id"] == gl.id
    assert grocery_list["extra_items"] == gl.extra_items
    assert grocery_list["user_id"] == gl.user_id
    assert grocery_list["grocery_list_items"] == gl.grocery_list_items

    # Test when grocery list doesn't exist
    user_2_token = get_token("user_2")

    response = client.get(
        "/api/grocery_lists/1",
        headers={"Authorization": f"Bearer {user_2_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Grocery List with ID 1 does not exist"


def test_update_grocery_list(db, client):
    # Update extra items to new ones
    user_1_token = get_token("user_1")

    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    gl = db.query(models.GroceryList).filter_by(user_id=user_1.id).one_or_none()

    response = client.put(
        f"/api/grocery_lists/{gl.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"extra_items": "Item 3\nItem 4"},
    )
    assert response.status_code == 200

    grocery_list = response.json()
    assert grocery_list["id"] == gl.id
    assert grocery_list["user_id"] == gl.user_id
    assert grocery_list["extra_items"] == "Item 3\nItem 4"
    assert len(grocery_list["grocery_list_items"]) == 2
    for grocery_list_item in grocery_list["grocery_list_items"]:
        assert (
            grocery_list_item["name"] == "Item 3"
            or grocery_list_item["name"] == "Item 4"
        )
        assert grocery_list_item["extra_items"] == True

    # Get rid of extra items
    response = client.put(
        f"/api/grocery_lists/{gl.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"extra_items": ""},
    )
    assert response.status_code == 200

    grocery_list = response.json()
    assert grocery_list["id"] == gl.id
    assert grocery_list["user_id"] == gl.user_id
    assert grocery_list["extra_items"] == ""
    assert len(grocery_list["grocery_list_items"]) == 0

    # Wrong type for extra items
    response = client.put(
        f"/api/grocery_lists/{gl.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"extra_items": []},
    )
    assert response.status_code == 422

    # Invalid grocery list ID
    response = client.put(
        f"/api/grocery_lists/10",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"extra_items": []},
    )
    assert response.status_code == 422


def test_delete_grocery_list(db, client):
    # Test when grocery list exists
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    gl = db.query(models.GroceryList).filter_by(user_id=user_1.id).one_or_none()
    user_1_token = get_token("user_1")

    response = client.delete(
        f"/api/grocery_lists/{gl.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
    )
    assert response.status_code == 200

    assert (
        db.query(models.GroceryList).filter_by(user_id=user_1.id).one_or_none() is None
    )

    # Test when grocery list doesn't exist
    user_2_token = get_token("user_2")

    response = client.delete(
        f"/api/grocery_lists/1",
        headers={"Authorization": f"Bearer {user_2_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Grocery List with ID 1 does not exist"
