from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from server.dependencies import get_storage_manager
from server.storage.storage_manager import StorageManager
from server.storage.models import GroceryList, GroceryListItem, MealPlanItem

router = APIRouter(prefix="/api/grocery_lists")


class GroceryListItemSchema(BaseModel):
    id: int
    grocery_list_id: int
    active: bool
    quantity: Optional[int]
    unit: Optional[str]
    name: str
    comment: Optional[str]
    recipe_name: str
    thumbnail_url: Optional[str]
    servings: Optional[int]
    extra_items: bool
    user_id: int

    class Config:
        orm_mode = True


class GroceryListCreateSchema(BaseModel):
    start_date: int
    end_date: int
    extra_items: Optional[str]


class GroceryListUpdateSchema(BaseModel):
    extra_items: str


class GroceryListSchema(BaseModel):
    id: int
    extra_items: Optional[str]
    grocery_list_items: List[GroceryListItemSchema]

    class Config:
        orm_mode = True


@router.post("", response_model=GroceryListSchema)
def create_grocery_list(
    request_data: GroceryListCreateSchema,
    sm: StorageManager = Depends(get_storage_manager),
):
    request_data = request_data.dict(exclude_unset=True)

    filters = {
        "start_date": datetime.fromtimestamp(request_data["start_date"]),
        "end_date": datetime.fromtimestamp(request_data["end_date"]),
    }

    meal_plan_items = sm.list(MealPlanItem, filters, [MealPlanItem.date])
    extra_items = request_data.get("extra_items", "")
    grocery_list = sm.create(GroceryList, {"extra_items": extra_items})

    for meal_plan_item in meal_plan_items:
        for ingredient in meal_plan_item.recipe.ingredient:
            sm.create(
                GroceryListItem,
                {
                    "grocery_list_id": grocery_list.id,
                    "active": True,
                    "quantity": ingredient.quantity,
                    "unit": ingredient.unit,
                    "name": ingredient.name,
                    "comment": ingredient.comment,
                    "recipe_name": meal_plan_item.recipe.name,
                    "thumbnail_url": meal_plan_item.recipe.thumbnail_url,
                    "servings": meal_plan_item.recipe.servings,
                    "extra_items": False,
                },
            )

    extra_items_lines = extra_items.split("\n")
    for extra_item in extra_items_lines:
        sm.create(
            GroceryListItem,
            {
                "grocery_list_id": grocery_list.id,
                "active": True,
                "quantity": 0,
                "name": extra_item,
                "recipe_name": "Extra Items",
                "extra_items": True,
                "servings": 1,
            },
        )

    return grocery_list


@router.put("/{id}", response_model=GroceryListSchema)
def update_grocery_list(
    id: int,
    request_data: GroceryListUpdateSchema,
    sm: StorageManager = Depends(get_storage_manager),
):
    old_extra_items = sm.list(
        GroceryListItem, {"grocery_list_id": id, "extra_items": True}
    )

    for item in old_extra_items:
        sm.delete(GroceryListItem, {"id": item.id})

    new_extra_items = request_data.get("extra_items", "")
    grocery_list = sm.update(GroceryList, {"id": id}, {"extra_items": new_extra_items})

    extra_items_lines = new_extra_items.split("\n")
    for extra_item in extra_items_lines:
        sm.create(
            GroceryListItem,
            {
                "grocery_list_id": id,
                "active": True,
                "quantity": 0,
                "name": extra_item,
                "recipe_name": "Extra Items",
                "extra_items": True,
                "servings": 1,
            },
        )

    return grocery_list


@router.get("/{id}", response_model=GroceryListSchema)
def get_grocery_list(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.get(GroceryList, {"id": id})


@router.delete("/{id}", response_model=GroceryListSchema)
def delete_grocery_list(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.delete(GroceryList, {"id": id})
