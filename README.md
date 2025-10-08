# MVP Standards Checker

Automatically apply MVP Health Care communications standards to Word documents.

## Features

Currently implements **Module 3: Communications Standards** with 8 automated rule categories:

- ✅ State abbreviations (N.Y. → NY, V.T. → VT, C.T. → CT)
- ✅ Punctuation (& → and, double spaces)
- ✅ Digital terminology (healthcare → health care, telehealth → virtual care, log in → sign in)
- ✅ Time formatting (3:00 PM → 3 pm, 8 AM-5 PM → 8 am–5 pm)
- ✅ Number formatting (spell out 1-9, add commas to 1,000+)
- ✅ Healthcare terms (preventative → preventive)
- ✅ MVP branding (Gia®)
- ✅ Document analysis (word count, reading level, SEO keywords)

## Installation

```bash
# Clone or download the repository
cd mvp-standards-checker

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the Streamlit app
streamlit run app.py
```

## Document Structure

For best results, add markers to your Word document:

```
start_page_copy
[Your main content here]
end_page_copy

start_disclaimer
[Disclaimer content here]
end_disclaimer
```

These markers are optional but help the tool identify which sections to process.

## File Structure

```
mvp-standards-checker/
├── app.py                          # Main Streamlit app
├── config.yaml                     # Configuration
├── requirements.txt
├── core/
│   ├── __init__.py
│   ├── document_processor.py       # Word doc handling
│   ├── text_analyzer.py           # Reading level, metrics
│   └── utils.py                   # Shared utilities
└── modules/
    ├── __init__.py
    └── communications_standards.py # Module 3
```

## Configuration

Edit `config.yaml` to customize:
- Which rules to apply
- Target word counts and reading levels
- Exclusions and exceptions

## Coming Soon

- **Module 1:** Content Proofing Checklist
- **Module 2:** Digital Communications Standards
- **Module 4:** Brand Standards
- Medicare compliance checking
- More automated rules

## Development

Based on existing MVP Standards Checker Flask app, rewritten with modular architecture for easier maintenance and extension.
