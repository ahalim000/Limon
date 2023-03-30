from server.storage.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, ForeignKey
from sqlalchemy.orm import declared_attr, declarative_mixin, synonym

from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy


@declarative_mixin
class UserIdMixin:
    @declared_attr
    def user_id(cls):
        return Column(
            Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
        )


class User(Base, UserIdMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    user_id = synonym("id")


class Recipe(Base, UserIdMixin):
    __tablename__ = "recipe"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    image_url = Column(String)
    thumbnail_url = Column(String)
    source = Column(String, nullable=False)
    servings = Column(Integer, nullable=False)
    servings_type = Column(String, nullable=False)
    prep_time = Column(Integer)
    cook_time = Column(Integer)
    description = Column(String, nullable=False)
    nutrition = Column(String, nullable=False)
    favorite = Column(Boolean, nullable=False)
    ingredients = relationship(
        "Ingredient", back_populates="recipe", cascade="all, delete-orphan"
    )
    steps = relationship("Step", back_populates="recipe", cascade="all, delete-orphan")
    tags = relationship(
        "Tag",
        secondary="recipe_tag_assoc",
        back_populates="recipes",
        cascade="all, delete",
        passive_deletes=True,
    )


class Tag(Base, UserIdMixin):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    recipes = relationship(
        "Recipe",
        secondary="recipe_tag_assoc",
        back_populates="tags",
        cascade="all, delete",
        passive_deletes=True,
    )


class RecipeTagAssoc(Base):
    __tablename__ = "recipe_tag_assoc"

    recipe_id = Column(
        Integer,
        ForeignKey("recipe.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    tag_id = Column(
        Integer,
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )


class Ingredient(Base, UserIdMixin):
    __tablename__ = "ingredient"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(
        Integer, ForeignKey("recipe.id", ondelete="CASCADE"), nullable=False
    )
    quantity = Column(Integer, nullable=False)
    unit = Column(String)
    name = Column(String, nullable=False)
    comment = Column(String)
    input = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    recipe = relationship("Recipe", back_populates="ingredients")
    user_id = association_proxy("recipe", "user_id")


class Step(Base, UserIdMixin):
    __tablename__ = "step"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(
        Integer, ForeignKey("recipe.id", ondelete="CASCADE"), nullable=False
    )
    text = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    recipe = relationship("Recipe", back_populates="steps")
    user_id = association_proxy("recipe", "user_id")


class MealPlanItem(Base, UserIdMixin):
    __tablename__ = "meal_plan_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(
        Integer, ForeignKey("recipe.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(DateTime, nullable=False)
    servings = Column(Integer, nullable=False)
    meal_type = Column(String, nullable=False)
    recipe = relationship("Recipe")
    user_id = association_proxy("recipe", "user_id")


class GroceryList(Base, UserIdMixin):
    __tablename__ = "grocery_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    extra_items = Column(String, nullable=False)
    recipe = relationship("GroceryListItem")


class GroceryListItem(Base, UserIdMixin):
    __tablename__ = "grocery_list_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    grocery_list_id = Column(
        Integer, ForeignKey("grocery_list.id", ondelete="CASCADE"), nullable=False
    )
    active = Column(Boolean, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String)
    name = Column(String, nullable=False)
    comment = Column(String)
    recipe_name = Column(String, nullable=False)
    thumbnail_url = Column(String)
    servings = Column(Integer, nullable=False)
    extra_items = Column(Boolean, nullable=False)
    grocery_list = relationship("GroceryList")
    user_id = association_proxy("grocery_list", "user_id")
