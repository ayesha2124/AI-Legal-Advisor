import fitz  # PyMuPDF
from transformers import pipeline
import re
from datetime import datetime, timedelta

# Load Hugging Face summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def extract_parties(text):
    disclosing = ""
    receiving = ""

    disclosing_match = re.search(r"Disclosing Party\s*[:\-–]\s*(.+?)(?:,|\n|$)", text, re.IGNORECASE)
    receiving_match = re.search(r"Receiving Party\s*[:\-–]\s*(.+?)(?:,|\n|$)", text, re.IGNORECASE)

    if disclosing_match:
        disclosing = disclosing_match.group(1).strip()
    if receiving_match:
        receiving = receiving_match.group(1).strip()

    if not disclosing and not receiving:
        return "[Parties not found. Please verify manually.]"
    
    return f"Disclosing Party: {disclosing}<br>Receiving Party: {receiving}"

def extract_dates(text):
    date_match = re.search(
        r'(\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})',
        text
    )

    if date_match:
        try:
            start_date = datetime.strptime(date_match.group(1).replace(",", ""), "%B %d %Y")
            end_date = start_date + timedelta(days=365 * 2)
            return f"Agreement Date: {start_date.strftime('%B %d, %Y')}<br>Agreement Expiration: {end_date.strftime('%B %d, %Y')}"
        except:
            pass

    return "[Dates not clearly found. Please verify manually.]"

def identify_risks(text):
    risks = []

    if "reasonably understood" in text:
        risks.append("Ambiguous phrase: 'reasonably understood' may be misinterpreted.")
    if "remedy" not in text and "breach" in text:
        risks.append("Missing remedies for breach of confidentiality.")
    if "return" not in text and "destroy" not in text:
        risks.append("No mention of return or destruction of confidential info.")
    if "signature" not in text and "signed" not in text:
        risks.append("Possible missing signatures.")
    if "term" not in text and "duration" not in text:
        risks.append("Missing agreement duration clause.")

    if not risks:
        risks.append("No major risks detected.")

    return risks

def calculate_compliance_score(risks):
    total_possible = 5
    penalty = len([r for r in risks if "Missing" in r or "Ambiguous" in r])
    return max(0, 100 - penalty * 20)

def summarize_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        return f"rror reading PDF: {str(e)}"

    if not text.strip():
        return "⚠️ No text found in the document."

    short_text = text[:3000]

    try:
        summary_result = summarizer(short_text, max_length=512, min_length=100, do_sample=False)
        raw_summary = summary_result[0]['summary_text']

        parties = extract_parties(text)
        dates = extract_dates(text)
        risks = identify_risks(text)
        score = calculate_compliance_score(risks)

        structured_summary = f"""
<b>NDA Summary Report</b><br><br>

<b>Purpose:</b><br>
This document is a Non-Disclosure Agreement (NDA), outlining obligations to protect confidential information.<br><br>

<b>👥 Parties:</b><br>
{parties}<br><br>

<b>Key Clauses:</b><br>
{raw_summary}<br><br>

<b>Important Dates:</b><br>
{dates}<br><br>

<b>⚖️ Legal Duties:</b><br>
Ensure confidentiality, limit disclosure, and restrict use of shared information.<br><br>

<b>⚠️ Risks Detected:</b><br>
""" + "<br>".join(f"- {r}" for r in risks) + f"""<br><br>

<b>Compliance Score:</b> {score}/100
"""
        return structured_summary.strip()
    except Exception as e:
        return f"Summarization failed: {str(e)}"
