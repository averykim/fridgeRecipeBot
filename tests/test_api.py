import pytest
from httpx import AsyncClient

# 비동기 테스트를 위한 데코레이터
@pytest.mark.asyncio
async def test_create_and_get_recipe(async_client: AsyncClient):
    # 1. 식재료 먼저 생성 (레시피 재료로 사용하기 위함)
    ingredient_data = {
        "name": "돼지고기",
        "category": "육류",
        "calories": 300,
        "aliases": [{"alias_name": "pork", "language": "en"}]
    }
    ing_response = await async_client.post("/ingredients/create", json=ingredient_data)
    assert ing_response.status_code == 200
    ingredient_id = ing_response.json()["id"]

    # 2. 레시피 생성 테스트 (앞서 만든 식재료 ID 사용)
    recipe_data = {
        "name": "돼지고기 김치찌개", # Field(min_length=2) 만족
        "steps": "1. 냄비에 돼지고기를 볶는다. 2. 김치를 넣고 푹 끓인다.", # Field(min_length=10) 만족
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
    assert recipe_response.status_code == 200
    
    # 응답 데이터 검증
    created_recipe = recipe_response.json()
    assert created_recipe["name"] == "돼지고기 김치찌개"
    assert len(created_recipe["recipe_ingredients"]) == 1
    assert created_recipe["recipe_ingredients"][0]["amount"] == "200g"
    
    recipe_id = created_recipe["id"]

    # 3. 레시피 단건 조회 테스트 (selectinload가 잘 작동하는지 확인)
    get_response = await async_client.get(f"/recipes/{recipe_id}")
    assert get_response.status_code == 200
    
    fetched_recipe = get_response.json()
    assert fetched_recipe["id"] == recipe_id
    assert fetched_recipe["steps"].startswith("1. 냄비에")