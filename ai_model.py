from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import torch

# Load semantic similarity model (lightweight + good)
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load sentiment model
sentiment_analyzer = pipeline("sentiment-analysis")


def semantic_score(question, answer):
    """
    Measures how semantically similar the answer is to the question.
    Returns similarity score between 0 and 1.
    """
    embeddings = semantic_model.encode([question, answer], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    return float(similarity)


def confidence_score(answer):
    """
    Uses sentiment analysis to estimate confidence tone.
    Returns score between 0 and 1.
    """
    result = sentiment_analyzer(answer)[0]
    
    if result["label"] == "POSITIVE":
        return result["score"]
    else:
        return -result["score"]