from flask import Flask, request, jsonify
import settings
import re

app = Flask(__name__)

def format_instructions(raw):
    if not raw:
        return "No recipe found."
    
    text = raw.replace('\r\n', '\n').strip()
    steps = re.split(r'(?i)step\s*\d+[:.]*|(?<=\d)\.', text)

    if len(steps) <= 1:
        steps = text.split('. ')
    
    cleaned_steps = []
    for step in steps:
        step = step.strip()
        if len(step) > 5:
            if not step.endswith('.'):
                step += '.'
            cleaned_steps.append(f"   {len(cleaned_steps)+1}. {step}")
    return "\n".join(cleaned_steps)

@app.route('/generate', methods=['POST'])
def generate_response():
    data = request.json
    recipes = data.get('recipes', [])
    
    if not recipes:
        return jsonify({"message": "Can't find recipe. Try another ingredients!"})
    
    formatted_responses = []
    message_parts = []

    for recipe in recipes:
        name = recipe.get('name', "Unknown Recipe")
        matched = ", ".join(recipe.get('matched', []))
        missing = ", ".join(recipe.get('missing', []))
        instructions = format_instructions(recipe.get('instructions', ''))

        message = (
            f"### 🍴 {recipe['name']}\n"
            f"✅ matched ingredients: {matched}\n"
            f"❌ missing ingredients: {missing if missing else 'no missing'}\n\n"
            f"📝 instruction:\n{instructions}\n"
            f"------------------------------------------"
        )

        formatted_responses.append({
            'name': name,
            'message': message
        })

        message_parts.append(message)

    full_message = "\n\n".join(message_parts)
    
    return jsonify({
        "recipes": formatted_responses,
        "full_message": full_message
    })

if __name__ == '__main__':
    print(f"[generate] APP_ENV={settings.APP_ENV}")
    app.run(debug=True, host='0.0.0.0', port=5003)
