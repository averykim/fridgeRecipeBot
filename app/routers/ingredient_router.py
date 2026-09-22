from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

#schema
from schemas.ingredient_schema import IngredientResponse, IngredientCreate
#models
from models.ingredients import Ingredient, IngredientAlias
#db
from core.database import get_db

router = APIRouter(prefix='/ingredients', tags=['Ingredients'])

@router.post('/create', response_model=IngredientResponse)
async def create_ingredient(ingredient_in: IngredientCreate, db: AsyncSession = Depends(get_db)):
    db_ingredient = Ingredient(
        name=ingredient_in.name, 
        category=ingredient_in.category,
        calories=ingredient_in.calories
    )

    db.add(db_ingredient)
    await db.commit()
    await db.refresh(db_ingredient)
    # if aliases exist
    if ingredient_in.aliases:
        for alias_data in ingredient_in.aliases:
            db_alias = IngredientAlias(alias_name=alias_data,
                                       ingredient_id=db_ingredient.id,  # connect parent's id from above
                                       language=alias_data.language
                                       )
            db.add(db_alias)
    await db.commit()
    await db.refresh(db_ingredient, attribute_names=['aliases'])

    return db_ingredient

@router.get("/{ingredient_id}", response_model=IngredientResponse)
async def get_ingredient(ingredient_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Ingredient).options(selectinload(Ingredient.aliases)).where(Ingredient.id == ingredient_id)
    result = await db.execute(stmt)
    
    db_ingredient = result.scalar_one_or_none()
    
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Cannot find the ingredient")
    
    return db_ingredient