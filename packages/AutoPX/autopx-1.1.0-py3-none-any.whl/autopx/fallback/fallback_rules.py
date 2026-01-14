from autopx.utils.constants import VectorizationType

class FallbackRules:
    """
    Defines fallback rules for preprocessing and vectorization.
    """

    def __init__(self):
        # Default fallback mapping
        self.vectorization_fallback = {
            VectorizationType.SEQUENCE: VectorizationType.TFIDF,
            VectorizationType.TFIDF: VectorizationType.COUNT,
            VectorizationType.COUNT: VectorizationType.COUNT  # last resort
        }

    def get_vectorization_fallback(self, current_vectorization):
        """
        Returns a simpler fallback vectorization strategy if the current one fails.
        """
        return self.vectorization_fallback.get(current_vectorization, VectorizationType.COUNT)
