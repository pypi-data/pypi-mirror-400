import re
from autopx.utils.constants import Language, TaskType

class Cleaner:
    """
    Cleans text based on detected language and NLP task.
    """

    def __init__(self):
        # Basic regex patterns
        self.url_pattern = re.compile(r'http\S+|www\S+')
        self.special_char_pattern = re.compile(r'[^a-zA-Z0-9\s\u0600-\u06FF]')  # Keep Urdu range

    def clean(self, text: str, task: str, language: str) -> str:
        if not text:
            return ""

        cleaned = text.strip()

        # 1. Remove URLs
        cleaned = self.url_pattern.sub("", cleaned)

        # 2. Task-specific cleaning
        if task in [TaskType.SENTIMENT, TaskType.CHATBOT]:
            cleaned = self._remove_special_characters_preserve_emojis(cleaned, language)
        else:
            cleaned = self.special_char_pattern.sub(" ", cleaned)

        # 3. Lowercase English/Roman Urdu
        if language in [Language.ENGLISH, Language.ROMAN_URDU]:
            cleaned = cleaned.lower()

        # 4. Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned.strip()

    def _remove_special_characters_preserve_emojis(self, text: str, language: str) -> str:
        """
        Remove special characters but preserve emojis.
        """
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF]+", flags=re.UNICODE
        )

        cleaned = ""
        for char in text:
            if language == Language.URDU and '\u0600' <= char <= '\u06FF':
                cleaned += char
            elif language in [Language.ENGLISH, Language.ROMAN_URDU] and char.isalnum():
                cleaned += char
            elif emoji_pattern.match(char):
                cleaned += char
            elif char.isspace():
                cleaned += " "
        return cleaned
