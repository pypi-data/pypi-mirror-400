import re
from autopx.utils.constants import Language

class Tokenizer:
    """
    Handles tokenization of text based on language and script.
    """

    def __init__(self):
        pass

    def tokenize(self, text: str, language: str) -> list[str]:
        if not text:
            return []

        if language == Language.ENGLISH:
            return re.findall(r'\b\w+\b', text.lower())
        elif language == Language.URDU:
            return [t for t in text.split() if t.strip()]
        elif language == Language.ROMAN_URDU:
            return self._char_ngrams(text.lower(), n=3)
        else:
            return text.split()

    def _char_ngrams(self, text: str, n: int = 3) -> list[str]:
        text = re.sub(r'\s+', ' ', text).strip()
        return [text[i:i+n] for i in range(len(text)-n+1)]
