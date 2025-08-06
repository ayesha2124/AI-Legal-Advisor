import fitz  # PyMuPDF
from transformers import pipeline

# Load Hugging Face Named Entity Recognition pipeline
ner_pipeline = pipeline("ner", grouped_entities=True)

def extract_entities(filepath):
    try:
        # Extract text from PDF
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        return f"⚠️ Error reading PDF: {str(e)}"

    if not text.strip():
        return "⚠️ No readable text found in the document."

    # Limit text size for NER model
    text = text[:2000]

    # Run NER
    try:
        entities = ner_pipeline(text)
    except Exception as e:
        return f"⚠️ Named Entity Recognition failed: {str(e)}"

    # Organize entities by label
    grouped = {}
    for ent in entities:
        label = ent["entity_group"]
        word = ent["word"].strip()
        if label not in grouped:
            grouped[label] = set()
        grouped[label].add(word)

    # Format output as HTML
    formatted = "<div style='line-height:1.8;'>"
    for label, words in grouped.items():
        words_str = ", ".join(sorted(words))
        formatted += f"<b style='color:#9c7700'>{label}:</b> {words_str}<br>"
    formatted += "</div>"

    return formatted
