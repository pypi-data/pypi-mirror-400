from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from autopx.utils.constants import VectorizationType

class VectorizerHelper:
    """
    Unified helper for TF-IDF and CountVectorizer.
    """

    def __init__(self, strategy=VectorizationType.TFIDF):
        self.strategy = strategy
        if strategy == VectorizationType.TFIDF:
            self.vectorizer = TfidfVectorizer()
        else:
            self.vectorizer = CountVectorizer()

    def fit_transform(self, texts: list[str]):
        """
        Fit and transform the input texts.
        """
        if not texts:
            return None
        return self.vectorizer.fit_transform(texts)

    def transform(self, texts: list[str]):
        """
        Transform the input texts using the fitted vectorizer.
        """
        return self.vectorizer.transform(texts)
