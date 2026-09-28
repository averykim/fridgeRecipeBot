import difflib
from sklearn.feature_extraction.text import TfidfVectorizer


def calculate_jaccard_similarity(set_a: set, set_b: set) -> float:
    """Calculate the Jaccard similarity (ingredient match rate) between two sets"""
    if not set_a and not set_b:
        return 1.0
        
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    
    return intersection / union

def cosine_similarity(text_a: str, text_b: str) ->  float:
    """
    Calculate the contextual match rate of recipe texts using TF-IDF and cosine similarity
    """
    if not text_a.strip() or not text_b.strip():
        return 0.0
    
    # 1. initialize TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    
    try:
        # convert two text into vector
        tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
        
        # calculate cosine similarity
        # result = [[1.0, similarity], [similarity, 1.0]] -> 2D array -> [0][1]
        similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity_score)
    except ValueError:
        return 0.0

def calculate_text_similarity(text_a: str, text_b: str) -> float:
    """
    Calculates the morphological similarity (recipe match rate) between two strings
    on a scale of 0.0 to 1.0
    """
    if not text_a or not text_b:
        return 0.0
        
    # Uses SequenceMatcher to determine the similarity of text structure and word order
    return difflib.SequenceMatcher(None, text_a, text_b).ratio()