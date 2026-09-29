import asyncio
from sqlalchemy import select
from deep_translator import GoogleTranslator

from app.core.database import async_session_maker
from app.models.recipes import Recipe, RecipeIngredient
from app.models.ingredients import Ingredient, IngredientAlias

from app.external.fetchers.base import RecipeFetcher
from app.external.fetchers.themealdb import TheMealDBFetcher


# 1. Translator helpe
def translate(text_list: list[str], source: str, target: str) -> list[str]:
    if not text_list:
        return []
    try:
        # join words by \n to make one sentence
        combined_text = "\n".join(text_list)
        
        # one time request
        translated_text = GoogleTranslator(source=source, target=target).translate(combined_text)
        
        # divide words by \n
        return [t.strip() for t in translated_text.split("\n") if t.strip()]
    except Exception as e:
        print(f"Translator error: {e}")
        return text_list # fail => return english list

# 2. Ingredient DB
async def get_or_create_ingredient(db, eng_name: str, fo_name: str, lang: str) -> int:
    eng_name = eng_name.strip().lower()
    fo_name = fo_name.strip()
    
    # Check english name is in DB
    ing_check = await db.execute(select(Ingredient).filter(Ingredient.name == eng_name))
    db_ingredient = ing_check.scalars().first()
    
    if not db_ingredient:
        # Create parent
        db_ingredient = Ingredient(name=eng_name)
        db.add(db_ingredient)
        await db.commit()
        await db.refresh(db_ingredient)
        
        # Create child
        db_alias = IngredientAlias(
            alias_name=fo_name,
            ingredient_id=db_ingredient.id,
            language=lang
        )
        db.add(db_alias)
        await db.commit()
    
    return db_ingredient.id

# 3. main seed
async def seed_database(fetcher: RecipeFetcher, limit: int = 5, input_lang: str = "en"):
    print(f"{fetcher.__class__.__name__}를 통해 레시피를 수집합니다...")
    
    standardized_recipes = await fetcher.fetch(limit=limit) 
    
    async with async_session_maker() as db:
        for recipe_data in standardized_recipes:
            title = recipe_data["title"]
            
            # 1. validate overlapping
            existing = await db.execute(select(Recipe).filter(Recipe.title == title))
            if existing.scalars().first():
                print(f"already exists recipe: {title}")
                continue
                
            # 2. Recipe Insert
            new_recipe = Recipe(
                title=title, 
                description=recipe_data.get("description"),
                instructions=recipe_data.get("instructions", ""),
                image=recipe_data.get("image"),
                cooking_time=recipe_data.get("cooking_time"),
                difficulty=recipe_data.get("difficulty"),
                source=fetcher.__class__.__name__,
                language=input_lang 
            )
            db.add(new_recipe)
            await db.commit()
            await db.refresh(new_recipe)
            
            # Batch translate
            raw_ingredients = recipe_data.get("ingredients", [])
            eng_names = []
            kor_names = []
            
            if raw_ingredients:
                try:
                    if input_lang == "en":
                        eng_names = raw_ingredients
                        kor_names = translate(text_list=raw_ingredients, source="en", target="ko")
                    else:
                        eng_names = translate(text_list=raw_ingredients, source="ko", target="en")
                        kor_names = raw_ingredients
                except Exception as e:
                    print(f"batch translate error ({title}): {e}")
                    eng_names = raw_ingredients
                    kor_names = raw_ingredients
            
            added_ingredient_ids = set()
                    
            # Save ingredients into DB and recipe mapping
            for eng, kor in zip(eng_names, kor_names):
                if not eng:
                    continue
                
                ingredient_id = await get_or_create_ingredient(db, eng, kor, "ko")
                
                if ingredient_id in added_ingredient_ids:
                    continue
                
                # New ingredient -> remember ID
                added_ingredient_ids.add(ingredient_id)
                
                recipe_ing_link = RecipeIngredient(
                    recipe_id=new_recipe.id,
                    ingredient_id=ingredient_id,
                    amount=None
                )
                db.add(recipe_ing_link)
                
            print(f"Saved: {title} (ingredient {len(raw_ingredients)}개)")
            
            # Wait 1 second before translate next recipe
            await asyncio.sleep(1)

# 4. execute script
if __name__ == "__main__":
    fetcher = TheMealDBFetcher()
    asyncio.run(seed_database(fetcher=fetcher, limit=3, input_lang="en"))