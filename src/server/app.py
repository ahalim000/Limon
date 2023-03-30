from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response

from server.storage.database import SessionLocal
from server.routes import (
    grocery_list_items,
    grocery_lists,
    meal_plan_items,
    tags,
    users,
    recipes,
)
from server.storage.models import User
from server.config import CONFIG


async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
        if response.status_code < 300:
            request.state.db.commit()
        else:
            request.state.db.rollback()
    except Exception:
        request.state.db.rollback()
        raise
    finally:
        request.state.db.close()
    return response


async def setup_bootstrap_admin():
    try:
        db = SessionLocal()
        admin_user = db.query(User).filter_by(username="admin").one_or_none()

        if admin_user is None:
            admin_user = User(
                username="admin",
                hashed_password=users.hash_password(CONFIG.bootstrap_admin_password),
                role="admin",
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()


def init_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(BaseHTTPMiddleware, dispatch=db_session_middleware)
    app.add_event_handler("startup", setup_bootstrap_admin)

    app.include_router(recipes.router)
    app.include_router(users.router)
    app.include_router(tags.router)
    app.include_router(meal_plan_items.router)
    app.include_router(grocery_lists.router)
    app.include_router(grocery_list_items.router)

    return app
