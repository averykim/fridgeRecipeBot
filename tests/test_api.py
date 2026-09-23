import pytest
from httpx import AsyncClient

# decorator for testing async
@pytest.mark.asyncio
async def test_create_and_get_recipe(async_client: AsyncClient):
    # 1. create ingredient first for recipe
    ingredient_data = {
        "name": "돼지고기",
        "category": "Meat",
        "calories": 300,
        "aliases": [{"alias_name": "Pork", "language": "en"}]
    }
    ing_response = await async_client.post("/ingredients/create", json=ingredient_data)
    assert ing_response.status_code == 200, ing_response.json()
    ingredient_id = ing_response.json()["id"]

    # 2. Create recipe (use ingredient id that generating above)
    recipe_data = {
        "name": "돼지고기 김치찌개", # Field(min_length=2) True
        "steps": "1. 냄비에 돼지고기를 볶는다. 2. 김치를 넣고 푹 끓인다.", # Field(min_length=10) True
        "image": "http://example.com/kimchi.jpg",
        "cooking_time": 30,
        "language": "ko",
        "recipe_ingredients": [
            {
                "ingredient_id": ingredient_id,
                "amount": "200g"
            }
        ]
    }
    
    recipe_response = await async_client.post("/recipes/create", json=recipe_data)
    assert recipe_response.status_code == 200, recipe_response.json()
    
    # Validate Response data
    created_recipe = recipe_response.json()
    assert created_recipe["name"] == "돼지고기 김치찌개"
    assert len(created_recipe["recipe_ingredients"]) == 1
    assert created_recipe["recipe_ingredients"][0]["amount"] == "200g"
    
    recipe_id = created_recipe["id"]

    # 3. Search single recipe (check that selectinload is working)
    get_response = await async_client.get(f"/recipes/{recipe_id}")
    assert get_response.status_code == 200
    
    fetched_recipe = get_response.json()
    assert fetched_recipe["id"] == recipe_id
    assert fetched_recipe["steps"].startswith("1. 냄비에")