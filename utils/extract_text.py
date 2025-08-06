import fitz  # PyMuPDF
<<<<<<< HEAD
from transformers import pipeline
=======
from docx import Document
from transformers import pipeline
import os
>>>>>>> 72f408b (final)

# Load Hugging Face Named Entity Recognition pipeline
ner_pipeline = pipeline("ner", grouped_entities=True)

<<<<<<< HEAD
=======
# ✅ Function 1: Extract text from PDF or DOCX
def extract_text_from_file(file_path):
    text = ""
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        elif ext == ".docx":
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            return "", "Unsupported file format."
    except Exception as e:
        return "", f"Error reading file: {str(e)}"

    return text.strip(), None

# ✅ Function 2: Extract entities (NER)
>>>>>>> 72f408b (final)
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
