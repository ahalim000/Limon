from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from server.dependencies import get_storage_manager
from server.storage.storage_manager import StorageManager
from server.storage.models import Tag


router = APIRouter(prefix="/api/tags")


class TagCreateUpdateSchema(BaseModel):
    name: str


class TagSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class ListTagSchema(BaseModel):
    items: List[TagSchema]


@router.get("", response_model=ListTagSchema)
def list_tags(
    name: Optional[str] = None, sm: StorageManager = Depends(get_storage_manager)
):
    filters = {}
    if name is not None:
        filters["name"] = name

    tags = sm.list(Tag, filters, [Tag.name])

    return {"items": tags}


@router.post("", response_model=TagSchema)
def create_tag(
    request_data: TagCreateUpdateSchema,
    sm: StorageManager = Depends(get_storage_manager),
):
    request_data = request_data.dict()

    return sm.create(Tag, request_data)


@router.put("/{id}", response_model=TagSchema)
def update_tag(
    id: int,
    request_data: TagCreateUpdateSchema,
    sm: StorageManager = Depends(get_storage_manager),
):
    request_data = request_data.dict()

    return sm.update(Tag, {"id": id}, request_data)


@router.delete("/{id}", response_model=TagSchema)
def delete_tag(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.delete(Tag, {"id": id})
