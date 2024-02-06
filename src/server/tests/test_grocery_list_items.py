from server.tests.utils import get_token
from server.storage import models


def test_toggle_grocery_list_item(db, client):
    user_1_token = get_token("user_1")

    user_1 = db.query(models.User).filter_by(username="user_1").one_or_none()
    grocery_list = (
        db.query(models.GroceryList).filter_by(user_id=user_1.id).one_or_none()
    )
    gli = models.GroceryListItem(
        grocery_list_id=grocery_list.id,
        active=True,
        quantity=1.0,
        unit="small",
        name="onion",
        comment="finely chopped",
        recipe_name="Recipe 1",
        servings=4,
        extra_items=False,
    )
    db.add(gli)
    db.flush()

    response = client.put(
        f"/api/grocery_list_items/{gli.id}/toggle",
        headers={"Authorization": f"Bearer {user_1_token}"},
    )
    assert response.status_code == 204

    grocery_list_item = (
        db.query(models.GroceryListItem).filter_by(id=gli.id).one_or_none()
    )
    assert grocery_list_item.active == False
