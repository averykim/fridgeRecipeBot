from flask import Flask, request, jsonify
import spacy, os, re
from settings import APP_ENV

app = Flask(__name__)
# Load SpaCy's English model
nlp = spacy.load(os.getenv("SPACY_MODEL", "en_core_web_sm"))

TIME_RE = re.compile(r"(\d+)\s*(min|mins|minute|minutes|h|hour|hours)\b", re.I)
DIF_RE = re.compile(r"\b(easy|medium|hard)\b", re.I)

GREETINGS = {"hi", "hello", "hey"}
HELP = {"help", "how", "usage", "guide", "instructions", "what can you do"}
THANKS = {"thanks", "thank you", "thx", "appreciate", "ok", "okay"}

# Using SpaCy to extract ingredients by nouns and proper nouns
def parse_constraints(text: str):
    t = (text or "").lower()
    constraints = {}

    m = TIME_RE.search(t)
    if m:
        constraints["max_prep_time"] = int(m.group(1))
    
    m2 = DIF_RE.search(t)
    if m2:
        constraints["difficulty"] = m2.group(1).capitalize()

    if "spicy" in t:
        constraints["spicy"] = True

    return constraints

def classify_intent(text: str):
    t = (text or "").strip()
    tl = t.lower()
    doc = nlp(t)
    tokens = [tok.text.lower() for tok in doc if tok.is_alpha]
    
    # 1) quick checks (based on token)
    if any(tok in GREETINGS for tok in tokens):
        return "greeting", {}
    if any(tok in HELP for tok in tokens):
        return "help", {}
    if any(tok in THANKS for tok in tokens):
        return "thanks", {}
    
    # 2) constraints
    constraints = parse_constraints(t)
    if constraints:
        return "constraints_query", constraints
    
    # 3) ingredient-like query heuristic
    nouns = []
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN") and token.is_alpha and not token.is_stop:
            nouns.append(token.lemma_.lower())

    return "ingredients_query", {"nouns": sorted(set(nouns))}


@app.route('/intent', methods=['POST'])
def recognize_ingredients():
    data = request.json or {}
    text = data.get("text", "") or ""
    intent_label, constraints = classify_intent(text)
    return jsonify({"intent": intent_label, "constraints": constraints})

@app.route("/health", methods=['GET'])
def health():
    return jsonify({"status": "ok"}, 200)

if __name__ == '__main__':
    print(f"[intent] APP_ENV={APP_ENV}")
    app.run(debug=True, host='0.0.0.0', port=5004)
