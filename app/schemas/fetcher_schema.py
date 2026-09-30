from typing import Optional, List
from pydantic import BaseModel

class ParsedIngredient(BaseModel):
    name: str
    amount: Optional[str] = None
    

class ParsedRecipe(BaseModel):
    title: str
    instructions: str
    image: Optional[str] = None
    style: Optional[str] = None
    source: str
    ingredients: List[ParsedIngredient]
    