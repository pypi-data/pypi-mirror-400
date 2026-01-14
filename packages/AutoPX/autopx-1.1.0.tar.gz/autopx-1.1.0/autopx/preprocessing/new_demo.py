from autopx.core.autopx import AutoPX
from autopx.utils.constants import ModelType

# Sample texts
texts = [
    "I love Python! 🐍",
    "Machine learning is amazing.",
    "This is terrible news 😢",
    "The movie was fantastic!",
    "I hate waiting in long lines..."
]

# Initialize AutoPX pipeline
autopx = AutoPX(model_type=ModelType.ML)

# Preprocess texts and generate JSON report
processed_data, json_report = autopx.preprocess(texts)
print("Processed Data:")
print(processed_data)

print("\nJSON Report:")
print(json_report)

# Generate Markdown report
md_report = autopx.get_report(format="markdown")
print("\nMarkdown Report:")
print(md_report)

# Generate PDF report (saved automatically in project folder)
pdf_report_path = autopx.get_report(format="pdf")
print(f"\nPDF Report saved at: {pdf_report_path}")
