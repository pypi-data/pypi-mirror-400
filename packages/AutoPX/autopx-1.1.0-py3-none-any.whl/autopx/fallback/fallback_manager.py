from autopx.fallback.fallback_rules import FallbackRules
from autopx.utils.logger import Logger

class FallbackManager:
    """
    Manages fallback operations when preprocessing or vectorization fails.
    """

    def __init__(self):
        self.rules = FallbackRules()
        self.logger = Logger()

    def apply_vectorization_fallback(self, current_vectorization):
        """
        Returns a safer fallback vectorization if the current one fails.
        """
        fallback = self.rules.get_vectorization_fallback(current_vectorization)
        self.logger.warning(
            f"Vectorization '{current_vectorization}' failed. Falling back to '{fallback}'."
        )
        return fallback

    def handle_error(self, error_message: str, stage: str = None):
        """
        Logs an error and decides if a fallback can be applied.
        """
        self.logger.error(f"Error during stage '{stage}': {error_message}")
