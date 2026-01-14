from autopx.core.data_analysis import DataAnalyzer
from autopx.core.decision_engine import DecisionEngine
from autopx.preprocessing.cleaner import Cleaner
from autopx.vectorizers.count import VectorizerHelper
from autopx.reports.report_builder import ReportBuilder
from autopx.utils.constants import ModelType
from autopx.utils.logger import Logger


class AutoPX:
    """
    Main AutoPX pipeline class for intelligent text preprocessing.
    """

    def __init__(self, model_type: ModelType = ModelType.ML):
        self.model_type = model_type
        self.analyzer = DataAnalyzer()
        self.decision_engine = DecisionEngine()
        self.cleaner = Cleaner()
        self.report_builder = ReportBuilder()
        self.logger = Logger(__name__)  # FIXED
        self.last_report_data = {}

    def preprocess(self, texts: list[str], task: str = None) -> tuple:
        """
        Main method to preprocess texts and generate an explainable report.
        Returns processed_data and a JSON report.
        """
        self.logger.info("Starting AutoPX preprocessing pipeline...")

        # 1. Analyze Data
        analysis = self.analyzer.analyze(texts)

        # 2. Infer Task
        inferred_task = task if task else self.decision_engine.infer_task(texts, analysis)
        self.logger.info(f"Task: {inferred_task} | Language: {analysis['language']}")

        # 3. Clean Texts
        cleaned_texts = [self.cleaner.clean(t, inferred_task, analysis["language"]) for t in texts]

        # 4. Vectorization
        vec_strategy = self.decision_engine.select_vectorization(
            inferred_task,
            self.model_type,
            analysis["dataset_size"]
        )

        vectorizer = VectorizerHelper(strategy=vec_strategy)
        processed_data = vectorizer.fit_transform(cleaned_texts)

        # 5. Save Report Data
        self.last_report_data = {
            "analysis": analysis,
            "task": inferred_task,
            "vectorization": vec_strategy,
            "cleaned_sample": cleaned_texts[:5]
        }

        # 6. Generate JSON Report
        report = self.report_builder.generate(self.last_report_data, format="json")

        self.logger.info("Preprocessing complete.")
        return processed_data, report

    def get_report(self, format: str = "markdown"):
        """
        Returns the report in the specified format for the last run.
        """
        return self.report_builder.generate(self.last_report_data, format=format)
