from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Ingredient(Base):
    __tablename__ = "ingredients"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    category: Mapped[str | None] = mapped_column(String(50))
    calories: Mapped[int | None] = mapped_column(Integer)
    
    aliases: Mapped[list["IngredientAlias"]] = relationship(back_populates="ingredient", cascade="all, delete-orphan")
    
    
class IngredientAlias(Base):
    __tablename__ = "ingredient_aliases"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)