import unittest
from autopx.core.decision_engine import DecisionEngine
from autopx.utils.constants import TaskType, Language

class TestDecision(unittest.TestCase):
    def setUp(self):
        self.engine = DecisionEngine()

    def test_infer_sentiment(self):
        analysis = {'avg_length': 10, 'has_emojis': True}
        task = self.engine.infer_task([], analysis)
        self.assertEqual(task, TaskType.SENTIMENT)

    def test_infer_topic(self):
        analysis = {'avg_length': 150, 'has_emojis': False}
        task = self.engine.infer_task([], analysis)
        self.assertEqual(task, TaskType.TOPIC_MODELING)

if __name__ == "__main__":
    unittest.main()
