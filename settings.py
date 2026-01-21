import os

APP_ENV = os.getenv("APP_ENV", "docker").lower()

if APP_ENV == "local":
    ING_URL    = os.getenv("ING_URL",    "http://localhost:5001/recognize")
    SEARCH_URL = os.getenv("SEARCH_URL", "http://localhost:5002/search")
    GEN_URL    = os.getenv("GEN_URL",    "http://localhost:5003/generate")
    MONGO_URI  = os.getenv("MONGO_URI",  "mongodb://localhost:27017/recipe_db")
else:
    ING_URL    = os.getenv("ING_URL",    "http://ingredient_recognition:5001/recognize")
    SEARCH_URL = os.getenv("SEARCH_URL", "http://recipe_search:5002/search")
    GEN_URL    = os.getenv("GEN_URL",    "http://response_generator:5003/generate")
    MONGO_URI  = os.getenv("MONGO_URI",  "mongodb://mongo:27017/recipe_db")
