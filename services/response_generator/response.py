from flask import Flask, request, jsonify
import settings

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_response():
    data = request.json
    recipes = data.get('recipes', [])
    
    # Generate a response for each recipe
    response = []
    for recipe in recipes:
        response.append({
            'name': recipe['name'],
            'instructions': recipe['instructions'],
            'message': f"Here's a recipe for {recipe['name']}: {recipe['instructions']}"
        })
    
    return jsonify({"recipes": response})

if __name__ == '__main__':
    print(f"[generate] APP_ENV={settings.APP_ENV}")
    app.run(debug=True, host='0.0.0.0', port=5003)
