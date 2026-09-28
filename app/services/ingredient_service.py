from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.models.ingredients import Ingredient, IngredientAlias
from app.schemas.ingredient_schema import IngredientCreate, IngredientResponse


async def create_ingredients_in_db(db: AsyncSession, ingredient:IngredientCreate):
    db_ingredient = Ingredient(
        name=ingredient.name, 
        category=ingredient.category,
        calories=ingredient.calories
        )
    
    db.add(db_ingredient)
    await db.commit()
    await db.refresh(db_ingredient)
    # if aliases exist
    if ingredient.aliases:
        for alias_data in ingredient.aliases:
            db_alias = IngredientAlias(alias_name=alias_data.alias_name,
                                        ingredient_id=db_ingredient.id,  # connect parent's id from above
                                        language=alias_data.language
                                        )
            db.add(db_alias)
    await db.commit()
    await db.refresh(db_ingredient, attribute_names=['aliases'])

    return db_ingredient

async def search_ingredients(db: AsyncSession, keyword: str):
    stmt = (select(Ingredient)
            .outerjoin(IngredientAlias, Ingredient.id == IngredientAlias.ingredient_id)
            .where(
                or_(Ingredient.name.ilike(f"%{keyword}%"),
                    IngredientAlias.alias_name.ilike(f"%{keyword}%"))
                    )
            ).distinct().limit(10)

    result = await db.execute(stmt)
    return result.scalars().all()

async def get_ingredient_by_id(db: AsyncSession, ingredient_id: int):
    stmt = select(Ingredient).options(selectinload(Ingredient.aliases)).where(Ingredient.id == ingredient_id)
    result = await db.execute(stmt)
        
    return result.scalar_one_or_none()