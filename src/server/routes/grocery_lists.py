from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from server.dependencies import get_current_user, get_db
from server.schemas import (
    GroceryListCreateSchema,
    GroceryListSchema,
    GroceryListUpdateSchema,
)
from server.storage.models import GroceryList, GroceryListItem, MealPlanItem, User
from server.storage.utils import safe_query

router = APIRouter(prefix="/api/grocery_lists", tags=["grocery_lists"])


@router.post("", response_model=GroceryListSchema)
def create_grocery_list(
    request_data: GroceryListCreateSchema,  # type: ignore
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    existing_grocery_list = db.scalars(
        safe_query(select, [GroceryList], user)
    ).one_or_none()
    if existing_grocery_list is not None:
        raise HTTPException(
            status_code=400,
            detail={"message": "Only one grocery list can exist at a time"},
        )

    request_data = request_data.dict(exclude_unset=True)

    start_date = request_data.pop("start_date")
    end_date = request_data.pop("end_date")

    query = safe_query(select, [MealPlanItem], user).filter(
        MealPlanItem.date >= start_date, MealPlanItem.date <= end_date
    )
    meal_plan_items = db.scalars(query).all()

    grocery_list = GroceryList(user_id=user.id, **request_data)

    for meal_plan_item in meal_plan_items:
        for ingredient in meal_plan_item.recipe.ingredients:
            grocery_list.grocery_list_items.append(
                GroceryListItem(
                    active=True,
                    quantity=ingredient.quantity,
                    unit=ingredient.unit,
                    name=ingredient.name,
                    comment=ingredient.comment,
                    recipe_name=meal_plan_item.recipe.name,
                    servings=meal_plan_item.recipe.servings,
                    extra_items=False,
                )
            )

    if grocery_list.extra_items is not None:
        extra_items = grocery_list.extra_items.split("\n")
        for extra_item in extra_items:
            grocery_list.grocery_list_items.append(
                GroceryListItem(
                    active=True,
                    quantity=0,
                    name=extra_item,
                    recipe_name="Extra Items",
                    servings=1,
                    extra_items=True,
                )
            )

    db.add(grocery_list)
    db.flush()

    return grocery_list


@router.get("/{id}", response_model=GroceryListSchema)
def get_grocery_list(
    id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    grocery_list = db.scalars(
        safe_query(select, [GroceryList], user).filter_by(id=id)
    ).one_or_none()

    if grocery_list is None:
        raise HTTPException(404, f"Grocery List with ID {id} does not exist")

    return grocery_list


@router.put("/{id}", response_model=GroceryListSchema)
def update_grocery_list(
    id: int,
    request_data: GroceryListUpdateSchema,  # type: ignore
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    request_data = request_data.dict(exclude_unset=True)

    grocery_list = db.scalars(
        safe_query(select, [GroceryList], user).filter_by(id=id)
    ).one()

    grocery_list.grocery_list_items[:] = [
        item for item in grocery_list.grocery_list_items if not item.extra_items
    ]

    extra_items = request_data.pop("extra_items", grocery_list.extra_items)
    grocery_list.extra_items = extra_items

    if extra_items != "":
        extra_items_list = extra_items.split("\n")
        for extra_item in extra_items_list:
            grocery_list.grocery_list_items.append(
                GroceryListItem(
                    active=True,
                    quantity=0,
                    name=extra_item,
                    recipe_name="Extra Items",
                    servings=1,
                    extra_items=True,
                )
            )

    db.add(grocery_list)
    db.flush()

    return grocery_list


@router.delete("/{id}", response_model=GroceryListSchema)
def delete_grocery_list(
    id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    grocery_list = db.scalars(
        safe_query(select, [GroceryList], user).filter_by(id=id)
    ).one_or_none()

    if grocery_list is None:
        raise HTTPException(404, f"Grocery List with ID {id} does not exist")

    db.delete(grocery_list)
    db.flush()

    return grocery_list
