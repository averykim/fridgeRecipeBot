from flask import Flask, request, jsonify
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
import settings
import logging, os, time
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Connect MongoDB 
client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=30000)
db = client.get_default_database()  # recipe_db
recipes_collection = db.recipes

# Indexing
recipes_collection.create_index([("source", ASCENDING), ("source_id", ASCENDING)], unique = True)
recipes_collection.create_index([("ingredients", ASCENDING)])
recipes_collection.create_index([("cached_at", DESCENDING)])

def norm(s:str) -> str:
    return (s or "").strip().lower()

def extract_ingredients(meal: dict) -> list[str]:
    out = []
    for i in range(1, 21):
        value = meal.get(f"strIngredient{i}")
        if value and value.strip():
            out.append(norm(value))
    return sorted(set([x for x in out if x]))

def themealdb_filter_by_ingredient(ingredient: str) -> list[str]:
    url = f"{settings.THEMEALDB_BASE}/filter.php"
    r = requests.get(url, params = {"i": ingredient}, timeout = settings.HTTP_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    meals = data.get("meals") or []
    return [m.get("idMeal") for m in meals if m.get("idMeal")]

def themealdb_lookup(meal_id:str) -> dict | None:
    url = f"{settings.THEMEALDB_BASE}/lookup.php"
    r = requests.get(url, params = {"i": meal_id}, timeout = settings.HTTP_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    arr = data.get("meals") or []
    return arr[0] if arr else None

def cache_meal_to_db(meal: dict) -> None:
    ing = extract_ingredients(meal)
    doc = {
        "name": meal.get("strMeal") or "",
        "instructions": meal.get("strInstructions") or "",
        "ingredients": ing,
        "source": "themealdb",
        "source_id": meal.get("idMeal"),
        "cached_at": int(time.time()),
        "raw": meal,
    }
    if not doc["source_id"]:
        return
    
    recipes_collection.update_one(
        {"source": doc["source"], "source_id": doc["source_id"]},
        {"$set": doc},
        upsert = True
    )

# lookup and cache
def fetch_from_api(ingredients: list[str], max_ids: int = 20) -> int:
    ids = set()
    for ing in ingredients:
        ing = norm(ing)
        if not ing:
            continue
        
        # filter
        try:
            for mid in themealdb_filter_by_ingredient(ing):
                ids.add(mid)
                if len(ids) >= max_ids:
                    break

        except requests.RequestException as e:
            app.logger.error(e)
        if len(ids) >= max_ids:
            break

    # Lookup
    added = 0
    for mid in list(ids):
        try:
            meal = themealdb_lookup(mid)
            if not meal:
                break
            cache_meal_to_db(meal)
            added += 1
        except (requests.RequestException, PyMongoError):
            continue
    return added

# Search and sorted by number of matching ingredients
def db_search_scored(ingredients: list[str], limit: int = 10) -> list[dict]:
    if not ingredients:
        return []
    cursor = recipes_collection.find(
        {
            "ingredients": {"$in": ingredients}
        },
        {
            "_id": 0,
            "name": 1,
            "instructions": 1,
            "ingredients": 1,
            "cached_at": 1
            }
    ).limit(limit)

    results = list(cursor)
    ing_set = set(ingredients)
    for r in results:
        recipe_ing = set(r.get("ingredients", []))

        # Matching ingredients
        matched = ing_set.intersection(recipe_ing)

        # Missing ingredients
        missing = recipe_ing - ing_set

        r["matched"] = list(matched)
        r["missing"] = list(missing)

        r["_score"] = len(matched)

    results.sort(key=lambda x: (x["_score"], x.get("cached_at", 0)), reverse = True)
    
    return results

# Check if a server is responding to commands
@app.route("/health", methods=["GET"])
def health():
    try:
        client.admin.command("ping")
        return jsonify({"status": "ok", "env": settings.APP_ENV, "offline_mode": settings.OFFLINE_MODE}), 200
    except Exception as e:
        app.logger.exception("Mongo ping failed")
        return jsonify({"status": "bad", "error": str(e)}), 500

@app.route("/search", methods=["POST"])
def search_recipes():
    try:
        data = request.get_json(silent=True) or {}
        ingredients = [norm(s) for s in data.get("ingredients", []) if s and norm(s)]
        limit = int(data.get("limit", 10))

        # If there is no ingredients then always return empty list with 200 status
        if not ingredients:
            return jsonify({"recipes": []}), 200
        
        # 1. DB first
        recipes_list = db_search_scored(ingredients, limit=limit)
        if len(recipes_list) >= limit or settings.OFFLINE_MODE:
            return jsonify({
                "mode": "db_only" if settings.OFFLINE_MODE else "db_cache",
                "recipes": recipes_list
            }), 200
        
        # 2. Use API if there is no data in db
        cached_added = fetch_from_api(ingredients, max_ids=20)

        # 3. Retrieve data from DB again
        recipes_list = db_search_scored(ingredients, limit=limit)

        return jsonify({
            "mode": "api_and_cache",
            "cached_added": cached_added,
            "recipes": recipes_list
        }), 200

    except PyMongoError as e:
        app.logger.exception("Mongo query failed")
        return jsonify({"error": f"DB error: {e}"}), 500
    except Exception as e:
        app.logger.exception("Unexpected error in /search")
        return jsonify({"error": f"Server error: {e}"}), 500

if __name__ == "__main__":
    print(f"[search] APP_ENV={settings.APP_ENV}, MONGO_URI={settings.MONGO_URI}")
    app.run(debug=True, host="0.0.0.0", port=5002)
