from fastapi import FastAPI
from app.routers.ingredient_router import router  as ingre_router
from app.routers.recipe_router import router as re_router

app = FastAPI()

app.include_router(ingre_router)
app.include_router(re_router)