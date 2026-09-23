from fastapi import FastAPI
from app.routers.ingredient_router import router  as ingredient_router
from app.routers.recipe_router import router as recipe_router

app = FastAPI(title="NAENGPA")

app.include_router(ingredient_router)
app.include_router(recipe_router)

@app.get("/")
async def root():
    return {"message": "naengpa API server is running."}