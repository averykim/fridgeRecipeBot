from typing import Optional
from pydantic import BaseModel, ConfigDict

class IngredientAliasBase(BaseModel):
    alias_name: str
    language: str = "en"
    
class IngredientAliasResponse(IngredientAliasBase):
    id: int
    ingredient_id: int

# Common (Create and Response)
class IngredientBase(BaseModel):
    name: str
    category: str
    calories: Optional[int] = None
    
# Data create: client -> API
class IngredientCreate(IngredientBase):
    aliases: Optional[list[str]] = []
    
# Data response: API -> client
class IngredientResponse(IngredientBase):
    id: int
    aliases: list[IngredientAliasResponse] = []
    
    model_config = ConfigDict(from_attributes=True)