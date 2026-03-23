from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class IngredientAlias(Base):
     __tablename__ = "ingredients_aliases"

