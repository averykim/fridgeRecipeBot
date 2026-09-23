from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    category: Mapped[str | None] = mapped_column(String(50))
    calories: Mapped[int | None] = mapped_column(Integer)
    
    aliases: Mapped[list["IngredientAlias"]] = relationship("IngredientAlias", back_populates="ingredient", cascade="all, delete-orphan")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan"
    )

class IngredientAlias(Base):
    __tablename__ = "ingredient_aliases"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    alias_name: Mapped[str] = mapped_column(String(50))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="aliases")
    language:Mapped[str] = mapped_column(String(50), default="en")