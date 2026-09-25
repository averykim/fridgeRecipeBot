from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

#schema
from app.schemas.recipe_schema import RecipeResponse, RecipeCreate
#models
from app.models.recipes import Recipe, RecipeIngredient
#db
from app.core.database import get_db

#services
from app.services.recommend_service import find_recipe_in_db
from app.services.ai_recipe_service import generate_recipe_ai
from app.services.recipe_service import get_recipe_by_id, create_recipe_in_db

router = APIRouter(prefix='/recipes', tags=['Recipes'])

@router.post('/recommend', RecipeResponse)
async def recommend_recipe(ingredients: List[str] = Body(..., description="List of ingredients input by the user"),
                           style: str = Body("home cooking", description="Desired cooking style"),
                           diet_type: str | None = Body(None, description="Dietary restrictions"),
                           language: str = Body("en", description="Requested language code (ko, en, etc.)"),
                           db: AsyncSession = Depends(get_db)):
    
    # 1. Search matched recipe in the db first
    match_recipe = await find_recipe_in_db(db=db,
                                           ingredients_name=ingredients,
                                           style=style,
                                           language=language
                                           )
    
    if match_recipe:
        return match_recipe
    
    # 2. If not found in DB, use AI
    ai_recipe_data = await generate_recipe_ai(ingredients=ingredients,
                                              style=style,
                                              diet_type=diet_type,
                                              language=language
                                              )
    
    # 3. Save new recipe from AI in te DB
    new_recipe = Recipe(
        title=ai_recipe_data.title,
        description=ai_recipe_data.description,
        instructions=ai_recipe_data.instructions,
        cooking_time=ai_recipe_data.cooking_time,
        difficulty=ai_recipe_data.difficulty,
        style=style,
        diet_type=diet_type,
        language=language,
        source="gemini"
    )
    
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe, attribute_names=['recipe_ingredients'])

    return new_recipe
    

# User creates own recipe
@router.post('/create', response_model=RecipeResponse)
async def create_recipe(recipe_in: RecipeCreate, db: AsyncSession = Depends(get_db)):
    return create_recipe_in_db(db=db, recipe_in=recipe_in)


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    db_recipe = await get_recipe_by_id(db=db, recipe_id=recipe_id)
    
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Cannot find the recipe")
    
    return db_recipe