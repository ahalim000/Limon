from typing import List, Optional
from datetime import time
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from server.dependencies import get_storage_manager
from server.storage.storage_manager import StorageManager
from server.storage.models import Ingredient, Recipe, RecipeTagAssoc, Step, Tag


router = APIRouter(prefix="/api/recipes")


class IngredientSchema(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    quantity: Optional[int]
    unit: Optional[str]
    name: str
    comment: Optional[str]
    input: Optional[str]

    class Config:
        orm_mode = True


class IngredientCreateSchema(BaseModel):
    quantity: Optional[int]
    unit: Optional[str]
    name: str
    comment: Optional[str]
    input: Optional[str]


class StepSchema(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    text: str

    class Config:
        orm_mode = True


class TagSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class RecipeCreateSchema(BaseModel):
    name: str
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    source: Optional[str]
    servings: int
    servings_type: Optional[str]
    prep_time: Optional[time]
    cook_time: Optional[time]
    description: Optional[str]
    nutrition: Optional[str]
    favorite: Optional[bool]
    ingredient_schemas: Optional[List[IngredientCreateSchema]]
    step_texts: Optional[List[str]]
    tag_ids: Optional[List[int]]


class RecipeUpdateSchema(BaseModel):
    name: Optional[str]
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    source: Optional[str]
    servings: Optional[int]
    servings_type: Optional[str]
    prep_time: Optional[time]
    cook_time: Optional[time]
    description: Optional[str]
    nutrition: Optional[str]
    favorite: Optional[bool]
    ingredient_schemas: Optional[List[IngredientCreateSchema]]
    step_texts: Optional[List[str]]
    tag_ids: Optional[List[int]]


class RecipeSchema(BaseModel):
    id: int
    user_id: int
    name: str
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    source: Optional[str]
    servings: int
    servings_type: Optional[str]
    prep_time: Optional[time]
    cook_time: Optional[time]
    description: Optional[str]
    nutrition: Optional[str]
    favorite: Optional[bool]
    ingredients: List[IngredientSchema]
    steps: List[StepSchema]
    tags: List[TagSchema]

    class Config:
        orm_mode = True


class ListRecipeSchema(BaseModel):
    items: List[RecipeSchema]


@router.get("", response_model=ListRecipeSchema)
def list_recipes(
    name: Optional[str] = None, sm: StorageManager = Depends(get_storage_manager)
):
    filters = {}
    if name is not None:
        filters["name"] = name

    recipes = sm.list(Recipe, filters, [Recipe.name])

    return {"items": recipes}


@router.post("", response_model=RecipeSchema)
def create_recipe(
    request_data: RecipeCreateSchema, sm: StorageManager = Depends(get_storage_manager)
):
    request_data = request_data.dict(exclude_unset=True)

    ingredient_schemas = request_data.pop("ingredient_schemas", [])
    step_texts = request_data.pop("steps_texts", [])
    tag_ids = request_data.pop("tag_ids", [])

    recipe = sm.create(Recipe, request_data)

    for index, schema in enumerate(ingredient_schemas):
        schema["recipe_id"] = recipe.id
        schema["position"] = index
        sm.create(Ingredient, schema)

    for index, text in enumerate(step_texts):
        sm.create(Step, {"recipe_id": id, "text": text, "position": index})

    for tag_id in tag_ids:
        sm.create(RecipeTagAssoc, {"recipe_id": recipe.id, "tag_id": tag_id})

    return recipe


@router.get("/{id}", response_model=RecipeSchema)
def get_recipe(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.get(Recipe, {"id": id})


@router.put("/{id}", response_model=RecipeSchema)
def update_recipe(
    id: int,
    request_data: RecipeUpdateSchema,
    sm: StorageManager = Depends(get_storage_manager),
):
    request_data = request_data.dict(exclude_unset=True)

    ingredient_schemas = request_data.pop("ingredient_schemas", [])
    step_texts = request_data.pop("step_texts", [])
    tag_ids = request_data.pop("tag_ids", [])

    if ingredient_schemas:
        ingredients = []
        for index, schema in enumerate(ingredient_schemas):
            schema["position"] = index
            ingredients.append(Ingredient(**schema))
        request_data["ingredients"] = ingredients

    if step_texts:
        steps = []
        for index, text in enumerate(step_texts):
            steps.append(Step(text=text, position=index))
        request_data["steps"] = steps

    if tag_ids:
        tags = []
        for tag_id in tag_ids:
            tags.append(Tag(recipe_id=id, tag_id=tag_id))
        request_data["tags"] = tags

    return sm.update(Recipe, {"id": id}, request_data)


@router.delete("/{id}", response_model=RecipeSchema)
def delete_recipe(id: int, sm: StorageManager = Depends(get_storage_manager)):
    return sm.delete(Recipe, {"id": id})
