import os

from unittest.mock import mock_open, patch, MagicMock

from typing import cast
from server.tests.utils import get_token
from server.tests.test_recipes_data import user_1_test_recipes
from server.storage import models


def test_authentication(client):
    # Try without auth
    user_response = client.get("/api/users/me")
    assert user_response.status_code == 401
    # Get Token
    token_request = client.post(
        "/api/token",
        data={"username": "admin", "password": "admin"},
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


def test_list_recipes(db, client):
    # Test that admin has access to all users' recipes
    admin_token = get_token("admin")
    response = client.get(
        "/api/recipes", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 20

    # Test that default sort (alphabetical) works
    assert data["items"][0]["name"] == "Recipe 0"
    assert data["items"][1]["name"] == "Recipe 0"
    assert data["items"][10]["name"] == "Recipe 5"
    assert data["items"][19]["name"] == "Recipe 9"

    # Test that sorting by random works
    response = client.get(
        "/api/recipes",
        params={"sort": "rand"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data_sorted_rand_1 = response.json()

    response = client.get(
        "/api/recipes",
        params={"sort": "rand"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data_sorted_rand_2 = response.json()

    assert data_sorted_rand_1 != data_sorted_rand_2

    # Test unsupported sort types
    response = client.get(
        "/api/recipes",
        params={"sort": "unsupported"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Sort type unsupported: unsupported"

    # Test that user_1 only has access to its own recipes
    user_1_token = get_token("user_1")
    response = client.get(
        "/api/recipes", headers={"Authorization": f"Bearer {user_1_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    for item in data["items"]:
        assert item["user_id"] == user_1.id

    # Test filtering by params
    user_2_token = get_token("user_2")
    response = client.get(
        "/api/recipes",
        params={"favorite": True},
        headers={"Authorization": f"Bearer {user_2_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0


def test_upload_recipe_image(db, client):
    user_1_token = get_token("user_1")
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()

    # Valid mime type
    recipe_1 = (
        db.query(models.Recipe)
        .filter_by(user_id=user_1.id)
        .filter_by(name="Recipe 1")
        .one()
    )

    fpath = os.path.join(os.path.dirname(__file__), "assets/black_square.jpg")
    with open(fpath, "rb") as f:
        image_data = f.read()

    mocked_open = MagicMock()
    with patch("builtins.open", mock_open(mocked_open)):
        response = client.post(
            f"/api/recipes/{recipe_1.id}/upload_image",
            headers={"Authorization": f"Bearer {user_1_token}"},
            files={"file": ("assets/black_square.jpg", image_data, "image/jpeg")},
        )

    assert response.status_code == 200
    mocked_open.assert_called()

    # Invalid mime type
    recipe_2 = (
        db.query(models.Recipe)
        .filter_by(user_id=user_1.id)
        .filter_by(name="Recipe 2")
        .one()
    )

    fpath = os.path.join(os.path.dirname(__file__), "assets/dummy.pdf")
    with open(fpath, "rb") as f:
        image_data = f.read()

    mocked_open = MagicMock()
    with patch("builtins.open", mock_open(mocked_open)):
        response = client.post(
            f"/api/recipes/{recipe_2.id}/upload_image",
            headers={"Authorization": f"Bearer {user_1_token}"},
            files={"file": ("assets/dummy.pdf", image_data, "application/pdf")},
        )
    assert response.status_code == 400

    data = response.json()
    assert data["detail"] == "Image file format not supported: application/pdf"

    # Different recipe has same image
    recipe_3 = (
        db.query(models.Recipe)
        .filter_by(user_id=user_1.id)
        .filter_by(name="Recipe 3")
        .one()
    )

    recipe_4 = (
        db.query(models.Recipe)
        .filter_by(user_id=user_1.id)
        .filter_by(name="Recipe 4")
        .one()
    )

    fpath = os.path.join(os.path.dirname(__file__), "assets/black_square.jpg")
    with open(fpath, "rb") as f:
        image_data = f.read()

    mocked_open = MagicMock()
    with patch("builtins.open", mock_open(mocked_open)):
        response = client.post(
            f"/api/recipes/{recipe_3.id}/upload_image",
            headers={"Authorization": f"Bearer {user_1_token}"},
            files={"file": ("assets/black_square.jpg", image_data, "image/jpeg")},
        )
        assert response.status_code == 200

        mocked_open.assert_called()
        r_3 = response.json()
        assert r_3["image_url"] != None

        response = client.post(
            f"/api/recipes/{recipe_4.id}/upload_image",
            headers={"Authorization": f"Bearer {user_1_token}"},
            files={"file": ("assets/black_square.jpg", image_data, "image/jpeg")},
        )
        assert response.status_code == 200

        mocked_open.assert_called()
        r_4 = response.json()
        assert r_4["image_url"] != None

        assert r_3["image_url"] != r_4["image_url"]

    # Recipe already has image
    original_image_url = recipe_1.image_url
    assert original_image_url != None

    fpath = os.path.join(os.path.dirname(__file__), "assets/blue_square.png")
    with open(fpath, "rb") as f:
        image_data = f.read()

    mocked_open = MagicMock()
    mocked_unlink = MagicMock()
    with patch("builtins.open", mock_open(mocked_open)), patch(
        "os.unlink", mocked_unlink
    ):
        response = client.post(
            f"/api/recipes/{recipe_1.id}/upload_image",
            headers={"Authorization": f"Bearer {user_1_token}"},
            files={"file": ("assets/blue_square.png", image_data, "image/jpeg")},
        )

    assert response.status_code == 200

    mocked_open.assert_called()
    mocked_unlink.assert_called()
    r_1 = response.json()
    assert r_1["image_url"] != None
    assert original_image_url != r_1["image_url"]


def test_create_recipe(db, client):
    user_1_token = get_token("user_1")
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()

    # All fields
    response = client.post(
        "/api/recipes",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json=user_1_test_recipes[0],
    )
    assert response.status_code == 200

    recipe = response.json()
    assert recipe["user_id"] == user_1.id
    assert recipe["name"] == "Recipe 11"
    assert recipe["image_url"] == "static/katherine-chase-zITJdTt5aLc-unsplash.png"
    assert recipe["source"] == "Family Cookbook"
    assert recipe["servings"] == 4
    assert recipe["servings_type"] == "servings"
    assert recipe["prep_time"] == 65
    assert recipe["cook_time"] == 60
    assert recipe["description"] == "A traditional recipe"
    assert recipe["nutrition"] == "300 calories per serving"
    assert recipe["favorite"] == False
    assert recipe["ingredients"][0]["input"] == "1 small onion, finely chopped"
    assert recipe["steps"][4]["text"] == "Step 5"
    assert recipe["tags"] == []

    # Minimal fields
    response = client.post(
        "/api/recipes",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json=user_1_test_recipes[1],
    )
    assert response.status_code == 200

    recipe = response.json()
    assert recipe["name"] == "Recipe 12"
    assert recipe["image_url"] == None
    assert recipe["nutrition"] == ""

    # Required fields excluded
    response = client.post(
        "/api/recipes",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json=user_1_test_recipes[2],
    )
    assert response.status_code == 422

    # Invalid type for steps field
    response = client.post(
        "/api/recipes",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json=user_1_test_recipes[3],
    )
    assert response.status_code == 422


def test_get_recipe(db, client):
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    user_1_recipes = db.query(models.Recipe).filter_by(user_id=user_1.id)
    user_1_token = get_token("user_1")

    for recipe in user_1_recipes:
        response = client.get(
            f"/api/recipes/{recipe.id}",
            headers={"Authorization": f"Bearer {user_1_token}"},
        )
        assert response.status_code == 200


def test_update_recipe(db, client):
    user_1_token = get_token("user_1")
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()

    original_recipes = db.query(models.Recipe).filter_by(user_id=user_1.id).all()
    original_recipe_0 = original_recipes[0]
    original_recipe_0_ingredient_0 = original_recipe_0.ingredients[0]
    original_recipe_0_step_1 = original_recipe_0.steps[1]
    original_recipe_0_tag_2 = original_recipe_0.tags[2]

    # Update Recipe 0 favorite field
    response = client.put(
        f"/api/recipes/{original_recipes[0].id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json=user_1_test_recipes[4],
    )
    assert response.status_code == 200

    recipe = response.json()
    assert recipe["id"] == original_recipe_0.id
    assert recipe["user_id"] == user_1.id
    assert recipe["name"] == "Recipe 0"
    assert recipe["image_url"] == None
    assert recipe["source"] == "Family Cookbook"
    assert recipe["servings"] == 4
    assert recipe["servings_type"] == "servings"
    assert recipe["prep_time"] == 60
    assert recipe["cook_time"] == 120
    assert recipe["description"] == "A traditional recipe"
    assert recipe["nutrition"] == "300 calories per serving"
    assert recipe["favorite"] == True
    assert recipe["tags"][5]["name"] == "Tag 5"
    assert recipe["ingredients"][0]["input"] == "1 small onion, finely chopped"
    assert recipe["steps"][4]["text"] == "Step 4"

    # Update Recipe 0 ingredients
    response = client.put(
        f"/api/recipes/{original_recipes[0].id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json=user_1_test_recipes[5],
    )
    assert response.status_code == 200

    recipe = response.json()
    assert recipe["id"] == original_recipe_0.id
    assert len(recipe["ingredients"]) == 1
    assert recipe["ingredients"][0]["id"] != original_recipe_0_ingredient_0.id
    assert recipe["ingredients"][0]["input"] == "2 tbsp white vinegar"

    # Update Recipe 0 steps
    response = client.put(
        f"/api/recipes/{original_recipes[0].id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json=user_1_test_recipes[6],
    )
    assert response.status_code == 200

    recipe = response.json()
    assert recipe["id"] == original_recipe_0.id
    assert len(recipe["steps"]) == 6
    assert recipe["steps"][1]["id"] != original_recipe_0_step_1.id
    assert recipe["steps"][1]["text"] == "New Step 1"
    assert recipe["steps"][5]["text"] == "New Step 5"

    # Update Recipe 0 tags
    user_1_tags = db.query(models.Tag).filter_by(user_id=user_1.id).all()
    for i in range(5):
        user_1_test_recipes[7]["tag_ids"].append(user_1_tags[i].id)

    response = client.put(
        f"/api/recipes/{original_recipes[0].id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json=user_1_test_recipes[7],
    )
    assert response.status_code == 200

    recipe = response.json()
    assert recipe["id"] == original_recipe_0.id
    assert len(recipe["tags"]) == 5
    assert recipe["tags"][2]["id"] == original_recipe_0_tag_2.id
    assert recipe["tags"][2]["name"] == "Tag 2"
    assert recipe["tags"][3]["name"] == "Tag 3"


def test_delete_recipe(db, client):
    user_1_token = get_token("user_1")
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()

    original_recipe = db.query(models.Recipe).filter_by(user_id=user_1.id).first()
    original_recipes = db.query(models.Recipe).filter_by(user_id=user_1.id).all()
    assert original_recipe in original_recipes

    response = client.delete(
        f"/api/recipes/{original_recipe.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
    )
    assert response.status_code == 200

    new_recipe = response.json()
    assert new_recipe["id"] == original_recipe.id

    new_recipes = db.query(models.Recipe).filter_by(user_id=user_1.id).all()
    assert original_recipe not in new_recipes
