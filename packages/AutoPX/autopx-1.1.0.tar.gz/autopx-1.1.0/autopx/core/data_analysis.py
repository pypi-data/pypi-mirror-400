import re
from autopx.utils.constants import Language

class DataAnalyzer:
    """
    Analyzes raw input text to understand structure and language.
    """

    def analyze(self, texts: list[str]) -> dict:
        if not texts:
            return {
                "language": Language.UNKNOWN,
                "avg_length": 0,
                "has_emojis": False,
                "dataset_size": 0
            }

        avg_len = sum(len(t.split()) for t in texts) / len(texts)

        # Emoji detection
        emoji_pattern = re.compile(r"[\U00010000-\U0010FFFF]", flags=re.UNICODE)
        has_emojis = any(emoji_pattern.search(t) for t in texts[:100])

        language = self._detect_language(texts)

        return {
            "language": language,
            "avg_length": avg_len,
            "has_emojis": has_emojis,
            "dataset_size": len(texts)
        }

    def _detect_language(self, texts: list[str]) -> str:
        """
        Detects if the text is English, Urdu, or Roman Urdu.
        """
        sample_text = " ".join(texts[:5])

        # Urdu Unicode
        if re.search(r"[\u0600-\u06FF]", sample_text):
            return Language.URDU

        # Roman Urdu keywords
        roman_ur_keywords = {"hai", "main", "kya", "kaise", "bhi", "tha", "thi"}
        words = set(re.findall(r"\b\w+\b", sample_text.lower()))

        if words.intersection(roman_ur_keywords):
            return Language.ROMAN_URDU

        return Language.ENGLISH
