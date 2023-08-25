from typing import List, Optional

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from server.dependencies import get_current_user, get_db
from server.schemas import TagCreateSchema, TagSchema, TagUpdateSchema, TagListSchema
from server.storage.models import Tag, User
from server.storage.utils import safe_query

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=Page[TagSchema])
def list_tags(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    params: TagListSchema = Depends(),  # type: ignore
):
    query = safe_query(select, [Tag], user)

    for param_key, param_val in params.dict(exclude_unset=True).items():
        if param_val is not None:
            query = query.filter(getattr(Tag, param_key) == param_val)

    return paginate(db, query)


@router.post("", response_model=TagSchema)
def create_tag(
    request_data: TagCreateSchema,  # type: ignore
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    request_data = request_data.dict(exclude_unset=True)

    tag = Tag(user_id=user.id, **request_data)

    db.add(tag)
    db.commit()

    return tag


@router.put("/{id}", response_model=TagSchema)
def update_tag(
    id: int,
    request_data: TagUpdateSchema,  # type: ignore
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    request_data = request_data.dict(exclude_unset=True)

    tag = db.scalars(safe_query(select, [Tag], user).filter_by(id=id)).one()

    for key, val in request_data.items():
        setattr(tag, key, val)

    db.add(tag)
    db.commit()

    return tag


@router.delete("/{id}", response_model=TagSchema)
def delete_tag(
    id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    tag = db.scalars(safe_query(select, [Tag], user).filter_by(id=id)).one()

    db.delete(tag)
    db.commit()

    return tag
