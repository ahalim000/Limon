from datetime import datetime

from server.tests.utils import get_token
from server.storage import models


def test_list_meal_plan_items(db, client):
    user_1_token = get_token("user_1")
    end_date = int(datetime.now().timestamp())
    response = client.get(
        "/api/meal_plan_items",
        headers={"Authorization": f"Bearer {user_1_token}"},
        params={
            "start_date": 0,
            "end_date": end_date,
        },
    )
    assert response.status_code == 200

    data = response.json()

    # Test that user_1 only has access to its own meal plan items
    assert len(data["items"]) == 10
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    for item in data["items"]:
        recipe = db.query(models.Recipe).filter_by(id=item["recipe_id"]).one_or_none()
        assert recipe.user_id == user_1.id

        # Test that date ranges are correct
        date = datetime.fromisoformat(item["date"]).timestamp()
        assert date >= 0
        assert date <= end_date

    # Test filtering by params
    response = client.get(
        "/api/meal_plan_items",
        headers={"Authorization": f"Bearer {user_1_token}"},
        params={
            "start_date": 0,
            "end_date": end_date,
            "meal_type": "dinner",
        },
    )
    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 10
    for item in data["items"]:
        assert item["meal_type"] == "dinner"

    # Test that meal plan items are returned in order by date
    first_meal_plan_item_date = data["items"][0]["date"]
    for item in data["items"]:
        assert item["date"] >= first_meal_plan_item_date

    # Test that admin has access to all users' meal plan items
    admin_token = get_token("admin")
    response = client.get(
        "/api/meal_plan_items",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={
            "start_date": 0,
            "end_date": int(datetime.now().timestamp()),
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 20


def test_create_meal_plan_item(db, client):
    user_1_token = get_token("user_1")
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()

    # All fields/All required fields
    recipe = db.query(models.Recipe).filter_by(user_id=user_1.id).first()
    date = datetime.utcnow().isoformat()

    response = client.post(
        "/api/meal_plan_items",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={
            "recipe_id": recipe.id,
            "date": date,
            "servings": 8,
            "meal_type": "lunch",
        },
    )
    assert response.status_code == 200

    meal_plan_item = response.json()
    assert meal_plan_item["recipe_id"] == recipe.id
    assert meal_plan_item["date"] == date
    assert meal_plan_item["servings"] == 8
    assert meal_plan_item["meal_type"] == "lunch"

    # Required fields excluded
    response = client.post(
        "/api/meal_plan_items",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={
            "date": date,
            "servings": 8,
            "meal_type": "lunch",
        },
    )
    assert response.status_code == 422

    # Invalid type for servings field
    response = client.post(
        "/api/meal_plan_items",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={
            "recipe_id": recipe.id,
            "date": date,
            "servings": "eight",
            "meal_type": "lunch",
        },
    )
    assert response.status_code == 422


def test_get_meal_plan_item(db, client):
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    user_1_meal_plan_items = db.query(models.MealPlanItem).filter_by(user_id=user_1.id)
    user_1_token = get_token("user_1")

    for meal_plan_item in user_1_meal_plan_items:
        response = client.get(
            f"/api/meal_plan_items/{meal_plan_item.id}",
            headers={"Authorization": f"Bearer {user_1_token}"},
        )
        assert response.status_code == 200


def test_update_meal_plan_item(db, client):
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    user_1_token = get_token("user_1")

    original_meal_plan_items = (
        db.query(models.MealPlanItem).filter_by(user_id=user_1.id).all()
    )
    original_meal_plan_item_0 = original_meal_plan_items[0]
    original_meal_plan_item_1 = original_meal_plan_items[1]

    user_1_recipes = db.query(models.Recipe).filter_by(user_id=user_1.id).all()
    new_recipe_id = None
    for recipe in user_1_recipes:
        if recipe.id != original_meal_plan_item_0.recipe_id:
            new_recipe_id = recipe.id
            break

    # Update recipe_id
    response = client.put(
        f"/api/meal_plan_items/{original_meal_plan_item_0.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"recipe_id": new_recipe_id},
    )
    assert response.status_code == 200

    new_meal_plan_item_0 = response.json()
    assert new_meal_plan_item_0["id"] == original_meal_plan_item_0.id
    assert new_meal_plan_item_0["recipe_id"] == new_recipe_id
    assert new_meal_plan_item_0["date"] == original_meal_plan_item_0.date.isoformat()
    assert new_meal_plan_item_0["servings"] == original_meal_plan_item_0.servings
    assert new_meal_plan_item_0["meal_type"] == original_meal_plan_item_0.meal_type

    new_mpi_0 = (
        db.query(models.MealPlanItem).filter_by(id=new_meal_plan_item_0["id"]).one()
    )
    assert new_mpi_0.user_id == original_meal_plan_item_0.user_id

    # Update multiple fields
    new_servings = 3
    new_meal_type = "lunch"
    response = client.put(
        f"/api/meal_plan_items/{original_meal_plan_item_1.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
        json={"servings": new_servings, "meal_type": new_meal_type},
    )
    assert response.status_code == 200

    new_meal_plan_item_1 = response.json()
    assert new_meal_plan_item_1["id"] == original_meal_plan_item_1.id
    assert new_meal_plan_item_1["recipe_id"] == original_meal_plan_item_1.recipe_id
    assert new_meal_plan_item_1["date"] == original_meal_plan_item_1.date.isoformat()
    assert new_meal_plan_item_1["servings"] == new_servings
    assert new_meal_plan_item_1["meal_type"] == new_meal_type

    new_mpi_1 = (
        db.query(models.MealPlanItem).filter_by(id=new_meal_plan_item_1["id"]).one()
    )
    assert new_mpi_1.user_id == original_meal_plan_item_1.user_id


def test_delete_meal_plan_item(db, client):
    user_1_token = get_token("user_1")
    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()

    original_meal_plan_item = (
        db.query(models.MealPlanItem).filter_by(user_id=user_1.id).first()
    )
    original_meal_plan_items = (
        db.query(models.MealPlanItem).filter_by(user_id=user_1.id).all()
    )

    assert original_meal_plan_item in original_meal_plan_items

    response = client.delete(
        f"/api/tags/{original_meal_plan_item.id}",
        headers={"Authorization": f"Bearer {user_1_token}"},
    )
    assert response.status_code == 200

    deleted_meal_plan_item = response.json()
    assert deleted_meal_plan_item["id"] == original_meal_plan_item.id

    new_meal_plan_items = (
        db.query(models.MealPlanItem).filter_by(user_id=user_1.id).all()
    )
    assert deleted_meal_plan_item not in new_meal_plan_items
