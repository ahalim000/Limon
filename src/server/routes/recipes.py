import re
import os
import uuid
import magic

from typing import List

from fastapi import APIRouter, Depends, UploadFile, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from ingredient_parser import parse_ingredient
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from server.dependencies import get_current_user, get_db
from server.schemas import (
    RecipeCreateSchema,
    RecipeSchema,
    RecipeUpdateSchema,
    RecipeListSchema,
)
from server.storage.models import Ingredient, Recipe, Step, Tag, User
from server.storage.utils import safe_query
from server.config import CONFIG
from server.constants import ALLOWED_IMAGE_FORMATS, IMAGE_FORMAT_EXTENSION_MAP

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def parse_ingredients(data: List[str]) -> List[Ingredient]:
    processed_data = []
    for ingredient in data:
        processed_ingredient = ingredient.strip()
        if processed_ingredient:
            processed_data.append(processed_ingredient)

    ingredients = []
    for index, ingredient in enumerate(data):
        parsed = parse_ingredient(ingredient)
        raw_quantity = parsed.quantity or ""
        matched_quantity = re.match(
            r"[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)", raw_quantity
        )
        quantity = float(matched_quantity[0]) if matched_quantity else 0.0
        ingredient = Ingredient(
            quantity=quantity,
            unit=parsed.unit,
            name=parsed.name,
            comment=parsed.comment,
            input=parsed.sentence,
            position=index,
        )
        ingredients.append(ingredient)

    return ingredients


@router.get("", response_model=Page[RecipeSchema])
def list_recipes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    params: RecipeListSchema = Depends(),  # type: ignore
    sort: str = "alpha",
):
    query = safe_query(select, [Recipe], user)
    if sort == "alpha":
        query = query.order_by(Recipe.name)
    elif sort == "rand":
        query = query.order_by(func.random())
    else:
        raise Exception(f"Sort type unsupported: {sort}")

    for param_key, param_val in params.dict(exclude_unset=True).items():
        if param_val is not None:
            query = query.filter(getattr(Recipe, param_key) == param_val)

    return paginate(db, query)


@router.post("/{id}/upload_image", response_model=RecipeSchema)
def upload_recipe_image(
    id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    file_data = file.file.read()
    mime_type = magic.from_buffer(file_data, mime=True)
    if mime_type not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=400, detail=f"Image file format not supported: {mime_type}"
        )
    extension = IMAGE_FORMAT_EXTENSION_MAP[mime_type]

    recipe = db.scalars(safe_query(select, [Recipe], user).filter_by(id=id)).one()
    user_id = recipe.user_id
    dst_folder = os.path.join(CONFIG.static_dir, str(user_id))
    os.makedirs(dst_folder, exist_ok=True)

    filename = f"{uuid.uuid4()}{extension}"
    dst_file = os.path.join(dst_folder, filename)
    with open(dst_file, "wb") as f:
        f.write(file_data)

    if recipe.image_url:
        os.unlink(recipe.image_url)

    recipe.image_url = f"/static/{user_id}/{filename}"
    db.add(recipe)
    db.commit()
    return recipe


@router.post("", response_model=RecipeSchema)
def create_recipe(
    request_data: RecipeCreateSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)  # type: ignore
):
    request_data = request_data.dict(exclude_unset=True)

    ingredients_data = request_data.pop("ingredients", [])
    steps_data = request_data.pop("steps", [])
    tag_ids = request_data.pop("tag_ids", [])

    recipe = Recipe(user_id=user.id, **request_data)

    recipe.ingredients.extend(parse_ingredients(ingredients_data))

    processed_steps_data = []
    for text in steps_data:
        processed_text = text.strip()
        if processed_text:
            processed_steps_data.append(processed_text)

    for index, text in enumerate(processed_steps_data):
        recipe.steps.append(Step(text=text, position=index))

    for tag_id in tag_ids:
        tag = db.scalars(safe_query(select, [Tag], user).filter_by(id=tag_id)).one()
        recipe.tags.append(tag)

    db.add(recipe)
    db.commit()

    return recipe


@router.get("/{id}", response_model=RecipeSchema)
def get_recipe(
    id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return db.scalars(safe_query(select, [Recipe], user).filter_by(id=id)).one()


@router.put("/{id}", response_model=RecipeSchema)
def update_recipe(
    id: int,
    request_data: RecipeUpdateSchema,  # type: ignore
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    request_data = request_data.dict(exclude_unset=True)

    ingredients_data = request_data.pop("ingredients", [])
    steps_data = request_data.pop("steps", [])
    tag_ids = request_data.pop("tag_ids", [])

    recipe = db.scalars(safe_query(select, [Recipe], user).filter_by(id=id)).one()

    for key, val in request_data.items():
        setattr(recipe, key, val)

    if ingredients_data:
        recipe.ingredients.clear()
        recipe.ingredients.extend(parse_ingredients(ingredients_data))

    if steps_data:
        recipe.steps.clear()
        for index, text in enumerate(steps_data):
            recipe.steps.append(Step(text=text, position=index))

    if tag_ids:
        recipe.tags.clear()
        for tag_id in tag_ids:
            tag = db.scalars(safe_query(select, [Tag], user).filter_by(id=tag_id)).one()
            recipe.tags.append(tag)

    db.add(recipe)
    db.commit()

    return recipe


@router.delete("/{id}", response_model=RecipeSchema)
def delete_recipe(
    id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    recipe = db.scalars(safe_query(select, [Recipe], user).filter_by(id=id)).one()
    resp = RecipeSchema.from_orm(recipe)

    db.delete(recipe)
    db.commit()

    return resp
