from autopx.utils.constants import Language, TaskType

class StopwordHandler:
    """
    Handles stopword removal/preservation based on task and language.
    """

    ENGLISH_STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "if", "in", "on", "with", "for", "of", "at", "by"
    }

    URDU_STOPWORDS = {
        "ہے", "کا", "کی", "کے", "میں", "کو", "سے", "یہ", "وہ"
    }

    ROMAN_URDU_STOPWORDS = {
        "hai", "ka", "ki", "ke", "main", "ko", "se", "ye", "wo"
    }

    def __init__(self):
        pass

    def remove_stopwords(self, text: str, task: str, language: str) -> str:
        if not text:
            return ""

        words = text.split()

        # Preserve stopwords for sentiment/chatbot
        if task in [TaskType.SENTIMENT, TaskType.CHATBOT]:
            return text

        if language == Language.ENGLISH:
            stopwords = self.ENGLISH_STOPWORDS
        elif language == Language.URDU:
            stopwords = self.URDU_STOPWORDS
        elif language == Language.ROMAN_URDU:
            stopwords = self.ROMAN_URDU_STOPWORDS
        else:
            stopwords = set()

        filtered = [w for w in words if w.lower() not in stopwords]
        return " ".join(filtered)
