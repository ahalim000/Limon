from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from server.storage.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = synonym("id")


class Recipe(Base):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String)
    source: Mapped[str] = mapped_column(String, nullable=False, default="")
    servings: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    servings_type: Mapped[str] = mapped_column(String, nullable=False, default="")
    prep_time: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cook_time: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    nutrition: Mapped[str] = mapped_column(String, nullable=False, default="")
    favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredients: Mapped[List["Ingredient"]] = relationship(
        "Ingredient", back_populates="recipe", cascade="all, delete-orphan"
    )
    steps: Mapped[List["Step"]] = relationship(
        "Step", back_populates="recipe", cascade="all, delete-orphan"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="recipe_tag_assoc",
        back_populates="recipes",
        cascade="all, delete",
        passive_deletes=True,
    )


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    recipes: Mapped[List["Recipe"]] = relationship(
        "Recipe",
        secondary="recipe_tag_assoc",
        back_populates="tags",
        cascade="all, delete",
        passive_deletes=True,
    )


class RecipeTagAssoc(Base):
    __tablename__ = "recipe_tag_assoc"

    recipe_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recipe.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )


class Ingredient(Base):
    __tablename__ = "ingredient"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipe.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1)
    unit: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(String)
    input: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ingredients")
    user_id: AssociationProxy[int] = association_proxy("recipe", "user_id")


class Step(Base):
    __tablename__ = "step"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipe.id", ondelete="CASCADE"), nullable=False
    )
    text: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="steps")
    user_id: AssociationProxy[int] = association_proxy("recipe", "user_id")


class MealPlanItem(Base):
    __tablename__ = "meal_plan_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipe.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    servings: Mapped[int] = mapped_column(Integer, nullable=False)
    meal_type: Mapped[str] = mapped_column(String, nullable=False, default="Dinner")
    recipe: Mapped["Recipe"] = relationship("Recipe")
    user_id: AssociationProxy[int] = association_proxy("recipe", "user_id")


class GroceryList(Base):
    __tablename__ = "grocery_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    extra_items: Mapped[str] = mapped_column(String, nullable=False, default="")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    grocery_list_items: Mapped[List["GroceryListItem"]] = relationship(
        "GroceryListItem", back_populates="grocery_list", cascade="all, delete-orphan"
    )


class GroceryListItem(Base):
    __tablename__ = "grocery_list_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    grocery_list_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grocery_list.id", ondelete="CASCADE"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(String)
    recipe_name: Mapped[str] = mapped_column(String, nullable=False)
    servings: Mapped[int] = mapped_column(Integer, nullable=False)
    extra_items: Mapped[bool] = mapped_column(Boolean, nullable=False)
    grocery_list: Mapped["GroceryList"] = relationship(
        "GroceryList", back_populates="grocery_list_items"
    )
    user_id: AssociationProxy[int] = association_proxy("grocery_list", "user_id")
