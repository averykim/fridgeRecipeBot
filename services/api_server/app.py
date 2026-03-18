from flask import Flask, request, jsonify, render_template
import requests, os, time
import settings

app = Flask(__name__)

def call_with_retry(method, url, **kwargs):
    for i in range(6):
        try:
            print(f"[call_with_retry] Sending to {url} with data: {kwargs.get('json')}", flush=True)
            return requests.request(method, url, timeout=10, **kwargs)
        except requests.exceptions.ConnectionError:
            if i == 5:
                raise
            time.sleep(1.5)

@app.route('/')
def index():
    # Render the HTML file when accessing the root URL
    return render_template('index.html')

@app.route('/get_info', methods=['POST'])
def get_info():
    # Get the user's ingredient input
    data = request.json or {}
    print(f"[api_server] Raw request.json: {data}", flush=True)
    ingredients = data.get("ingredients", [])
    print(f"[api_server] Extracted ingredients: {ingredients}", flush=True)

    # Steo 0: Build a text string for intent classification
    intent_text = " ".join(ingredients) if isinstance(ingredients, list) else str(ingredients)
    intent_r = call_with_retry("POST", settings.INTENT_URL, json={"text": intent_text})
    intent_r.raise_for_status()
    intent_data = intent_r.json()
    intent = intent_data.get("intent", "ingredients_query")
    constraints = intent_data.get("constraints", {}) or {}

    # Handle Non-recipe intents
    if intent in ("help", "greeting", "thanks"):
        msg = {
            "help": "Enter ingredients like: chicken, garlic, onion. You can also add constraints like 'under 20 minutes' or 'easy'.",
            "greeting": "Hi!, Tell me what ingredients you have, and I'll suggest recipes.",
            "thanks": "You're welcome! Want another recipe recommnedation?"
        }[intent]
        return jsonify({"recipes": [], "message": msg, "intent": intent}), 200
    
    # Step 1: Send ingredients to Ingredient Recognition Service
    r = call_with_retry("POST", settings.ING_URL, json={"ingredients": ingredients})
    print(f"[api_server] Sent to ING_URL ({settings.ING_URL}): {{'ingredients': {ingredients}}}", flush=True)
    r.raise_for_status()
    recognized = r.json().get("recognized_ingredients", [])

    # Step 2: Send recognized ingredients to Recipe Search Service
    s = call_with_retry("POST", settings.SEARCH_URL, json={"ingredients": recognized})
    s.raise_for_status()

    recipes = s.json().get("recipes", [])
    if not recipes:
        return jsonify({
            "recipes": [], 
            "message": "No recipes found",
            "intent": intent,
            "constraints": constraints
            }), 200

    # Step 3: Send recipes to Response Generator
    g = call_with_retry("POST", settings.GEN_URL, json={"recipes": recipes})
    g.raise_for_status()

    result = g.json()
    # If result is an array, wrap it in { recipes: array } and return it.
    if isinstance(result, list):
        return jsonify({
            "recipes": result,
            "intent": intent,
            "constraints": constraints
            }), 200

    # If result is a dictionary and the recipes key is an array, return it as is.
    if isinstance(result, dict) and isinstance(result.get("recipes"), list):
        result["intent"] = intent
        result["constraints"] = constraints
        return jsonify(result), 200

    # If it’s in some other format, safely return an empty structure.
    return jsonify({
        "recipes": [],
        "intent": intent,
        "constraints": constraints
        }), 200


if __name__ == '__main__':
    print(f"[app] APP_ENV={settings.APP_ENV}")
    app.run(debug=True, host='0.0.0.0', port=5000)
