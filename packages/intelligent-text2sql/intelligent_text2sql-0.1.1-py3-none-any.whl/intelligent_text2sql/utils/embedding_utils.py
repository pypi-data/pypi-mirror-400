from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(texts):
    model = get_model()
    if isinstance(texts, str):
        texts = [texts]
    return model.encode(texts)


def most_relevant(texts, query, top_k=2):
    text_embeddings = embed_text(texts)
    query_embedding = embed_text(query)

    similarities = cosine_similarity(
        query_embedding.reshape(1, -1),
        text_embeddings
    )[0]

    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [texts[i] for i in top_indices]
