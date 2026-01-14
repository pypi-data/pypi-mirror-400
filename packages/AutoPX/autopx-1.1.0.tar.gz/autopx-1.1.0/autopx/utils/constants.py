from enum import Enum

class Language(str, Enum):
    ENGLISH = "en"
    URDU = "ur"
    ROMAN_URDU = "roman_ur"
    UNKNOWN = "unknown"

class TaskType(str, Enum):
    SENTIMENT = "sentiment"
    TOPIC_MODELING = "topic_modeling"
    CHATBOT = "chatbot"

class ModelType(str, Enum):
    ML = "ml"               # Traditional Machine Learning
    DL = "dl"               # Deep Learning
    TRANSFORMERS = "transformers"  # Transformer-based models

class VectorizationType(str, Enum):
    TFIDF = "tfidf"
    COUNT = "count"
    SEQUENCE = "sequence"
    EMBEDDINGS = "embeddings"
