from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    amount: Optional[str] = None

class RecipeIngredientCreate(RecipeIngredientBase):
    pass

class RecipeIngredientResponse(RecipeIngredientBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class RecipeBase(BaseModel):
    name: str = Field(min_length=2)
    steps: str = Field(min_length=10)
    image: Optional[str] = None
    cooking_time: Optional[int] = None
    language: str = "en"
    
class RecipeCreate(RecipeBase):
    recipe_ingredients: List[RecipeIngredientCreate]

class RecipeResponse(RecipeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    recipe_ingredients: List[RecipeIngredientCreate] = []
    model_config = ConfigDict(from_attributes=True)