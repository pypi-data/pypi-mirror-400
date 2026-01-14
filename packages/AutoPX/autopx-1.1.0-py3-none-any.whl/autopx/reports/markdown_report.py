from autopx.utils.logger import Logger

class MarkdownReport:
    """
    Generates a Markdown formatted preprocessing report.
    """

    def __init__(self):
        self.logger = Logger()

    def generate(self, report_data: dict, filepath: str = None) -> str | None:
        """
        Generates a Markdown report from report_data dictionary.
        If filepath is provided, saves to file; otherwise returns Markdown string.
        """
        try:
            lines = ["# AutoPX Preprocessing Report\n"]

            # Analysis Section
            analysis = report_data.get('analysis', {})
            lines.append("## Data Analysis")
            lines.append(f"- Dataset size: {analysis.get('dataset_size', 'N/A')}")
            lines.append(f"- Average text length: {analysis.get('avg_length', 'N/A')}")
            
            # Ensure language is string
            language = analysis.get('language', 'N/A')
            if hasattr(language, 'value'):
                language = language.value
            lines.append(f"- Detected language: {language}")
            lines.append(f"- Emojis present: {analysis.get('has_emojis', False)}\n")

            # Task Section (must match unit test)
            task = report_data.get('task', 'N/A')
            if hasattr(task, 'value'):
                task = task.value
            lines.append(f"task: {task}\n")  # FIXED for test

            # Vectorization Section (optional, for readability)
            vectorization = report_data.get('vectorization', 'N/A')
            if hasattr(vectorization, 'value'):
                vectorization = vectorization.value
            lines.append(f"vectorization: {vectorization}\n")

            markdown_str = "\n".join(lines)

            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_str)
                self.logger.info(f"Markdown report saved to {filepath}")

            return markdown_str

        except Exception as e:
            self.logger.error(f"Failed to generate Markdown report: {e}")
            return None
