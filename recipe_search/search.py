from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from settings import APP_ENV, MONGO_URI
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Connect MongoDB 
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000)
db = client.get_default_database()  # recipe_db
recipes_collection = db.recipes

#c Check if a server is responding to commands
@app.route("/health", methods=["GET"])
def health():
    try:
        client.admin.command("ping")
        return jsonify({"status": "ok", "env": APP_ENV}), 200
    except Exception as e:
        app.logger.exception("Mongo ping failed")
        return jsonify({"status": "bad", "error": str(e)}), 500

@app.route("/search", methods=["POST"])
def search_recipes():
    try:
        data = request.get_json(silent=True) or {}
        ingredients = [s.strip().lower() for s in data.get("ingredients", []) if s and s.strip()]

        # If there is no ingredients then always return empty list with 200 status
        if not ingredients:
            return jsonify({"recipes": []}), 200

        # Mongo Query: Include all ingredients ($all)
        query = recipes_collection.find({"ingredients": {"$all": ingredients}})
        recipes = list(query)
        recipes_list = [{"name": r.get("name",""), "instructions": r.get("instructions","")} for r in recipes]

        return jsonify({"recipes": recipes_list}), 200

    except PyMongoError as e:
        app.logger.exception("Mongo query failed")
        return jsonify({"error": f"DB error: {e}"}), 500
    except Exception as e:
        app.logger.exception("Unexpected error in /search")
        return jsonify({"error": f"Server error: {e}"}), 500

if __name__ == "__main__":
    print(f"[search] APP_ENV={APP_ENV}, MONGO_URI={MONGO_URI}")
    app.run(debug=True, host="0.0.0.0", port=5002)
