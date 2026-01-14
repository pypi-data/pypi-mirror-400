from sklearn.feature_extraction.text import TfidfVectorizer

class TFIDF:
    """
    TF-IDF vectorization wrapper for AutoPX.
    """

    def __init__(self, max_features: int = 5000, ngram_range: tuple[int, int] = (1, 2)):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range
        )

    def fit_transform(self, texts: list[str]):
        """
        Fit TF-IDF on texts and return transformed vectors.
        """
        return self.vectorizer.fit_transform(texts)

    def transform(self, texts: list[str]):
        """
        Transform new texts using the already-fitted TF-IDF vectorizer.
        """
        return self.vectorizer.transform(texts)
