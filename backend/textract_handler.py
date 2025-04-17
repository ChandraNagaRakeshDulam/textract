import os
import boto3
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()

# AWS Setup
s3 = boto3.client('s3')
textract = boto3.client('textract')
BUCKET = os.environ['S3_BUCKET']

def extract_text_from_s3(local_file, s3_key):
    # If PDF, assume it's text-based and use PyMuPDF
    if local_file.lower().endswith('.pdf'):
        return extract_text_from_pdf_text_based(local_file)

    # Otherwise, upload and use Textract
    s3.upload_file(local_file, BUCKET, s3_key)

    response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': BUCKET, 'Name': s3_key}}
    )

    lines = [block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE']
    return {'lines': lines}

def extract_text_from_pdf_text_based(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    return {"lines": all_text.strip().split('\n')}
