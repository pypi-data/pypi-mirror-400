import json
from autopx.utils.logger import Logger

class JSONReport:
    """
    Generates a JSON formatted preprocessing report.
    """

    def __init__(self):
        self.logger = Logger()

    def generate(self, report_data: dict, filepath: str = None) -> str | None:
        """
        Generates a JSON report from report_data dictionary.
        If filepath is provided, saves to file; otherwise returns JSON string.
        """
        try:
            json_str = json.dumps(report_data, indent=4, ensure_ascii=False)
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                self.logger.info(f"JSON report saved to {filepath}")
            return json_str
        except Exception as e:
            self.logger.error(f"Failed to generate JSON report: {e}")
            return None
