from flask import Flask, request, jsonify
import spacy, os, re
from settings import APP_ENV

app = Flask(__name__)
# Load SpaCy's English model
nlp = spacy.load(os.getenv("SPACY_MODEL", "en_core_web_sm"))

TOKEN_RE = re.compile(r"[A-Za-z]+")

# Using SpaCy to extract ingredients by nouns and proper nouns
def extract_item(text: str):
    doc = nlp(text)
    filtered_text = {
        t.lemma_.lower().strip()
        for t in doc
        if t.pos_ in ("NOUN", "PROPN") and t.is_alpha and not t.is_stop
    }
    if filtered_text:
        return filtered_text
    
    fallback = {m.group(0).lower() for m in TOKEN_RE.finditer(text)}
    return fallback

@app.route('/recognize', methods=['POST'])
def recognize_ingredients():
    data = request.json or {}
    items = [s.strip() for s in data.get("ingredients", []) if s and s.strip()]
    filtered = set()

    for raw in items:
        cand = extract_item(raw)
        filtered.update(cand)

    # convert set to list
    final_list = sorted(filtered)
    
    return jsonify({"recognized_ingredients": final_list})

if __name__ == '__main__':
    print(f"[recognize] APP_ENV={APP_ENV}")
    app.run(debug=True, host='0.0.0.0', port=5001)
