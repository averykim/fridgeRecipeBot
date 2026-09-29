import asyncio
from sqlalchemy.future import select
from deep_translator import GoogleTranslator

from app.core.database import async_session_maker
from app.models.recipes import Recipe, RecipeIngredient
from app.models.ingredients import Ingredient, IngredientAlias

from app.external.fetchers.base import RecipeFetcher
from app.external.fetchers.themealdb import TheMealDBFetcher

# 1. 번역기 헬퍼 함수
def translate(text: str, source: str, target: str) -> str:
    try:
        return GoogleTranslator(source=source, target=target).translate(text).strip()
    except Exception as e:
        print(f"번역 에러 ({text}): {e}")
        return text

# 2. 식재료 통합 처리 (부모=영어, 자식=한국어) 함수
async def get_or_create_ingredient(db, ingredient_name: str, input_lang: str) -> int:
    if input_lang == "ko":
        # 한국어 입력: Alias에서 먼저 검색
        alias_check = await db.execute(select(IngredientAlias).filter(IngredientAlias.alias_name == ingredient_name))
        db_alias = alias_check.scalars().first()
        
        if db_alias:
            return db_alias.ingredient_id
            
        # 없으면 영문으로 번역
        eng_name = translate(ingredient_name, source='ko', target='en')
        kor_name = ingredient_name
    else: 
        # 영어 입력: 바로 영문명 사용하고 한글명 번역
        eng_name = ingredient_name
        kor_name = translate(ingredient_name, source='en', target='ko')

    # 공통 로직: 부모(영어) 확인 및 생성
    ing_check = await db.execute(select(Ingredient).filter(Ingredient.name == eng_name))
    db_ingredient = ing_check.scalars().first()
    
    if not db_ingredient:
        # 부모 생성 (영어 기준)
        db_ingredient = Ingredient(name=eng_name)
        db.add(db_ingredient)
        await db.commit()
        await db.refresh(db_ingredient)
        
        # 자식 생성 (한국어 별칭)
        db_alias = IngredientAlias(
            alias_name=kor_name,
            ingredient_id=db_ingredient.id,
            language="ko"
        )
        db.add(db_alias)
        await db.commit()
        
    return db_ingredient.id

# 3. 메인 Seed 함수
async def seed_database(fetcher: RecipeFetcher, limit: int = 5, input_lang: str = "en"):
    print(f"{fetcher.__class__.__name__}를 통해 레시피를 수집합니다...")
    
    standardized_recipes = await fetcher.fetch(limit=limit) 
    
    async with async_session_maker() as db:
        for recipe_data in standardized_recipes:
            title = recipe_data["title"]
            
            # 🔥 1. 중복 레시피 검증 (새로운 모델에 맞춰 Recipe.title 로 수정)
            existing = await db.execute(select(Recipe).filter(Recipe.title == title))
            if existing.scalars().first():
                print(f"이미 존재하는 레시피 패스: {title}")
                continue
                
            # 🔥 2. 레시피 Insert (최신 모델 필드 매핑)
            new_recipe = Recipe(
                title=title, 
                description=recipe_data.get("description"), # 없을 경우 None
                instructions=recipe_data.get("instructions", ""),
                image=recipe_data.get("image"),             # 없을 경우 None
                cooking_time=recipe_data.get("cooking_time"),
                difficulty=recipe_data.get("difficulty"),
                source=fetcher.__class__.__name__,          # 어떤 API에서 가져왔는지 출처 명시
                language=input_lang 
            )
            db.add(new_recipe)
            await db.commit()
            await db.refresh(new_recipe)
            
            # 3. 식재료 처리 및 매핑
            for ing_name in recipe_data["ingredients"]:
                # 만능 함수로 식재료 ID 발급
                ingredient_id = await get_or_create_ingredient(db, ing_name, input_lang)
                
                # 🔥 4. 레시피-식재료 다대다 연결 (amount 파라미터 추가 반영)
                recipe_ing_link = RecipeIngredient(
                    recipe_id=new_recipe.id,
                    ingredient_id=ingredient_id,
                    # 현재 API 구조상 용량을 분리하지 않았다면 None, 
                    # 나중에 fetcher에서 용량도 추출한다면 recipe_data에서 꺼내서 할당하면 됩니다.
                    amount=None 
                )
                db.add(recipe_ing_link)
            
            await db.commit()
            print(f"저장 완료: {title} (재료 {len(recipe_data['ingredients'])}개)")

# 4. 실행 스크립트 
if __name__ == "__main__":
    fetcher = TheMealDBFetcher()
    asyncio.run(seed_database(fetcher=fetcher, limit=3, input_lang="en"))