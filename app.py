from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename

from models.summarizer import summarize_pdf
from models.query_model import answer_query
from utils.extract_text import extract_entities  # ✅ Corrected import

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -------------------- ROUTES --------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarization')
def summarization_page():
    return render_template('summarization.html')

@app.route('/document_query')
def query_page():
    return render_template('document_query.html')

@app.route('/draft')
def draft_page():
    return render_template('draft.html')


# ------------------ SUMMARIZATION ------------------

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'summary_doc.pdf')
    file.save(filepath)

    # Perform summarization
    summary = summarize_pdf(filepath)
    return jsonify({"summary": summary})


# ------------------ DOCUMENT QUERY ------------------

@app.route('/upload_query_file', methods=['POST'])
def upload_query_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'query_doc.pdf')
    file.save(filepath)

    return jsonify({"message": "File uploaded successfully"})


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get("question")

    uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], 'query_doc.pdf')
    if not os.path.exists(uploaded_file):
        return jsonify({"answer": "⚠️ Please upload a document first."})

    answer = answer_query(question, uploaded_file)
    return jsonify({"answer": answer})


# ------------------ ENTITY EXTRACTION (OPTIONAL) ------------------

@app.route('/extract_entities', methods=['POST'])
def extract_entities_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'ner_doc.pdf')
    file.save(filepath)

    result = extract_entities(filepath)
    return jsonify({"entities": result})


# ------------------ MAIN ------------------

if __name__ == '__main__':
    app.run(debug=True)
