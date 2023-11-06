import os, secrets
import pytest

os.environ["RECIPE_DATABASE_URL"] = "postgresql:///test_recipes"
os.environ["RECIPE_SECRET_KEY"] = secrets.token_hex(32)

from server.storage import models
from server.storage.database import SessionLocal, Base, engine
from server.routes.users import hash_password
from server.dependencies import get_db
from server.app import init_app

from fastapi.testclient import TestClient

DB_SEEDED = False

app = init_app()
client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def df():
    global DB_SEEDED

    db = SessionLocal()
    if not DB_SEEDED:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        admin = models.User(
            username="admin", hashed_password=hash("admin"), role="admin"
        )

        user_1 = models.User(
            username="user_1", hashed_password=hash_password("user_1"), role="user"
        )
        user_2 = models.User(
            username="admin", hashed_password=hash_password("user_2"), role="user"
        )

        db.add_all([admin, user_1, user_2])
        db.flush()

        DB_SEEDED = True

    app.dependency_overrides[get_db] = lambda: db

    savepoint = db.begin_nested()
    yield db
    savepoint.rollback()
    db.close()
