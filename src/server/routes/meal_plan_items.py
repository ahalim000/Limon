from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from server.dependencies import get_storage_manager
from server.storage.storage_manager import StorageManager
from server.storage.models import MealPlanItem, Recipe


router = APIRouter(prefix="/api/meal_plan_items")


class MealPlanItemCreateSchema(BaseModel):
    recipe_id: int
    date: int
    servings: Optional[int]
    meal_type: Optional[str]


class MealPlanItemUpdateSchema(BaseModel):
    recipe_id: Optional[int]
    date: Optional[int]
    servings: Optional[int]
    meal_type: Optional[str]


class MealPlanItemSchema(BaseModel):
    id: int
    recipe_id: int
    date: datetime
    servings: int
    meal_type: Optional[str]
    user_id: int

    class Config:
        orm_mode = True


class ListMealPlanItemSchema(BaseModel):
    items: List[MealPlanItemSchema]


@router.get("", response_model=ListMealPlanItemSchema)
def list_meal_plan_items(
    start_date: int, end_date: int, sm: StorageManager = Depends(get_storage_manager)
):
    filters = {
        "start_date": datetime.fromtimestamp(start_date),
        "end_date": datetime.fromtimestamp(end_date),
    }

    meal_plan_items = sm.list(MealPlanItem, filters, [MealPlanItem.date])

    return {"items": meal_plan_items}


@router.post("", response_model=MealPlanItemSchema)
def create_meal_plan_item(
    request_data: MealPlanItemCreateSchema,
    sm: StorageManager = Depends(get_storage_manager),
):
    request_data = request_data.dict(exclude_unset=True)
    request_data["date"] = datetime.fromtimestamp(request_data["date"])

    recipe = sm.get(Recipe, request_data["recipe_id"])
    request_data["recipe"] = recipe

    if "servings" not in request_data:
        request_data["servings"] = recipe.servings

    return sm.create(MealPlanItem, request_data)


@router.get("/{id}", response_model=MealPlanItemSchema)
def get_meal_plan_item(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.get(MealPlanItem, {"id": id})


@router.put("/{id}", response_model=MealPlanItemSchema)
def update_meal_plan_item(
    id: int,
    request_data: MealPlanItemUpdateSchema,
    sm: StorageManager = Depends(get_storage_manager),
):
    request_data = request_data.dict(exclude_unset=True)

    return sm.update(MealPlanItem, {"id": id}, request_data)


@router.delete("/{id}", response_model=MealPlanItemSchema)
def delete_meal_plan_item(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.delete(MealPlanItem, {"id": id})
