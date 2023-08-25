from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from server.storage.models import (
    GroceryList,
    GroceryListItem,
    Ingredient,
    MealPlanItem,
    Recipe,
    Step,
    Tag,
    User,
)
from server.storage.utils import sqlalchemy_to_pydantic


class Token(BaseModel):
    access_token: str
    token_type: str


UserSchema = sqlalchemy_to_pydantic(User, exclude_fields=["hashed_password"])
UserCreateSchema = sqlalchemy_to_pydantic(
    User,
    include_fields=["username"],
    additional_attributes={"password": (str, ...)},
    name="UserCreate",
)
UserUpdateSchema = sqlalchemy_to_pydantic(
    User,
    include_fields=["role"],
    all_fields_optional=True,
    additional_attributes={"password": (Optional[str], None)},
    name="UserUpdate",
)
UserListSchema = sqlalchemy_to_pydantic(
    User,
    all_fields_optional=True,
    include_fields=["username", "role"],
    name="UserList",
)

TagSchema = sqlalchemy_to_pydantic(Tag)
TagCreateSchema = sqlalchemy_to_pydantic(
    Tag,
    exclude_fields=["id", "user_id"],
    treat_default_as_optional=True,
    name="TagCreate",
)
TagUpdateSchema = sqlalchemy_to_pydantic(
    Tag,
    exclude_fields=["id", "user_id"],
    all_fields_optional=True,
    name="TagUpdate",
)
TagListSchema = sqlalchemy_to_pydantic(
    Tag,
    exclude_fields=["id", "user_id"],
    all_fields_optional=True,
    name="TagList",
)

IngredientSchema = sqlalchemy_to_pydantic(Ingredient)
StepSchema = sqlalchemy_to_pydantic(Step)
RecipeSchema = sqlalchemy_to_pydantic(
    Recipe,
    additional_attributes={
        "ingredients": (List[IngredientSchema], ...),
        "steps": (List[StepSchema], ...),
        "tags": (List[TagSchema], ...),
    },
)
RecipeCreateSchema = sqlalchemy_to_pydantic(
    Recipe,
    exclude_fields=["id", "user_id"],
    treat_default_as_optional=True,
    additional_attributes={
        "tag_ids": (List[int], []),
        "steps": (List[str], []),
        "ingredients": (List[str], []),
    },
    name="RecipeCreate",
)
RecipeUpdateSchema = sqlalchemy_to_pydantic(
    Recipe,
    exclude_fields=["id", "user_id"],
    all_fields_optional=True,
    additional_attributes={
        "tag_ids": (List[int], []),
        "steps": (List[str], []),
        "ingredients": (List[str], []),
    },
    name="RecipeUpdate",
)
RecipeListSchema = sqlalchemy_to_pydantic(
    Recipe,
    exclude_fields=["id", "user_id"],
    all_fields_optional=True,
    name="RecipeList",
)

MealPlanItemSchema = sqlalchemy_to_pydantic(MealPlanItem)
MealPlanItemCreateSchema = sqlalchemy_to_pydantic(
    MealPlanItem,
    exclude_fields=["id", "user_id"],
    treat_default_as_optional=True,
    name="MealPlanItemCreate",
)
MealPlanItemUpdateSchema = sqlalchemy_to_pydantic(
    MealPlanItem,
    exclude_fields=["id", "user_id"],
    all_fields_optional=True,
    name="MealPlanItemUpdate",
)
MealPlanItemListSchema = sqlalchemy_to_pydantic(
    MealPlanItem,
    exclude_fields=["id", "user_id"],
    all_fields_optional=True,
    name="MealPlanItemList",
)

GroceryListItemSchema = sqlalchemy_to_pydantic(GroceryListItem)

GroceryListSchema = sqlalchemy_to_pydantic(
    GroceryList,
    additional_attributes={"grocery_list_items": (List[GroceryListItemSchema], ...)},
)
GroceryListCreateSchema = sqlalchemy_to_pydantic(
    GroceryList,
    exclude_fields=["id", "user_id"],
    treat_default_as_optional=True,
    additional_attributes={"start_date": (datetime, ...), "end_date": (datetime, ...)},
    name="GroceryListCreate",
)
GroceryListUpdateSchema = sqlalchemy_to_pydantic(
    GroceryList,
    include_fields=["extra_items"],
    all_fields_optional=True,
    name="GroceryListUpdate",
)
