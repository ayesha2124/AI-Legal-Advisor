<<<<<<< HEAD
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
=======
import os
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from models.vector_store import VectorStore
from utils.extract_text import extract_text_from_file

# Set your API key (you can move this to env)
os.environ["GOOGLE_API_KEY"] = "AIzaSyBZLIi5ESCV8PcCDWBJgHJWKA-OvxwXaFg"

# Setup prompt
prompt_template = PromptTemplate.from_template("""
Use the following context to answer the question.

Context:
{context}

Question: {question}

Answer:
""")

llm = GoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2)

def answer_query(question, file_path):
    raw_text, error = extract_text_from_file(file_path)
    if error:
        return error

    if not raw_text.strip():
        return " Empty or unreadable document."

    vs = VectorStore()
    vs.build_index_from_text(raw_text)  # Optionally cache this if slow

    top_chunks = vs.search(question, top_k=3)

    if not top_chunks:
        return "No relevant content found in the document."

    context = "\n".join(top_chunks)
    final_prompt = prompt_template.format(context=context, question=question)

    try:
        response = llm.invoke(final_prompt)
        if "I don’t know" in response or "cannot answer" in response:
            return "Unrelated question."
        return response.strip()
    except Exception as e:
        return f" LLM Error: {str(e)}"
>>>>>>> 72f408b (final)
