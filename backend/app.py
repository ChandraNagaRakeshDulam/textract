from flask import Flask, request, jsonify
from flask_cors import CORS
from textract_handler import extract_text_from_s3
from qa_engine import answer_question
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store extracted text globally (temporary memory)
extracted_text_cache = ""

@app.route('/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = file.filename
    local_path = os.path.join(UPLOAD_FOLDER, filename)
    s3_key = f"uploads/{filename}"

    # Save file locally
    file.save(local_path)

    # Extract text
    try:
        result = extract_text_from_s3(local_path, s3_key)

        # Cache for Q&A
        global extracted_text_cache
        extracted_text_cache = "\n".join(result['lines'])

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')

    if not extracted_text_cache:
        return jsonify({'answer': 'No text has been extracted yet.'}), 400

    try:
        answer = answer_question(question, extracted_text_cache)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
