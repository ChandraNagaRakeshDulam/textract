import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()
bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION"))

def answer_question(question, context, tables=None):
    tables_section = f"Here are some relevant tables:\n{json.dumps(tables, indent=2)}" if tables else ""
    
    prompt = (
        "Human: Use the extracted document content to answer the user's question.\n\n"
        "Context:\n"
        "---------\n"
        f"{context}\n"
        "---------\n\n"
        f"{tables_section}\n\n"
        "If the answer involves tabular data such as fund fees, returns, allocations, or performance figures, respond using this **strict Markdown table format only**:\n\n"
        "| Column 1 | Column 2 |\n"
        "|----------|----------|\n"
        "| Row 1    | Value    |\n"
        "| Row 2    | Value    |\n\n"
        "💡 Do not include extra vertical bars (|). Do not wrap the table in code blocks or quotes. Start and end the table cleanly.\n\n"
        f"Question: {question}\n"
        "Assistant:"
    )

    body = {
        "prompt": prompt,
        "max_tokens_to_sample": 1000,
        "temperature": 0.3,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman:"]
    }

    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",  # or Claude 3 Sonnet if you're using that
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())
    return response_body.get("completion", "No answer found.")
