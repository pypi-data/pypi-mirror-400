import unittest
from autopx.core.decision_engine import DecisionEngine
from autopx.utils.constants import TaskType, ModelType, VectorizationType

class TestDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DecisionEngine()
    
    def test_infer_task_sentiment(self):
        analysis_report = {'avg_length': 10, 'has_emojis': True}
        task = self.engine.infer_task([], analysis_report)
        self.assertEqual(task, TaskType.SENTIMENT)
    
    def test_infer_task_topic_modeling(self):
        analysis_report = {'avg_length': 150, 'has_emojis': False}
        task = self.engine.infer_task([], analysis_report)
        self.assertEqual(task, TaskType.TOPIC_MODELING)
    
    def test_infer_task_chatbot_default(self):
        analysis_report = {'avg_length': 50, 'has_emojis': False}
        task = self.engine.infer_task([], analysis_report)
        self.assertEqual(task, TaskType.CHATBOT)
    
    def test_select_vectorization_dl(self):
        vec_type = self.engine.select_vectorization(TaskType.SENTIMENT, ModelType.DL, 500)
        self.assertEqual(vec_type, VectorizationType.SEQUENCE)
    
    def test_select_vectorization_topic_modeling(self):
        vec_type = self.engine.select_vectorization(TaskType.TOPIC_MODELING, ModelType.ML, 2000)
        self.assertEqual(vec_type, VectorizationType.TFIDF)
    
    def test_select_vectorization_small_dataset(self):
        vec_type = self.engine.select_vectorization(TaskType.SENTIMENT, ModelType.ML, 500)
        self.assertEqual(vec_type, VectorizationType.COUNT)

if __name__ == "__main__":
    unittest.main()
