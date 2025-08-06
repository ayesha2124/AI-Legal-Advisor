import fitz  # PyMuPDF
from docx import Document
from transformers import pipeline
from models.summarizer import extract_dates
import os
import re

# QA Model
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# ✅ NEW: Extract text from PDF or DOCX
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

# Main QA function
def answer_query(question, file_path):
    context, error = extract_text_from_file(file_path)
    if error:
        return error

    if not context:
        return "he uploaded document appears to be empty or unreadable."

    q_lower = question.lower()

    # Date-specific questions trigger date extraction
    if re.search(r"\b(effective date|agreement date|expiration|critical dates|validity|duration)\b", q_lower):
        return extract_dates(context)

    try:
        result = qa_pipeline({
            "question": question,
            "context": context[:3000]  # Truncate to keep fast
        })
        return result.get("answer", "❓ No answer found in the document.")
    except Exception as e:
        return f"⚠️ Error answering question: {str(e)}"
