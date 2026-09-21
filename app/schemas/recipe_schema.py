from typing import Optional
from pydantic import BaseModel, ConfigDict

class RecipeBase(BaseModel):
    name: str