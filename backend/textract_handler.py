import os
import boto3
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client('s3')
textract = boto3.client('textract')
BUCKET = os.environ['S3_BUCKET']

def extract_text_from_s3(local_file, s3_key):
    if local_file.lower().endswith('.pdf'):
        return extract_text_from_pdf_text_based(local_file)

    s3.upload_file(local_file, BUCKET, s3_key)

    response = textract.analyze_document(
        Document={'S3Object': {'Bucket': BUCKET, 'Name': s3_key}},
        FeatureTypes=["TABLES", "FORMS"]
    )

    blocks = response['Blocks']
    lines = [block['Text'] for block in blocks if block['BlockType'] == 'LINE']
    tables = extract_tables(blocks)

    return {'lines': lines, 'tables': tables}

def extract_text_from_pdf_text_based(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    return {"lines": all_text.strip().split('\n'), "tables": []}

def extract_tables(blocks):
    tables = []
    block_map = {block["Id"]: block for block in blocks}

    for block in blocks:
        if block["BlockType"] == "TABLE":
            table = []
            rows = {}
            for rel in block.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    for cell_id in rel["Ids"]:
                        cell = block_map[cell_id]
                        if cell["BlockType"] == "CELL":
                            row_idx = cell["RowIndex"]
                            col_idx = cell["ColumnIndex"]
                            text = ""
                            for c_rel in cell.get("Relationships", []):
                                if c_rel["Type"] == "CHILD":
                                    text = " ".join([block_map[t]["Text"] for t in c_rel["Ids"] if block_map[t]["BlockType"] == "WORD"])
                            if row_idx not in rows:
                                rows[row_idx] = {}
                            rows[row_idx][col_idx] = text
            for i in sorted(rows):
                row = [rows[i].get(j, "") for j in sorted(rows[i])]
                table.append(row)
            tables.append(table)
    return tables
