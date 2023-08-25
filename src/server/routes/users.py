from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from server.config import CONFIG
from server.dependencies import get_current_user, get_db
from server.schemas import (
    Token,
    UserCreateSchema,
    UserSchema,
    UserUpdateSchema,
    UserListSchema,
)
from server.storage.models import User
from server.storage.utils import safe_query

router = APIRouter(prefix="/api")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationException(Exception):
    pass


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.scalars(select(User).filter_by(username=username)).one_or_none()
    if user is None:
        raise AuthenticationException(f"User '{username}' doesn't exist")

    if not pwd_context.verify(password, user.hashed_password):
        raise AuthenticationException(f"Incorrect password for user '{username}'")

    return user


def create_oauth_token(claims: dict) -> str:
    return jwt.encode(claims, CONFIG.secret_key, algorithm=CONFIG.algorithm)


@router.post("/token", response_model=Token, tags=["token"])
def create_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    try:
        authenticate_user(db, form_data.username, form_data.password)
    except AuthenticationException as e:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=CONFIG.access_token_expire_minutes)

    token = create_oauth_token(
        {"sub": form_data.username, "exp": datetime.utcnow() + access_token_expires}
    )

    return {"access_token": token, "token_type": "bearer"}


@router.post("/users", response_model=UserSchema, tags=["users"])
def create_user(request_data: UserCreateSchema, db: Session = Depends(get_db)):  # type: ignore
    user = User(
        username=request_data.username,
        hashed_password=hash_password(request_data.password),
        role="user",
    )
    db.add(user)

    try:
        db.flush()
    except IntegrityError as e:
        if "already exists" in str(e):
            raise HTTPException(
                400, detail=f"Username '{request_data.username}' already taken"
            )
        raise

    return user


@router.get("/users", response_model=Page[UserSchema], tags=["users"])
def list_users(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    params: UserListSchema = Depends(),  # type: ignore
):
    if user.role != "admin":
        raise HTTPException(403, detail="Only admins can list users")

    query = safe_query(select, [User], user)
    for param_key, param_val in params.dict(exclude_unset=True).items():
        if param_val is not None:
            query = query.filter(getattr(User, param_key) == param_val)

    return paginate(db, query)


@router.get("/users/me", response_model=UserSchema, tags=["users"])
def get_user_self(user: User = Depends(get_current_user)):
    return user


@router.put("/users/{id}", response_model=UserSchema, tags=["users"])
def update_user(
    id: int,
    request_data: UserUpdateSchema,  # type: ignore
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    update_data = request_data.dict(exclude_unset=True)

    if "password" in update_data:
        update_user = db.scalars(
            safe_query(select, [User], user).filter_by(user=id)
        ).one()
        if user.id != update_user.id:
            raise HTTPException(
                403, detail="Passwords can only be updated for same user as requester"
            )

        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    if "role" in update_data:
        if user.role != "admin":
            raise HTTPException(403, detail="Roles can only be updated by admin users")

    query = safe_query(update, [User], user).filter_by(id=id).values(**update_data)
    db.execute(query)
    db.commit()
