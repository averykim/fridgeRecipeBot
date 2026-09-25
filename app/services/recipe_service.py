from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.recipes import Recipe, RecipeIngredient
from app.schemas.recipe_schema import RecipeCreate

# GET
async def get_recipe_by_id(db: AsyncSession, recipe_id: int) -> Recipe | None:
    stmt = select(Recipe).options(selectinload(Recipe.recipe_ingredients)).where(Recipe.id == recipe_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# POST
async def create_recipe_in_db(db: AsyncSession, recipe_in: RecipeCreate) -> Recipe:
    db_recipe = Recipe(
        title=recipe_in.title, 
        description=recipe_in.description,
        instructions=recipe_in.instructions,
        image=recipe_in.image,
        cooking_time=recipe_in.cooking_time,
        difficulty=recipe_in.difficulty,
        diet_type=recipe_in.diet_type,
        style=recipe_in.style,
        language=recipe_in.language,
        source="user"
    )
    
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    
    # add RecipeIngredient (Recipe-Ingredient data mapping)
    if recipe_in.recipe_ingredients:
        for ingredient in recipe_in.recipe_ingredients:
            db_ingredient = RecipeIngredient(
                recipe_in=db_recipe.id,
                ingredient_id=ingredient.ingredient_id,
                amount=ingredient.amount
            )
            db.add(db_ingredient)
        await db.commit()
        
    await db.refresh(db_recipe, attribute_names=['recipe_ingredients'])
    return db_recipe
    