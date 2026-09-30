from abc import ABC, abstractmethod
from typing import List
from app.schemas.recipe_schema import RecipeCreate

class RecipeFetcher(ABC):
    @abstractmethod
    async def fetch(self, limit: int = 10) -> List[RecipeCreate]:
        """
        Return format
        [
            {
                "title: "Recipe Name",
                "instructions": "STEPS",
                "ingredients": ["ingredient 1", "ingredient 2"]
            }
        ]
        """
        pass