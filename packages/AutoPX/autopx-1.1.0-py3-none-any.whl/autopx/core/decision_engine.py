from autopx.utils.constants import TaskType, ModelType, VectorizationType

class DecisionEngine:
    """
    Infers the NLP task and selects vectorization strategy.
    """

    def infer_task(self, texts: list[str], analysis: dict) -> str:
        avg_len = analysis.get("avg_length", 0)
        has_emojis = analysis.get("has_emojis", False)

        if avg_len < 30 and has_emojis:
            return TaskType.SENTIMENT

        if avg_len > 100:
            return TaskType.TOPIC_MODELING

        return TaskType.CHATBOT

    def select_vectorization(self, task: str, model_type: ModelType, dataset_size: int) -> str:
        if model_type in (ModelType.DL, ModelType.TRANSFORMERS):
            return VectorizationType.SEQUENCE

        if task == TaskType.TOPIC_MODELING:
            return VectorizationType.TFIDF

        if dataset_size < 1000:
            return VectorizationType.COUNT

        return VectorizationType.TFIDF
