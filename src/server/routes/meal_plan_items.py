from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from server.dependencies import get_current_user, get_db
from server.schemas import (
    MealPlanItemCreateSchema,
    MealPlanItemSchema,
    MealPlanItemUpdateSchema,
    MealPlanItemListSchema,
)
from server.storage.models import MealPlanItem, Recipe, User
from server.storage.utils import safe_query

router = APIRouter(prefix="/api/meal_plan_items", tags=["meal_plan_items"])


@router.get("", response_model=Page[MealPlanItemSchema])
def list_meal_plan_items(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    params: MealPlanItemListSchema = Depends(),  # type: ignore
):
    query = safe_query(select, [MealPlanItem], user).filter(
        MealPlanItem.date >= start_date, MealPlanItem.date <= end_date
    )

    for param_key, param_val in params.dict(exclude_unset=True).items():
        if param_val is not None:
            query = query.filter(getattr(MealPlanItem, param_key) == param_val)

    return paginate(db, query)


@router.post("", response_model=MealPlanItemSchema)
def create_meal_plan_item(
    request_data: MealPlanItemCreateSchema,  # type: ignore
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    request_data = request_data.dict(exclude_unset=True)

    recipe = db.scalars(
        safe_query(select, [Recipe], user).filter_by(id=request_data["recipe_id"])
    ).one()

    meal_plan_item = MealPlanItem(recipe=recipe, **request_data)

    db.add(meal_plan_item)
    db.commit()

    return meal_plan_item


@router.get("/{id}", response_model=MealPlanItemSchema)
def get_meal_plan_item(
    id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return db.scalars(safe_query(select, [MealPlanItem], user).filter_by(id=id)).one()


@router.put("/{id}", response_model=MealPlanItemSchema)
def update_meal_plan_item(
    id: int,
    request_data: MealPlanItemUpdateSchema,  # type: ignore
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    request_data = request_data.dict(exclude_unset=True)

    meal_plan_item = db.scalars(
        safe_query(select, [MealPlanItem], user).filter_by(id=id)
    ).one()

    for key, val in request_data.items():
        setattr(meal_plan_item, key, val)

    db.add(meal_plan_item)
    db.commit()

    return meal_plan_item


@router.delete("/{id}", response_model=MealPlanItemSchema)
def delete_meal_plan_item(
    id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    meal_plan_item = db.scalars(
        safe_query(select, [MealPlanItem], user).filter_by(id=id)
    ).one()

    db.delete(meal_plan_item)
    db.commit()

    return meal_plan_item
