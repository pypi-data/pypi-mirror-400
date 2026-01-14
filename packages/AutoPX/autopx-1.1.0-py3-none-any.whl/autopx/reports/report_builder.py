import json
from autopx.reports.markdown_report import MarkdownReport
from autopx.reports.pdf_report import PDFReport
from autopx.utils.logger import Logger

class ReportBuilder:
    """
    Unified report generator for AutoPX.
    Supports JSON, Markdown, and PDF formats.
    """

    def __init__(self):
        self.logger = Logger()
        self.markdown = MarkdownReport()
        self.pdf = PDFReport()

    def generate(self, report_data: dict, format: str = "pdf", filepath: str = None) -> str | None:
        """
        Generate report in the requested format.

        Args:
            report_data (dict): The preprocessing report data.
            format (str): "json", "markdown", or "pdf".
            filepath (str): Optional path to save the report.

        Returns:
            str: Path to saved report or report content (for JSON/Markdown).
        """
        try:
            format = format.lower()

            # JSON report
            if format == "json":
                json_str = json.dumps(report_data, indent=4)
                if filepath:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(json_str)
                    self.logger.info(f"JSON report saved to {filepath}")
                    return filepath
                return json_str

            # Markdown report
            elif format in ["markdown", "md"]:
                return self.markdown.generate(report_data, filepath)

            # PDF report
            elif format == "pdf":
                if not filepath:
                    filepath = "AutoPX_Report.pdf"
                return self.pdf.generate(report_data, filepath)

            # Unsupported format
            else:
                self.logger.error(f"Unsupported report format: {format}")
                return None

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return None
