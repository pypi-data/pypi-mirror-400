# autopx/reports/pdf_report.py

# ReportLab imports with fallback
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except ImportError:
    class canvas:
        class Canvas:
            def __init__(self, *args, **kwargs): pass
            def setFont(self, *args, **kwargs): pass
            def drawString(self, *args, **kwargs): pass
            def save(self): pass
    A4 = (595.27, 841.89)

from autopx.utils.logger import Logger
from typing import Optional, Dict, Union

class PDFReport:
    """
    Generates a PDF formatted preprocessing report for AutoPX.
    """

    def __init__(self):
        self.logger = Logger()

    def generate(
        self,
        report_data: Dict[str, Union[str, dict]] ,
        filepath: str = "AutoPX_Report.pdf"
    ) -> Optional[str]:
        """
        Generates a PDF report from report_data dictionary.

        Args:
            report_data (dict): Dictionary containing analysis, task, and vectorization info.
            filepath (str): Path to save the PDF report.

        Returns:
            str: Path to the saved PDF file, or None on failure.
        """
        try:
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            y = height - 50  # starting y position

            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, "AutoPX Preprocessing Report")
            y -= 40

            c.setFont("Helvetica", 12)

            # Data Analysis Section
            analysis = report_data.get('analysis', {})
            c.drawString(50, y, "Data Analysis:")
            y -= 20
            c.drawString(70, y, f"Dataset size: {analysis.get('dataset_size', 'N/A')}")
            y -= 20
            c.drawString(70, y, f"Average text length: {analysis.get('avg_length', 'N/A')}")
            y -= 20
            c.drawString(70, y, f"Detected language: {analysis.get('language', 'N/A')}")
            y -= 20
            c.drawString(70, y, f"Emojis present: {analysis.get('has_emojis', False)}")
            y -= 30

            # Task Section
            task = report_data.get('task', 'N/A')
            c.drawString(50, y, f"Task Inferred: {task}")
            y -= 30

            # Vectorization Section
            vectorization = report_data.get('vectorization', 'N/A')
            c.drawString(50, y, f"Vectorization Strategy: {vectorization}")
            y -= 30

            # Save PDF
            c.save()
            self.logger.info(f"PDF report saved to {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Failed to generate PDF report: {e}")
            return None
