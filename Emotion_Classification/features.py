from sklearn.feature_extraction.text import TfidfVectorizer

def build_vectorizer():
    return TfidfVectorizer(
        max_features=3000,
        stop_words="english",
        ngram_range=(1, 2)
    )
