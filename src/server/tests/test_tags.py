from server.tests.utils import get_token
from server.storage import models


def test_list_tags(db, client):
    # Test that admin has access to all users' tags
    admin_token = get_token("admin")
    response = client.get(
        "/api/tags", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 20

    # Test that tags are sorted alphabetically
    assert data["items"][0]["name"] == "Tag 0"
    assert data["items"][1]["name"] == "Tag 0"
    assert data["items"][10]["name"] == "Tag 5"
    assert data["items"][19]["name"] == "Tag 9"

    # Test that user_1 only has access to its own tags
    user_1_token = get_token("user_1")
    response = client.get(
        "/api/tags", headers={"Authorization": f"Bearer {user_1_token}"}
    )
    assert response.status_code == 200

    data = response.json()
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    for item in data["items"]:
        assert item["user_id"] == user_1.id

    # Test filtering by params
    user_2_token = get_token("user_2")
    response = client.get(
        "/api/tags",
        params={"name": "Tag 5"},
        headers={"Authorization": f"Bearer {user_2_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Tag 5"


def test_create_tags(client):
    user_1_token = get_token("user_1")

    # Required fields included
    response = client.post(
        "/api/recipes",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"name": "Tag 11"},
    )
    assert response.status_code == 200

    # Required fields excluded
    response = client.post(
        "/api/tags",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"name": None},
    )
    assert response.status_code == 422

    # Invalid type for name field
    response = client.post(
        "/api/tags",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"name": 11},
    )
    assert response.status_code == 422


def test_update_tags(db, client):
    user_1_token = get_token("user_1")
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()

    original_tags = db.query(models.Tag).filter_by(user_id=user_1.id).all()
    original_tag_0 = original_tags[0]

    # Collect recipes associated with Tag 0 before update
    original_tag_0_associated_recipes = (
        db.query(models.Recipe)
        .filter_by(user_id=user_1.id)
        .filter(models.Recipe.tags.any(models.Tag.name.in_(["Tag 0"])))
        .all()
    )
    original_tag_0_associated_recipes = sorted(
        original_tag_0_associated_recipes, key=lambda x: x.name
    )

    # Update Tag 0
    response = client.put(
        f"/api/tags/{original_tag_0.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"name": "New Tag 0"},
    )
    assert response.status_code == 200

    tag = response.json()
    assert tag["id"] == original_tag_0.id
    assert tag["user_id"] == user_1.id
    assert tag["name"] == "New Tag 0"

    # Collect recipes associated with Tag 0 after update
    new_tag_0_associated_recipes = (
        db.query(models.Recipe)
        .filter_by(user_id=user_1.id)
        .filter(models.Recipe.tags.any(models.Tag.name.in_(["New Tag 0"])))
        .all()
    )
    new_tag_0_associated_recipes = sorted(
        new_tag_0_associated_recipes, key=lambda x: x.name
    )

    # Test that Tag 0's recipe associations persist after its name has been updated
    assert original_tag_0_associated_recipes == new_tag_0_associated_recipes


def test_delete_tags(db, client):
    user_1_token = get_token("user_1")
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()

    original_tag = db.query(models.Tag).filter_by(user_id=user_1.id).first()
    original_tags = db.query(models.Tag).filter_by(user_id=user_1.id).all()

    assert original_tag in original_tags

    response = client.delete(
        f"/api/tags/{original_tag.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
    )
    assert response.status_code == 200

    deleted_tag = response.json()
    assert deleted_tag["id"] == original_tag.id

    new_tags = db.query(models.Tag).filter_by(user_id=user_1.id).all()
    assert deleted_tag not in new_tags
