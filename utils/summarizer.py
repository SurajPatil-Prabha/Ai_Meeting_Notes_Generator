"""
Local extractive summarizer using TF-IDF + cosine similarity
(a simplified TextRank-style approach). No API key, no external calls.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.text_utils import split_sentences


def summarize(text: str, num_sentences: int = 5) -> list[str]:
    """
    Return the top `num_sentences` most representative sentences from
    the text, in their ORIGINAL order (so the summary still reads
    naturally like a condensed transcript).
    """
    sentences = split_sentences(text)

    if len(sentences) <= num_sentences:
        return sentences

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(sentences)
    except ValueError:
        # e.g. all sentences were pure stopwords/empty after vectorizing
        return sentences[:num_sentences]

    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Simple graph-based ranking (power iteration, like a mini TextRank)
    scores = _text_rank(similarity_matrix)

    ranked_idx = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
    top_idx = sorted(ranked_idx[:num_sentences])  # restore original order

    return [sentences[i] for i in top_idx]


def _text_rank(sim_matrix: np.ndarray, damping: float = 0.85, iterations: int = 50) -> np.ndarray:
    n = sim_matrix.shape[0]
    if n == 0:
        return np.array([])

    # Normalize rows so each sums to 1 (avoid divide-by-zero)
    row_sums = sim_matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    transition = sim_matrix / row_sums

    scores = np.ones(n) / n
    for _ in range(iterations):
        new_scores = (1 - damping) / n + damping * transition.T.dot(scores)
        if np.allclose(new_scores, scores, atol=1e-6):
            scores = new_scores
            break
        scores = new_scores
    return scores


def top_keywords(text: str, num_keywords: int = 10) -> list[str]:
    """Extract top keywords/phrases from the text using TF-IDF scores."""
    sentences = split_sentences(text)
    if not sentences:
        return []

    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=200)
        tfidf_matrix = vectorizer.fit_transform(sentences)
    except ValueError:
        return []

    scores = np.asarray(tfidf_matrix.sum(axis=0)).ravel()
    terms = vectorizer.get_feature_names_out()

    ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
    seen = set()
    keywords = []
    for term, _ in ranked:
        # Skip near-duplicate keywords (e.g. "budget" vs "budget review")
        if any(term in k or k in term for k in seen):
            continue
        seen.add(term)
        keywords.append(term)
        if len(keywords) >= num_keywords:
            break
    return keywords
