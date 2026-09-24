from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.recipes import Recipe, RecipeIngredient
from app.models.ingredients import Ingredient, IngredientAlias

async def find_recipe_in_db(db: AsyncSession,
                            ingredient_names:list[str],
                            style: str | None = None,
                            diet_type: str | None = None,
                            language: str = "en"
                            ):
    # 1. convert ingredients to ingredient id array
    stmt_ids = select(Ingredient.id).outerjoin(IngredientAlias).where(
        (Ingredient.name.in_(ingredient_names)) | 
        (IngredientAlias.alias_name.in_(ingredient_names)))
    result_ids = await db.execute(stmt_ids)
    user_ingredient_ids = result_ids.scalars().all()
    
    if not user_ingredient_ids:
        return None 
    
    # 2. Search recipes
    stms_match = (select(Recipe)
                  .options(selectinload(Recipe.recipe_ingredients))
                  .join(RecipeIngredient)
                  .where(RecipeIngredient.ingredient_id.in_(user_ingredient_ids))
                  .group_by(Recipe.id)
                  .having(
                      func.count(RecipeIngredient.ingredient_id) == (
                          select(func.count(RecipeIngredient.ingredient_id))
                          .where(RecipeIngredient.recipe_id == Recipe.id)
                          .scalar_subquery()
                          )
                  )
    )
    
    if style or diet_type:
        stms_match == stms_match.where(Recipe.style == style | diet_type == diet_type)
        result_match = await db.execute(stms_match)
        
    return result_match.scalar_one_or_none()