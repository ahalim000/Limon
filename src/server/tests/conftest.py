import os, secrets
import pytest

from datetime import datetime, timedelta

os.environ["RECIPE_DATABASE_URL"] = "postgresql:///test_recipes"
os.environ["RECIPE_SECRET_KEY"] = secrets.token_hex(32)

from fastapi.testclient import TestClient

from server.storage import models
from server.storage.database import SessionLocal, Base, engine
from server.routes.users import hash_password
from server.dependencies import get_db

from server.app import init_app

DB_SEEDED = False

app = init_app()


@pytest.fixture(autouse=True, scope="function")
def db():
    global DB_SEEDED

    db = SessionLocal()
    if not DB_SEEDED:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        admin = models.User(
            username="admin", hashed_password=hash_password("admin"), role="admin"
        )
        user_1 = models.User(
            username="user_1", hashed_password=hash_password("user_1"), role="user"
        )
        user_2 = models.User(
            username="user_2", hashed_password=hash_password("user_2"), role="user"
        )

        for user in [user_1, user_2]:
            for i in range(10):
                user.tags.append(models.Tag(user_id=user_1.id, name=f"Tag {i}"))

        for user in [user_1, user_2]:
            for i in range(10):
                recipe = models.Recipe(
                    name=f"Recipe {i}",
                    image_url="static/katherine-chase-zITJdTt5aLc-unsplash.png",
                    source="Family Cookbook",
                    servings=4,
                    servings_type="servings",
                    prep_time=60,
                    cook_time=120,
                    description="A traditional recipe",
                    nutrition="300 calories per serving",
                    favorite=False,
                )
                recipe.tags.extend(user.tags)

                for j in range(5):
                    recipe.steps.append(models.Step(text=f"Step {j}", position=j))

                recipe.ingredients.extend(
                    [
                        models.Ingredient(
                            quantity=1,
                            unit="small",
                            name="onion",
                            comment="finely chopped",
                            input="1 small onion, finely chopped",
                            position=0,
                        ),
                        models.Ingredient(
                            quantity=2,
                            unit="tsp",
                            name="salt",
                            input="2 tsp salt",
                            position=1,
                        ),
                        models.Ingredient(
                            quantity=0.5,
                            unit="tsp",
                            name="oregano",
                            input=".5 tsp oregano",
                            position=2,
                        ),
                        models.Ingredient(
                            quantity=2,
                            unit="small",
                            name="red chiles",
                            comment="slivered",
                            input="2 small red chiles, slivered",
                            position=3,
                        ),
                        models.Ingredient(
                            quantity=1,
                            unit="28-oz can",
                            name="whole peeled tomatoes",
                            input="1 28-oz can whole peeled tomatoes",
                            position=4,
                        ),
                    ]
                )
                user.recipes.append(recipe)

        db.add_all([admin, user_1, user_2])
        db.flush()

        for user in [user_1, user_2]:
            for recipe in user.recipes:
                meal_plan_item = models.MealPlanItem(
                    recipe_id=recipe.id,
                    date=datetime.now() - timedelta(days=1),
                    servings=4,
                    meal_type="dinner",
                )
                db.add(meal_plan_item)

        grocery_list = models.GroceryList(
            user_id=user_1.id,
            extra_items="Item 1\nItem2",
        )
        db.add(grocery_list)

        db.flush()
        db.commit()

        DB_SEEDED = True

    app.dependency_overrides[get_db] = lambda: db

    savepoint = db.begin_nested()
    yield db
    savepoint.rollback()
    db.close()


@pytest.fixture(scope="function")
def client():
    return TestClient(app)
