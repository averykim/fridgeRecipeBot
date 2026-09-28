import httpx
from typing import List, Dict, Any
from app.external.fetchers.base import RecipeFetcher

# TheMealDB Adapter
class TheMealDBFetcher(RecipeFetcher):
    async def fetch(self, limit = 10) -> List[Dict[str, Any]]:
        url = "https://www.themealdb.com/api/json/v1/1/random.php"
        standardized_recipes = []
        async with httpx.AsyncClient() as client:
            for _ in range(limit):
                response = await client.get(url)
                if response.status_code != 200:
                    continue
                
                data = response.json()
                if not data.get("meals"):
                    continue
                
                meal = data["meals"][0]
                
                # parse
                ingredients = []
                for i in range(1, 21):
                    ing_name = meal.get(f"strIngredient{i}")
                    if ing_name and ing_name.strip():
                        ingredients.append(ing_name.strip().lower())
                        
                # Convert data structure
                standardized_recipes.append({
                    "title": meal.get("strMeal"),
                    "description": f"Category: {meal.get('strCategory')}, Area: {meal.get('strArea')}",
                    "instructions": meal.get("strInstructions"),
                    "cooking_time": 30,
                    "difficulty": "Medium",
                    "ingredients": ingredients
                })
        return standardized_recipes