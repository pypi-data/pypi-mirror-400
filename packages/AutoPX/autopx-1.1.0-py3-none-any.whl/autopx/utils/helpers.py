import re
import os
from autopx.utils.constants import Language

def is_english(text: str) -> bool:
    """Check if text is predominantly English."""
    return bool(re.search(r'[a-zA-Z]', text))

def is_urdu(text: str) -> bool:
    """Check if text contains Urdu characters."""
    return bool(re.search(r'[\u0600-\u06FF]', text))

def is_roman_urdu(text: str) -> bool:
    """Check for Roman Urdu by heuristics (common keywords)."""
    roman_keywords = ['hai', 'main', 'kya', 'kaise', 'bhi', 'tha', 'thi']
    words = set(re.findall(r'\b\w+\b', text.lower()))
    return len(words.intersection(roman_keywords)) > 0

def detect_language(text: str) -> Language:
    """Detect language using simple heuristics."""
    if is_urdu(text):
        return Language.URDU
    elif is_roman_urdu(text):
        return Language.ROMAN_URDU
    elif is_english(text):
        return Language.ENGLISH
    else:
        return Language.UNKNOWN

def safe_mkdir(path: str) -> bool:
    """Create a directory if it does not exist."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False

def clean_text_basic(text: str) -> str:
    """
    Basic cleaning: remove extra spaces, strip text, remove URLs.
    Can be extended for task-aware cleaning.
    """
    text = text.strip()
    text = re.sub(r"http\S+|www\S+", "", text)  # Remove URLs
    text = re.sub(r"\s+", " ", text)            # Normalize whitespace
    return text
