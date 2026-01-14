import unittest
from autopx.reports.report_builder import ReportBuilder
from autopx.utils.constants import TaskType, VectorizationType, Language

class TestReportBuilder(unittest.TestCase):
    def setUp(self):
        self.report_builder = ReportBuilder()
        self.sample_report = {
            'analysis': {
                'language': Language.ENGLISH,
                'avg_length': 15,
                'has_emojis': True,
                'dataset_size': 10
            },
            'task': TaskType.SENTIMENT,
            'vectorization': VectorizationType.TFIDF
        }

    def test_generate_json_report(self):
        output = self.report_builder.generate(self.sample_report, format="json")
        self.assertIn('"language": "en"', output)
        self.assertIn('"task": "sentiment"', output)

    def test_generate_markdown_report(self):
        output = self.report_builder.generate(self.sample_report, format="markdown")
        self.assertIn("# AutoPX Preprocessing Report", output)
        self.assertIn("language: en", output.lower())
        self.assertIn("task: sentiment", output.lower())

    def test_generate_pdf_report(self):
        # Ensure PDF generation returns filename
        output = self.report_builder.generate(self.sample_report, format="pdf", filepath="test_report.pdf")
        self.assertIsNotNone(output)
        self.assertIn(".pdf", output)

if __name__ == "__main__":
    unittest.main()
