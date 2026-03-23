import os

APP_ENV = os.getenv("APP_ENV", "docker").lower()

# API: TheMealDB
# www.themealdb.com/api/json/v1/1/list.php?i=list
THEMEALDB_KEY = os.getenv("THEMEALDB_KEY", "1")
THEMEALDB_BASE = f"https://www.themealdb.com/api/json/v1/{THEMEALDB_KEY}"
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "6.0"))
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "false").lower() == "true"

if APP_ENV == "local":
    ING_URL = "http://localhost:5001/recognize"
    INTENT_URL = "http://localhost:5004/intent"
    SEARCH_URL = "http://localhost:5002/search"
    GEN_URL    = "http://localhost:5003/generate"
    MONGO_URI  = "mongodb://localhost:27017/recipe_db"
else:
    ING_URL    = os.getenv("ING_URL",    "http://ingredient_recognition:5001/recognize")
    INTENT_URL    = os.getenv("INTENT_URL", "http://intent_recognition:5004/intent")
    SEARCH_URL = os.getenv("SEARCH_URL", "http://recipe_search:5002/search")
    GEN_URL    = os.getenv("GEN_URL",    "http://response_generator:5003/generate")
    MONGO_URI  = os.getenv("MONGO_URI",  "mongodb://mongo:27017/recipe_db")
