from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Recipe(Base):
    __tablename__ = "recipes"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    instructions: Mapped[str] = mapped_column(Text)
    image: Mapped[str | None] = mapped_column(Text)
    cooking_time: Mapped[int | None] = mapped_column(Integer)
    difficulty: Mapped[str | None] = map(String(150))
    diet_type: Mapped[str | None] = map(String(150))
    style: Mapped[str | None] = map(String(150))
    language: Mapped[str] = mapped_column(String(50), default="en")
    source: Mapped[str] = mapped_column(String(200), default="user")
    
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    amount: Mapped[str | None] = mapped_column(String(50))
    
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recipe_ingredients")
    
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="recipe_ingredients")

    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id", name="uix_recipe_ingredient"),)

