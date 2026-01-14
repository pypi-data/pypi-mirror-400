import unittest
from autopx.preprocessing.cleaner import Cleaner
from autopx.utils.constants import TaskType, Language

class TestCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = Cleaner()

    def test_clean_sentiment(self):
        text = "Happy! 😄 Visit http://ok.com"
        cleaned = self.cleaner.clean(text, TaskType.SENTIMENT, Language.ENGLISH)
        self.assertIn("😄", cleaned)
        self.assertNotIn("http", cleaned)

    def test_clean_urdu(self):
        text = "بہترین کتاب!"
        cleaned = self.cleaner.clean(text, TaskType.SENTIMENT, Language.URDU)
        self.assertIn("بہترین", cleaned)

if __name__ == "__main__":
    unittest.main()
