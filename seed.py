import asyncio
from sqlalchemy.future import select

from app.core.database import async_session_maker
from app.models.recipes import Recipe
from app.models.ingredients import Ingredient

from app.external.fetchers.base import RecipeFetcher
from app.external.fetchers.themealdb import TheMealDBFetcher

async def seed_database(fetcher: RecipeFetcher, limit: int = 10):
    print(f"{fetcher.__class__.__name__}를 통해 레시피를 수집합니다...")
    # 어댑터가 내부적으로 API 호출 및 표준화를 완료하여 반환
    standardized_recipes = await fetcher.fetch(limit=limit)
    
    async with async_session_maker() as db:
        for recipe_data in standardized_recipes:
            title = recipe_data["title"]
            
            # 1. 중복 레시피 검증
            existing = await db.execute(select(Recipe).filter(Recipe.title == title))
            if existing.scalars().first():
                print(f"이미 존재하는 레시피 패스: {title}")
                continue
                
            # 2. 레시피 기본 정보 Insert
            new_recipe = Recipe(
                title=title,
                description=recipe_data["description"],
                instructions=recipe_data["instructions"],
                cooking_time=recipe_data["cooking_time"],
                difficulty=recipe_data["difficulty"]
            )
            db.add(new_recipe)
            
            # 3. 식재료 (Ingredients) 조회 및 Insert
            for ing_name in recipe_data["ingredients"]:
                ing_check = await db.execute(select(Ingredient).filter(Ingredient.name == ing_name))
                if not ing_check.scalars().first():
                    new_ing = Ingredient(name=ing_name)
                    db.add(new_ing)
                    
            # TODO: 레시피-식재료 다대다 연결(RecipeIngredient) 매핑 로직 추가 필요
            
            await db.commit()
            print(f"저장 완료: {title} (재료 {len(recipe_data['ingredients'])}개)")

if __name__ == "__main__":
    # 원하는 수집기 인스턴스를 주입(DI)하여 실행
    fetcher = TheMealDBFetcher()
    asyncio.run(seed_database(fetcher=fetcher, limit=3))