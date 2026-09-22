from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.orm import selectinload
from typing import List

#schema
from schemas.recipe_schema import RecipeResponse, RecipeCreate
#models
from models.recipes import Recipe, RecipeIngredient
#db
from core.database import get_db

router = APIRouter(prefix='/recipes', tags=['Recipes'])

@router.post('/create', response_model=RecipeResponse)
async def create_recipe(recipe_in: RecipeCreate, db: AsyncSession = Depends(get_db)):
    db_recipe = Recipe(
        name=recipe_in.name, 
        steps=recipe_in.steps,
        image=recipe_in.image,
        cooking_time=recipe_in.cooking_time,
        language=recipe_in.language
    )

    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)

    for ingredient in recipe_in.recipe_ingredients:
        db_ingredient = RecipeIngredient(
            recipe_id=db_recipe.id,
            ingredient_id=ingredient.ingredient_id,
            amount=ingredient.amount
        )
        db.add(db_ingredient)
        
    await db.commit()
    await db.refresh(db_recipe, attribute_names=['recipe_ingredients'])

    return db_recipe

@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Recipe).options(selectinload(Recipe.recipe_ingredients)).where(Recipe.id == recipe_id)
    result = await db.execute(stmt)
    
    db_recipe = result.scalar_one_or_none()
    
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Cannot find the recipe")
    
    return db_recipe