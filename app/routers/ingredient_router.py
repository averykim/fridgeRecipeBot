from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

#schema
from app.schemas.ingredient_schema import IngredientResponse, IngredientCreate
#models
from app.models.ingredients import Ingredient, IngredientAlias
#db
from app.core.database import get_db
#service
from app.services.ingredient_service import search_ingredients, get_ingredient_by_id, create_ingredients_in_db

router = APIRouter(prefix='/ingredients', tags=['Ingredients'])

@router.post('/create', response_model=IngredientResponse)
async def create_ingredient(ingredient_in: IngredientCreate, db: AsyncSession = Depends(get_db)):
    return await create_ingredients_in_db(db=db, ingredient=ingredient_in)

@router.get("/{ingredient_id}", response_model=IngredientResponse)
async def get_ingredient(ingredient_id: int, db: AsyncSession = Depends(get_db)):
    db_ingredient = await get_ingredient_by_id(db=db, ingredient_id=ingredient_id)
    
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Cannot find the ingredient")
    
    return db_ingredient

@router.get('/search', response_model=List[IngredientResponse])
async def search_ingredient_api(keyword: str = Query(..., min_length=1, description="Part of searching ingredient"),
                                db:AsyncSession = Depends(get_db)):
    results = await search_ingredients(db=db, keyword=keyword)
    return results